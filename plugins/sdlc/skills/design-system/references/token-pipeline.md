# The token pipeline

How the optional design-tokens layer (`web-stack` Rule 2) stores tokens and builds every
platform's theme from them. Read it before you write a token file, the Style Dictionary config,
or a generated output's consumer. Without the layer, the Mantine theme is the token source and
none of this applies.

## One source, in DTCG JSON

- **`tokens/` at the work root holds the source.** When several repositories share the tokens —
  a web app and a native app, or two web apps — the source moves to one package that publishes
  the generated outputs, and each repository depends on that package instead of copying it.
- **Write the W3C Design Tokens (DTCG) format.** Each token is an object with `$value` and
  `$type`. Every semantic and component token also has a `$description` saying when to use it —
  the description is what an agent picks the token by. Set `$type` once
  on a group when every token in it shares the type. An alias is a reference in braces —
  `"$value": "{color.blue.600}"` — never a copied value. Write values in the shape the installed
  Style Dictionary release parses, and read its docs for that release.
- **Use the DTCG types.** `color`, `dimension`, `fontFamily`, `fontWeight`, `number`, `duration`,
  and `cubicBezier` for single values; `shadow`, `typography`, `border`, and `transition` for
  composites. A value that fits a type gets that type, not a bare string.
- **Split the source by tier and category**: `tokens/primitive/color.json`,
  `tokens/semantic/color.light.json`, `tokens/semantic/color.dark.json`,
  `tokens/semantic/space.json`, and `tokens/component/button.json` when the project has component
  tokens.
- **Each tier aliases only the tier below it.** A semantic token's `$value` is a reference to a
  primitive, a component token's is a reference to a semantic token, and only a primitive holds a
  literal value.
- **A design tool exports into the repository.** Variables from Figma or Tokens Studio land as a
  change to `tokens/` that goes through review like any other change. The JSON in the repository
  is the source of truth; the design file is where a change is proposed.

```jsonc
// tokens/primitive/color.json — what values exist
{
  "color": {
    "$type": "color",
    "blue": { "600": { "$value": "#1c7ed6" } },
    "gray": { "50": { "$value": "#f8f9fa" }, "600": { "$value": "#868e96" } }
  }
}

// tokens/semantic/color.light.json — what each value is for
{
  "color": {
    "$type": "color",
    "bg": {
      "surface": { "$value": "{color.gray.50}", "$description": "The page and card background." }
    },
    "text": {
      "muted": { "$value": "{color.gray.600}", "$description": "Secondary text: captions, helper text, timestamps." }
    },
    "action": {
      "primary": { "$value": "{color.blue.600}", "$description": "The one main action in a view." }
    }
  }
}

// tokens/component/button.json — optional, one component's decision
{
  "button": {
    "primary": {
      "bg": { "$type": "color", "$value": "{color.action.primary}", "$description": "The primary button's fill." }
    }
  }
}
```

The JSON files hold no comments; the labels above only name each file. The dark file defines the
same semantic names pointing at other primitives, and a second brand is one more semantic set.
Neither touches a primitive file or a component.

## Every output is generated, and none is edited

Style Dictionary builds the outputs from one config at the work root
(`style-dictionary.config.mjs`), run by a `tokens` script in `package.json` (`bun run tokens`).

| Output | Built as | Consumed by |
| --- | --- | --- |
| CSS variables | `css/variables` with `outputReferences: true`, so a semantic variable points at its primitive. Light values under `:root`, dark values under `[data-mantine-color-scheme='dark']` | The global stylesheet, imported before Tailwind |
| Tailwind theme | A custom format that writes one `@theme inline` block of **semantic tokens only**, mapping Tailwind's namespaces (`--color-*`, `--radius-*`, `--shadow-*`, `--font-*`, `--text-*`, `--ease-*`) to the CSS variables. It opens with `--color-*: initial;` to drop Tailwind's default palette, so `bg-blue-600` generates no class. A color keeps its full semantic path minus the `color` root: `color.bg.surface` is `--color-bg-surface`, used as `bg-bg-surface` | The global stylesheet, after `@import "tailwindcss"` |
| Mantine theme | A custom format that writes a TypeScript module: the primitive hues as ten-shade tuples (`50` to `900` as shades 0 to 9), role-named colors (`primary`, `danger`, `success`, `neutral`) as `virtualColor` entries pointing at a hue per mode so code writes `color="primary"`, `primaryColor`, `spacing`, `radius`, `fontSizes`, `lineHeights`, `fontFamily`, `headings`, and `shadows`, plus a `cssVariablesResolver` that points Mantine's own variables (`--mantine-color-body`, `--mantine-color-text`, `--mantine-color-dimmed`, `--mantine-color-default-border`) at the semantic tokens | The theme module, which passes them to `createTheme` and adds the `components` defaults |
| Board data | The `json` format, every token with its name, value, type, and description | The design board's token pages ([the board reference](./design-board.md)) |
| iOS | `ios-swift/class.swift` | The iOS app, when the product ships one |
| Android | `compose/object`, or `android/resources` for a view-based app | The Android app, when the product ships one |
| Flutter | `flutter/class.dart` | The Flutter app, when the product ships one |

- **Build only the outputs a consumer exists for.** A web-only product has no native output, and
  a project with no board has no board data.
- **One build per mode.** Build the light set, then build the dark set filtered to the tokens the
  mode changes, written under the dark selector. Two sources that define one token in the same
  build are a collision, not an override.
- **Never edit a generated file.** Change the JSON and run `bun run tokens`. Each generated file
  opens with a header that says so, and Biome ignores the generated folder.
- **Commit the outputs**, so the app builds and type-checks without the token step and a review
  shows a token change next to its effect. A `tokens:check` script rebuilds and fails on any
  difference, so a hand edit or a stale build cannot merge.
