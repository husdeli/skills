---
name: react-animations
description: Rules for animating a React interface — CSS and the UI library's own transitions first, the platform next, and a proven animation library (Motion) only for what they cannot do. INVOKE THIS SKILL before you add or change a transition, a keyframe animation, an enter or exit effect, a layout animation, a gesture, or a scroll effect in a React project, and before you plan or review one. Enforces the lowest rung that meets the requirement, a named reason before Motion, no hand-rolled animation code (no requestAnimationFrame loop, JavaScript tween, setTimeout chain, or effect that toggles a class), one animation library per project, transform and opacity only, reduced motion respected, and timing from theme tokens. Builds on the `react-clean` skill — load that one too.
---

# React animations

How a React component animates. Every rule in **`react-clean`** still applies to the component
that animates — these rules are the animation layer on top of it.

An animation climbs a ladder and stops at the first rung that meets the requirement. Each rung
up costs more bundle, more code, and more to review, so a higher rung needs a reason the lower
ones cannot meet.

## The ladder

| Rung | Use | It covers |
| --- | --- | --- |
| 1. CSS | A `transition` or `@keyframes`, written as Tailwind utilities (`transition-*`, `duration-*`, `ease-*`, `animate-*`) and switched by a class or a `data-*` attribute that follows state | Hover, focus, and press feedback; a color, opacity, or transform change on state; a spinner, pulse, or skeleton shimmer; an enter effect through `@starting-style` (Tailwind's `starting:` variant); a staggered list through a `--index` custom property in `transition-delay` |
| 2. The UI library | The component library's own motion: Mantine's `transitionProps` on `Modal`, `Drawer`, `Menu`, `Popover`, `Tooltip`, and the rest; `Transition` for mount and unmount; `Collapse` for height | Every overlay, menu, and dropdown the library ships; showing and hiding an element with an exit effect; expanding and collapsing a section |
| 3. The platform | The View Transitions API — through the router's own option (TanStack Router's `viewTransition` on `Link`, `navigate`, or the router's `defaultViewTransition`) — and CSS scroll-driven animations (`animation-timeline: view()` or `scroll()`) | A route change that cross-fades or morphs; a shared element that moves between two views; a reveal or progress bar tied to scroll, where the browsers the product supports have it or the page works without it |
| 4. Motion | The `motion` package, imported from `motion/react` | What rungs 1–3 cannot do — see below |

Rungs 1 and 2 are the default for almost every interface. Rung 2 sits beside rung 1, not above
it: when the library ships the animated component, use the library's animation and tune it
through its props (`transition`, `duration`, `timingFunction`) before you write any CSS for it.

## When Motion is the answer

Reach for Motion only when the requirement needs one of these, and name it in the plan or the
pull request:

- **An exit animation the library cannot run** — an element of a dynamic list leaving while the
  others close the gap (`AnimatePresence` with `layout`).
- **A layout animation** — an element animating between two sizes or positions that the layout
  computes, where a view transition does not fit (inside one view, interrupted often, or many
  elements at once).
- **Gestures with physics** — drag, swipe to dismiss, a pinch, or a release that carries
  velocity into a spring.
- **An interruptible spring** — a value that retargets mid-flight without jumping, such as a
  panel that follows a pointer.
- **Orchestration** — a sequence of several elements whose timing depends on each other or on
  data, beyond a fixed stagger.
- **A scroll-linked value the platform cannot give** — the browsers the product supports lack
  scroll-driven animations and the effect is part of the product, not decoration.

"Motion would be shorter" is not on the list. A Tailwind class that does the job is shorter still.

## Rules for every animation

- **No hand-rolled animation code.** No `requestAnimationFrame` loop, no JavaScript tween, no
  `setTimeout` chain to step through classes, and no `useEffect` that toggles a class after a
  render (`react-clean` Rule 4). If a rung cannot do it, the next rung up can. Drawing on a
  `<canvas>` or in WebGL is rendering, not UI animation, and is out of scope here.
- **One animation library.** Motion is the default (`web-stack`). A project that already ships
  another — GSAP, React Spring, `framer-motion` — keeps it, and Motion is not added beside it.
- **Animate `transform` and `opacity`.** These run on the compositor. Animating `width`,
  `height`, `top`, `left`, or `margin` re-runs layout on every frame; use `Collapse`, a
  `grid-template-rows` transition, or Motion's `layout` instead.
- **Respect reduced motion.** Set `respectReducedMotion` on `MantineProvider`. Write the CSS rung
  with `motion-safe:` (or `motion-reduce:` to turn it off), and wrap Motion in
  `<MotionConfig reducedMotion="user">` at the root. A reduced-motion user still sees the end
  state, without the movement.
- **Timing comes from tokens.** Durations and easings are named once — the Tailwind theme or the
  Mantine theme — and every animation picks one. A bare `duration-[437ms]` is a token that was
  never named.
- **Animation never carries meaning alone.** The state an animation shows is also visible when
  it does not run: under reduced motion, in a test, and before the JavaScript loads.

## Motion, when it is used

- **Import from `motion/react`.** `framer-motion` is the same library under its old name; a project
  on it keeps it until a migration is asked for.
- **Load features lazily.** Render `m.*` components inside `LazyMotion` with `domAnimation`
  (or `domMax` for drag and layout) rather than `motion.*`, so a page pays only for what it uses.
- **Keep it inside the component that animates.** Animation values and variants live in that
  component's file or a small hook beside it (`useSwipeToDismiss.ts`), never in a container, a
  service, or the domain.
- **Variants over inline objects** once a component has more than one animated state, so the
  states read as a list of names.

```tsx
// ❌ Avoid — a JavaScript-driven fade that CSS does for free
function Toast({ open }: ToastProps) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setVisible(open));
    return () => cancelAnimationFrame(id);
  }, [open]);
  return <div style={{ opacity: visible ? 1 : 0, transition: 'opacity 200ms' }} />;
}

// ✅ Good — rung 2: the library mounts, animates, and unmounts it
function Toast({ open, children }: ToastProps) {
  return (
    <Transition mounted={open} transition="fade-up" duration={200}>
      {(styles) => <div style={styles}>{children}</div>}
    </Transition>
  );
}

// ✅ Good — rung 4, because a dismissed item leaves and the rest close the gap
function NotificationList({ items }: NotificationListProps) {
  return (
    <AnimatePresence initial={false}>
      {items.map((item) => (
        <m.li key={item.id} layout exit={{ opacity: 0, x: 48 }}>
          <NotificationCard notification={item} />
        </m.li>
      ))}
    </AnimatePresence>
  );
}
```

## Checklist before finishing an animation

- [ ] The animation sits on the lowest rung that meets it, and a Motion animation names its reason
      from the list above.
- [ ] No `requestAnimationFrame` loop, JavaScript tween, `setTimeout` chain, or class-toggling effect.
- [ ] No second animation library next to the project's own.
- [ ] Only `transform` and `opacity` animate, or a height change goes through `Collapse`, a
      `grid-template-rows` transition, or `layout`.
- [ ] Reduced motion is respected, and the end state shows without the animation.
- [ ] Duration and easing come from a theme token.
