export const meta = {
  name: 'orchestrate-core',
  description: 'Deterministic plan → review → revise → implement → verify pipeline for one approved roadmap task',
  whenToUse:
    'Invoked by the /orchestrate command after the interactive stages (task selection, approval, and the interview decisions) are settled. Drives a single task through planning, gated review with at most one revision cycle, implementation, and verification — all as code-controlled flow, no model-driven orchestration.',
  phases: [
    { title: 'Plan', detail: 'implementation-planner produces plan + context pack + risk profile', model: 'opus' },
    { title: 'Review', detail: 'risk-scaled plan-reviewer gate (parallel lenses when high-risk) + at most one revision cycle', model: 'opus' },
    { title: 'Implement', detail: 'coding agent applies the approved plan', model: 'opus' },
    { title: 'Verify', detail: 'verify agent runs commands concurrently (sonnet); fix loop on opus', model: 'sonnet' },
  ],
}

// ---------------------------------------------------------------------------
// Inputs (from the /orchestrate main loop, passed verbatim as `args`)
//   args.task      = { id, title, description, acceptanceCriteria: string[], roadmapContext }
//   args.interview = { discoveryBrief, decisions } | null   (null when the interview gate skipped it)
// ---------------------------------------------------------------------------
// `args` may arrive already-parsed (object) or string-typed (JSON) depending on
// how the caller passes it — normalize before reading fields off it.
let _args = args
if (typeof _args === 'string') {
  try {
    _args = JSON.parse(_args)
  } catch {
    _args = null
  }
}
const task = (_args && _args.task) || {}
const interview = (_args && _args.interview) || null
const MAX_REVISION_CYCLES = 1
const MAX_FIX_CYCLES = 1

const acceptance = Array.isArray(task.acceptanceCriteria)
  ? task.acceptanceCriteria.map((c, i) => `${i + 1}. ${c}`).join('\n')
  : String(task.acceptanceCriteria || 'none stated')

const interviewBlock = interview
  ? `## Discovery Brief (from the interview stage)\n${interview.discoveryBrief || '(none)'}\n\n## Settled Decisions (treat as fixed constraints — do not reopen)\n${interview.decisions || '(none)'}`
  : 'No interview stage ran for this task (skipped by the complexity gate). Plan from the task description and acceptance criteria alone.'

const taskBlock = `## Task ${task.id ? `[${task.id}]` : ''}: ${task.title || '(untitled)'}
${task.description || ''}

## Acceptance criteria
${acceptance}

## Roadmap context
${task.roadmapContext || '(none)'}`

// ---------------------------------------------------------------------------
// Schemas — every stage returns structured output so control flow stays in JS
// ---------------------------------------------------------------------------
const CONTEXT_PACK_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['relevantFiles', 'keySymbols', 'conventions', 'verificationCommands'],
  properties: {
    relevantFiles: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['path', 'role'],
        properties: { path: { type: 'string' }, role: { type: 'string' } },
      },
    },
    keySymbols: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['symbol', 'location'],
        properties: { symbol: { type: 'string' }, location: { type: 'string' } },
      },
    },
    conventions: { type: 'array', items: { type: 'string' } },
    verificationCommands: { type: 'array', items: { type: 'string' } },
  },
}

const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['plan', 'contextPack', 'riskProfile'],
  properties: {
    plan: { type: 'string', description: 'The full Implementation Plan in the planner output format' },
    contextPack: CONTEXT_PACK_SCHEMA,
    riskProfile: {
      type: 'object',
      additionalProperties: false,
      required: ['filesTouched', 'addsDependency', 'addsPublicApi', 'criteriaAutoCheckable'],
      properties: {
        filesTouched: { type: 'integer' },
        addsDependency: { type: 'boolean' },
        addsPublicApi: { type: 'boolean' },
        criteriaAutoCheckable: {
          type: 'boolean',
          description: 'True if every acceptance criterion can be checked directly by the verification suite',
        },
      },
    },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['verdict', 'summary', 'issues'],
  properties: {
    verdict: { type: 'string', enum: ['APPROVED', 'CHANGES_REQUESTED'] },
    summary: { type: 'string' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['title', 'severity', 'problem', 'suggestion'],
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
          steps: { type: 'string' },
          problem: { type: 'string' },
          suggestion: { type: 'string' },
        },
      },
    },
  },
}

const IMPL_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['summary', 'stepsCompleted', 'filesChanged', 'blockers'],
  properties: {
    summary: { type: 'string' },
    stepsCompleted: { type: 'array', items: { type: 'string' } },
    filesChanged: {
      type: 'object',
      additionalProperties: false,
      required: ['created', 'modified'],
      properties: {
        created: { type: 'array', items: { type: 'string' } },
        modified: { type: 'array', items: { type: 'string' } },
      },
    },
    blockers: { type: 'array', items: { type: 'string' } },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['passed', 'results', 'failures'],
  properties: {
    passed: { type: 'boolean' },
    results: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['command', 'passed'],
        properties: {
          command: { type: 'string' },
          passed: { type: 'boolean' },
          output: { type: 'string' },
        },
      },
    },
    failures: { type: 'array', items: { type: 'string' } },
  },
}

function packToText(pack) {
  const lines = ['## Context Pack']
  lines.push('### Relevant files')
  for (const f of pack.relevantFiles || []) lines.push(`- ${f.path} — ${f.role}`)
  lines.push('### Key symbols')
  for (const s of pack.keySymbols || []) lines.push(`- ${s.symbol} (${s.location})`)
  lines.push('### Conventions')
  for (const c of pack.conventions || []) lines.push(`- ${c}`)
  lines.push('### Verification commands')
  for (const v of pack.verificationCommands || []) lines.push(`- ${v}`)
  return lines.join('\n')
}

function issuesToText(issues) {
  return (issues || [])
    .map(
      (x, i) =>
        `**Issue ${i + 1}: ${x.title}** (${x.severity})\n- Step(s): ${x.steps || 'n/a'}\n- Problem: ${x.problem}\n- Suggestion: ${x.suggestion}`,
    )
    .join('\n\n')
}

// ===========================================================================
// Stage 1 — Plan
// ===========================================================================
phase('Plan')
const planResult = await agent(
  `You are the implementation-planner for the /orchestrate pipeline. Produce a step-by-step implementation plan AND a context pack AND a risk profile for the task below.

${taskBlock}

${interviewBlock}

Return the plan in your standard Implementation Plan format as the \`plan\` field. Fill \`contextPack\` with the files, symbols, conventions, and the EXACT verification commands (tests, lint, typecheck) for this project. Fill \`riskProfile\` honestly — it drives whether a formal plan review runs.`,
  { phase: 'Plan', agentType: 'clean-architecture:implementation-planner', schema: PLAN_SCHEMA, model: 'opus', effort: 'high', label: 'plan' },
)

if (!planResult) {
  return { status: 'aborted', stage: 'plan', reason: 'planner returned no result' }
}

let plan = planResult.plan
const contextPack = planResult.contextPack
const risk = planResult.riskProfile
const packText = packToText(contextPack)

// ===========================================================================
// Stage 2 — Review (deterministic complexity gate + at most one revision cycle)
// ===========================================================================
// Review lenses. High-risk plans get both, run in PARALLEL (same wall-clock as
// one reviewer); normal-risk plans get a single holistic review.
const REVIEW_LENSES = [
  {
    key: 'correctness',
    focus:
      'Focus on CORRECTNESS and COMPLETENESS: will the plan actually satisfy every acceptance criterion? Look for missing steps, wrong assumptions, unhandled edge cases, and ordering hazards.',
  },
  {
    key: 'conventions',
    focus:
      'Focus on CODEBASE FIT: does the plan follow existing conventions, dependency rules, and architectural boundaries? Flag unjustified new public API surface or dependencies.',
  },
]

// Run the review for the current `plan`. Returns a merged {verdict, summary, issues}
// (CHANGES_REQUESTED if ANY reviewer requests changes), or null if every reviewer died.
async function runReview(highRisk, cycleLabel) {
  const base = `You are the plan-reviewer for the /orchestrate pipeline. Evaluate the plan against the task, acceptance criteria, and context pack. Read the referenced files — do not review from the plan text alone. Return APPROVED or CHANGES_REQUESTED with actionable issues.

${taskBlock}

${interviewBlock}

## Plan under review
${plan}

${packText}`

  if (!highRisk) {
    return await agent(`${base}\n\nReview holistically for correctness, completeness, and convention-alignment.`, {
      phase: 'Review',
      agentType: 'clean-architecture:plan-reviewer',
      schema: REVIEW_SCHEMA,
      model: 'opus',
      label: `review#${cycleLabel}`,
    })
  }

  // parallel() preserves order and yields null for a dead reviewer; tag each
  // result with its lens BEFORE filtering so labels never drift out of alignment.
  const reviews = (
    await parallel(
      REVIEW_LENSES.map((lens) => () =>
        agent(`${base}\n\n${lens.focus}`, {
          phase: 'Review',
          agentType: 'clean-architecture:plan-reviewer',
          schema: REVIEW_SCHEMA,
          model: 'opus',
          label: `review:${lens.key}#${cycleLabel}`,
        }),
      ),
    )
  )
    .map((r, i) => (r ? { ...r, lens: REVIEW_LENSES[i].key } : null))
    .filter(Boolean)

  if (!reviews.length) return null
  return {
    verdict: reviews.some((r) => r.verdict === 'CHANGES_REQUESTED') ? 'CHANGES_REQUESTED' : 'APPROVED',
    summary: reviews.map((r) => `[${r.lens}] ${r.summary}`).join(' | '),
    issues: reviews.flatMap((r) => r.issues || []),
  }
}

phase('Review')
const skipReview =
  risk.filesTouched <= 2 &&
  !risk.addsDependency &&
  !risk.addsPublicApi &&
  risk.criteriaAutoCheckable

const highRisk = risk.addsPublicApi || risk.addsDependency || risk.filesTouched > 5

let reviewSummary = 'skipped by complexity gate (trivial, low-risk plan)'
let approved = true

if (skipReview) {
  log(`Review gate: SKIPPED — ${risk.filesTouched} file(s), no new deps/API, criteria auto-checkable.`)
} else {
  log(
    `Review gate: REQUIRED — ${risk.filesTouched} file(s), deps=${risk.addsDependency}, api=${risk.addsPublicApi}. Mode: ${highRisk ? 'parallel lenses (high-risk)' : 'single holistic'}.`,
  )
  approved = false
  for (let cycle = 0; cycle <= MAX_REVISION_CYCLES && !approved; cycle++) {
    const review = await runReview(highRisk, cycle + 1)

    if (!review) return { status: 'aborted', stage: 'review', reason: 'reviewer returned no result' }
    reviewSummary = review.summary

    if (review.verdict === 'APPROVED') {
      approved = true
      break
    }

    // CHANGES REQUESTED — revise once, then loop re-reviews.
    if (cycle < MAX_REVISION_CYCLES) {
      log(`Review cycle ${cycle + 1}: CHANGES REQUESTED — revising plan.`)
      const revised = await agent(
        `You are the implementation-planner. Revise your prior plan to resolve every issue the reviewer raised. Note in the Context section how each issue was addressed. Return the full updated plan, context pack, and risk profile.

${taskBlock}

${interviewBlock}

## Previous plan
${plan}

${packText}

## Review issues to resolve
${issuesToText(review.issues)}`,
        { phase: 'Review', agentType: 'clean-architecture:implementation-planner', schema: PLAN_SCHEMA, model: 'opus', label: `revise#${cycle + 1}` },
      )
      if (!revised) return { status: 'aborted', stage: 'revision', reason: 'revision returned no result' }
      plan = revised.plan
    } else {
      // Exhausted the single allowed revision and still not approved → escalate.
      return {
        status: 'escalate',
        stage: 'review',
        reason: 'plan still not APPROVED after one revision cycle',
        plan,
        reviewSummary,
        issues: review.issues,
      }
    }
  }
}

// ===========================================================================
// Stage 3 & 4 — Implement, then Verify (fix-and-recheck loop)
// ===========================================================================
phase('Implement')
let impl = await agent(
  `You are the coding agent for the /orchestrate pipeline. Implement the approved plan exactly — no scope creep, no extra work. Follow the react-clean skill for any React file. Match the conventions in the context pack.

## Approved plan
${plan}

${packText}

## Acceptance criteria
${acceptance}`,
  { phase: 'Implement', agentType: 'clean-architecture:coding', schema: IMPL_SCHEMA, model: 'opus', label: 'implement' },
)

if (!impl) return { status: 'aborted', stage: 'implement', reason: 'coding agent returned no result' }
if (impl.blockers && impl.blockers.length) {
  return { status: 'escalate', stage: 'implement', reason: 'coding reported blockers', blockers: impl.blockers, plan }
}

phase('Verify')
const verifyCommands = (contextPack.verificationCommands || []).join('\n') || '(none recorded — discover them)'
let verify = null
let fixCycle = 0

for (; fixCycle <= MAX_FIX_CYCLES; fixCycle++) {
  verify = await agent(
    `You are the verification agent for the /orchestrate pipeline. Run the project's verification commands CONCURRENTLY (issue them as parallel Bash commands in one batch), then report pass/fail per command.

## Verification commands
${verifyCommands}

${interviewBlock}

## How to judge pass/fail
- Judge by whether THIS change introduced failures — not by absolute exit codes.
- A command that exits non-zero ONLY because of a known pre-existing baseline (e.g. \`tsc -b\` in a repo that already has type errors, when CI gates on build + tests rather than typecheck) is a PASS as long as the failure count is at or below the baseline. Compare against the repo's existing state before blaming the change.
- Only gate \`passed\` on the project's actual gating commands (build, tests, lint, config validation) as reflected in the settled decisions / acceptance criteria above.

## Output hygiene (important — keeps this within the retry budget)
- Cap each result's \`output\` to ~3 short lines. Never paste full compiler or test dumps.
- Summarize failures as concise one-line descriptions in \`failures\`.
- Make exactly ONE StructuredOutput call.

Set \`passed\` = true when every gating command succeeds (baseline-adjusted per above). List concrete \`failures\` otherwise.`,
    { phase: 'Verify', agentType: 'clean-architecture:verify', schema: VERIFY_SCHEMA, model: 'sonnet', effort: 'low', label: `verify#${fixCycle + 1}` },
  )

  if (!verify) return { status: 'aborted', stage: 'verify', reason: 'verify agent returned no result', plan }
  if (verify.passed) break

  if (fixCycle < MAX_FIX_CYCLES) {
    log(`Verify cycle ${fixCycle + 1}: FAILED — sending failures back to coding.`)
    impl = await agent(
      `You are the coding agent. Verification failed. Fix ONLY what is needed to make the checks pass — stay within the approved plan. Then stop; verification will re-run.

## Approved plan
${plan}

${packText}

## Verification failures to fix
${(verify.failures || []).map((f) => `- ${f}`).join('\n')}`,
      { phase: 'Verify', agentType: 'clean-architecture:coding', schema: IMPL_SCHEMA, model: 'opus', label: `fix#${fixCycle + 1}` },
    )
    if (!impl) return { status: 'aborted', stage: 'fix', reason: 'fix agent returned no result', plan }
  }
}

if (!verify.passed) {
  return {
    status: 'escalate',
    stage: 'verify',
    reason: `verification still failing after ${MAX_FIX_CYCLES} fix cycle(s)`,
    failures: verify.failures,
    plan,
  }
}

// ===========================================================================
// Success — main loop marks ticket + roadmap Completed and reports.
// ===========================================================================
return {
  status: 'completed',
  task: { id: task.id, title: task.title },
  interviewRan: !!interview,
  reviewRan: !skipReview,
  reviewSummary,
  plan,
  implementation: impl,
  verification: verify,
}
