# The design board

How the design board is set up: a Storybook that shows the whole design system — the catalog,
every token, and every shared component in every state — on its own server and its own URL,
apart from the app. Read it before you set up the board, add a page to it, or write a story.

The board is the optional `board` layer of `web-stack`. `/stack install` installs it, and
`/design-system board` generates or refreshes it.

## Packages and scripts

- **Dev dependencies**: `storybook`, `@storybook/react-vite`, `@storybook/addon-docs`, and
  `@storybook/addon-a11y`. Use the current stable release, all on one version, and read its docs.
- **Scripts in `package.json`**: `board` runs `storybook dev -p 6006`, and `board:build` runs
  `storybook build -o storybook-static`. `storybook-static/` is ignored by git.
- **`board:build` is a check command** (`web-stack` Rule 6). A story that no longer renders fails
  the change, like a type error.

## Where the files live

| File | Holds |
| --- | --- |
| `.storybook/main.ts` | The framework (`@storybook/react-vite`), the addons, the story globs, and `viteFinal` |
| `.storybook/preview.tsx` | The global stylesheet import, the theme decorator, and the color-scheme toolbar |
| `.storybook/pages/Introduction.mdx` | The catalog, rendered from `design-system.md` |
| `.storybook/pages/tokens/*.mdx` | One page per token category: color, type, spacing, radius, shadow, motion |
| `src/components/<Name>.stories.tsx` | The stories of one shared component, beside the component |

The board's own files stay under `.storybook/`, and nothing in the app imports from it. The app
never ships a board route.

## Setup

- **Reuse the app's Vite config, minus the app.** Storybook's Vite builder loads the project's
  `vite.config.*`. In `viteFinal`, remove the TanStack Start plugin so the board builds components
  only, and keep the rest — Tailwind's plugin, path aliases — so the board styles match the app.
- **Story globs** cover the shared components and the board pages:
  `../src/components/**/*.stories.tsx` and `./pages/**/*.mdx`. Feature components under
  `features/` are not on the board.
- **One provider, the app's own.** `preview.tsx` imports the app's global stylesheet — Mantine's
  layered styles, the token variables, and Tailwind, in the app's cascade order — and wraps every
  story in `MantineProvider` with the app's theme. The board never defines a theme of its own.
- **Light and dark on every story.** A toolbar global (`globalTypes`) switches the color scheme,
  and the decorator passes it to `MantineProvider` as `forceColorScheme`.
- **Accessibility runs on every story.** The a11y addon reports contrast and labeling failures in
  the panel; a failure on a shared component is a defect in the component or its tokens.

## Pages

- **Introduction renders the catalog.** Import `design-system.md` as raw text and render it with
  the `Markdown` doc block, so the board and the agents read one file and the board never holds a
  second copy of the catalog.
- **Token pages render the token build, never a hand-typed list.** With the design-tokens layer,
  read the board data the pipeline generates ([the token pipeline](./token-pipeline.md)). Without
  it, read the Mantine theme merged over `DEFAULT_THEME` with `mergeMantineTheme`. Colors render
  with the `ColorPalette` and `ColorItem` doc blocks, type with `Typeset`, and spacing, radius,
  shadow, and motion as one small sample per token, labeled with its semantic name. Import doc
  blocks from the docs package of the installed release (`@storybook/addon-docs/blocks` in
  Storybook 9 and later).
- **Show the semantic tier first.** Each token page leads with the semantic tokens — the ones code
  uses — and shows the primitive scale below them, labeled as the palette they draw from.

## Stories

- **One stories file per shared component**, written in Component Story Format with a typed
  `Meta` and `StoryObj`, titled `Components/<Name>`, and tagged `autodocs` so the board builds its
  docs page from the props type.
- **Cover every variant and every state the component has**: each `variant` and `size`, disabled,
  loading, error, empty, and long or wrapping content — whichever the props allow. A state the
  component has and the board does not show is a gap.
- **Fixture props only.** A shared component is presentational (`clean-fullstack-architecture`),
  so a story passes plain props and needs no router, query client, or network. A story that needs
  one is a sign the component belongs in `containers/`.
- **Name stories for the state they show** — `Disabled`, `WithLongLabel`, `Loading` — never
  `Example1`.
- **A story is not a test.** It shows the component; the test plan decides what is tested
  (`test-strategy`).

```tsx
import type { Meta, StoryObj } from '@storybook/react-vite';
import { StatusBadge } from './StatusBadge';

const meta = {
  title: 'Components/StatusBadge',
  component: StatusBadge,
  tags: ['autodocs'],
  args: { children: 'Published' },
} satisfies Meta<typeof StatusBadge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Success: Story = { args: { status: 'success' } };
export const Danger: Story = { args: { status: 'danger', children: 'Failed' } };
export const WithLongLabel: Story = {
  args: { status: 'neutral', children: 'Waiting for the second reviewer to approve' },
};
```

## Publishing

`bun run board:build` writes a static site to `storybook-static/` that any static host serves.
Where it is hosted, and who can open it, is the project owner's decision: deploying the board
publishes the design system, so never deploy it without the user's go-ahead. Once it has a URL,
the catalog's header links it.
