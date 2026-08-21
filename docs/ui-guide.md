# UI Redesign & Refactoring Specification

## 1. Objective

Refactor the existing frontend UI into a **minimalist, professional academic document workspace** while preserving the product's existing **editorial/academic visual identity**.

The redesign should improve:

* Information hierarchy
* Content density
* Form usability
* Step navigation
* Interaction feedback
* Accessibility
* Responsive behavior
* Visual consistency
* Codebase cleanliness

The goal is **not** to replace the current design with a generic SaaS dashboard.

The existing combination of:

* Parchment/editorial visual language
* Forest-green accent
* Fraunces for prominent/document headings
* Source Serif 4 for long-form academic content

should remain part of the product identity unless there is a clear usability reason to change it.

---

# 2. Non-Goals

Do NOT:

* Change business logic.
* Change API contracts.
* Change backend behavior.
* Change existing data models.
* Rewrite state management unnecessarily.
* Introduce a new UI framework or component library unless one already exists in the project.
* Add unnecessary dependencies.
* Replace the existing application architecture.
* Turn the application into a generic Linear/Notion-style SaaS dashboard.
* Remove the academic/editorial identity.
* Rewrite working components merely for stylistic reasons.
* Change functionality unrelated to the UI redesign.

This is primarily a **UI/UX refactoring task**, not an application rewrite.

---

# 3. Design Principles

Follow these principles throughout the implementation.

## 3.1 Neutral-first, not neutral-only

The UI should become calmer and more professional by reducing visual noise.

Use:

* Neutral backgrounds
* Subtle borders
* Muted semantic colors
* Minimal shadows
* Controlled spacing
* Clear typography hierarchy

However, preserve **forest green as the primary accent color**.

Forest green should be used selectively for:

* Active navigation
* Primary actions
* Focus/selected states
* Important links
* Progress indicators
* Brand accents

Do not use forest green for large surfaces or excessive decoration.

---

## 3.2 Preserve academic/editorial identity

The current typography and visual identity are intentional.

Use:

### UI / Controls

Prefer:

```text
system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

or the existing sans-serif equivalent.

Use this for:

* Buttons
* Inputs
* Selects
* Step navigation
* Metadata
* Badges
* Tables
* Utility labels

### Document / Reading Content

Preserve:

```text
Source Serif 4
```

or the existing serif content font.

Use it for:

* Abstract
* Long-form content
* Research text
* Generated document content
* Reading-oriented sections

### Major document headings

Preserve:

```text
Fraunces
```

where it strengthens the editorial/academic identity.

Use it primarily for:

* Main document title
* Major section headings
* Important editorial headings

Do not use Fraunces for every UI element.

### Technical content

Use:

```text
ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace
```

for:

* Metrics
* JSON
* Code
* Technical identifiers
* Baselines where appropriate

---

# 4. Design Tokens

Refactor the existing CSS variables into a coherent semantic design system.

Do not blindly replace all existing tokens if equivalent tokens already exist. Consolidate them where practical.

## 4.1 Backgrounds

Recommended direction:

```css
--bg-app: #F8F7F2;
--bg-surface: #FFFFFF;
--bg-subtle: #F3F4EF;
```

The application background should retain a very subtle warm/editorial tone rather than becoming a completely cold gray SaaS background.

---

## 4.2 Text

```css
--text-primary: #1F2933;
--text-secondary: #475569;
--text-muted: #94A3B8;
```

Ensure sufficient contrast for primary and secondary text.

Muted text must not be used for essential information.

---

## 4.3 Borders

```css
--border-subtle: #D9DDD6;
--border-focus: <forest-green-focus-color>;
```

Prefer 1px borders over heavy shadows for panels and form controls.

---

## 4.4 Brand / Accent

Preserve the existing forest-green brand color.

Define semantic tokens similar to:

```css
--brand: <existing-forest-green>;
--brand-hover: <darker-forest-green>;
--brand-subtle: <very-light-green>;
```

Do not invent a completely unrelated primary color.

---

## 4.5 Semantic statuses

Use muted semantic badges.

### Neutral

```text
Background: #F1F5F9
Text:       #334155
Border:     #CBD5E1
```

### Warning / Unsupported

```text
Background: #FEF3C7
Text:       #92400E
Border:     #FDE68A
```

### Danger / Major

```text
Background: #FEE2E2
Text:       #991B1B
Border:     #FECACA
```

### Success

```text
Background: #ECFDF5
Text:       #065F46
Border:     #A7F3D0
```

Do not use saturated red/yellow/green surfaces.

Semantic colors should communicate status without dominating the page.

---

# 5. Radius and Elevation

Use restrained corner radii:

```css
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
```

Avoid excessive pill-shaped UI.

Do not use:

```css
border-radius: 999px;
```

for normal cards, fields, buttons, or navigation elements.

Pill shapes may remain appropriate for small status badges where semantically justified.

Prefer:

```css
border: 1px solid var(--border-subtle);
```

over large drop shadows.

Use shadows only when they communicate elevation meaningfully, such as:

* Dropdown menus
* Popovers
* Dialogs
* Floating controls

---

# 6. Form Controls

## 6.1 Remove global textarea height

The current global rule:

```css
textarea {
    min-height: 140px;
}
```

must be removed.

This is currently causing short fields such as:

* baseline
* metric
* contribution text

to occupy excessive vertical space.

---

## 6.2 Short text fields

Short textareas should size according to their content where browser support permits.

Preferred behavior:

```css
field-sizing: content;
min-height: 38px;
```

However, do not allow content-based sizing to create an unbounded page.

Use sensible maximum heights and scrolling where necessary.

---

## 6.3 Long-form textareas

Create an explicit class or semantic variant for long-form fields.

Example:

```css
.doc-textarea-long {
    min-height: 120px;
    max-height: 400px;
    overflow-y: auto;
}
```

Use this only for fields intended for substantial text, such as:

* Abstract
* Methodology
* Contribution
* Long explanations
* Other genuinely multi-line content

Do not apply this class globally.

---

# 7. Focus and Accessibility

Every interactive form control must have a clear keyboard focus state.

Do NOT solve focus styling with:

```css
outline: none;
```

without providing an equivalent accessible focus indicator.

Prefer:

```css
:focus-visible {
    outline: 2px solid var(--brand);
    outline-offset: 2px;
}
```

or an equivalent accessible implementation.

Focus indicators must remain clearly visible against both the application background and surface backgrounds.

---

# 8. Interaction States

Interactive components must have intentional states.

For buttons, controls, navigation items, and selectable elements consider:

```text
Default
Hover
Focus
Active
Selected
Disabled
Loading
Success
Error
```

Hover effects should remain subtle.

Avoid:

* Scale-up animations
* Excessive movement
* Large shadows
* Bouncy effects

Prefer changes to:

* Background
* Border
* Text color
* Opacity
* Small elevation changes

---

# 9. Transitions

Do not use:

```css
transition: all 0.12s ease-in-out;
```

Prefer explicit properties:

```css
transition:
    background-color 120ms ease,
    border-color 120ms ease,
    color 120ms ease,
    box-shadow 120ms ease;
```

Only animate properties that actually need animation.

Respect:

```css
@media (prefers-reduced-motion: reduce)
```

and reduce or disable non-essential transitions for users who request reduced motion.

---

# 10. Document Header

The existing Hero section consumes too much vertical space and repeats on every step.

Replace the large Hero presentation with a compact document/workspace header.

The header should communicate only information that is useful during the workflow.

Possible information:

```text
Document / Project title
Session identifier
Current save state
Current workflow state
Relevant compact actions
```

Target height:

```text
Approximately 50–60px on desktop
```

Do not hardcode the exact height if the content requires more space, but keep the header compact.

Avoid repeating large:

* Titles
* Descriptions
* Session information
* Decorative elements

on every step.

---

# 11. Step Navigation

The existing 12-step pill navigation should become a compact workflow navigation system.

The navigation should clearly communicate:

```text
Current
Completed
Upcoming
Error / Needs attention
```

Example conceptual structure:

```text
01 Overview
02 Baseline
03 Claims
04 Evidence
05 Related Work
...
```

Do not copy this exact visual layout blindly. Adapt it to the existing application structure.

---

# 12. Step Navigation Rules

Navigation behavior must be explicit.

## Completed steps

Completed steps should be clickable.

Users should be able to return to previous steps and review/edit their information.

## Current step

The current step should have the strongest visual emphasis.

## Upcoming steps

Upcoming steps should normally remain non-clickable unless the existing workflow explicitly supports jumping ahead.

## Error / incomplete steps

Steps requiring attention should have a subtle visual indication.

Do not rely only on color to communicate this state.

---

# 13. Unsaved Changes

If navigating away from a step can cause data loss, handle unsaved changes appropriately.

Possible behavior:

```text
No unsaved changes
→ navigate immediately

Unsaved changes
→ preserve state if architecture supports it
OR
→ ask for confirmation before discarding
```

Do not introduce destructive navigation behavior accidentally during the UI refactor.

---

# 14. Responsive Behavior

The redesigned UI must work across:

* Desktop
* Tablet
* Mobile/narrow viewport

## Desktop

Use the full workflow navigation.

Example:

```text
01 Overview   02 Baseline   03 Claims   04 Evidence   ...
```

## Tablet

The navigation may become horizontally scrollable if necessary.

Do not allow the stepper to force the entire page wider than the viewport.

## Mobile

Do not attempt to squeeze all 12 steps into one row.

Use a compact representation such as:

```text
Step 3 of 12
Claims                         ▼
```

or another equivalent selector.

The main content should remain the primary focus.

---

# 15. Content Width and Vertical Density

The redesign should reduce unnecessary whitespace without making the interface cramped.

Prioritize:

```text
Readable content width
Consistent vertical rhythm
Compact metadata
Clear section separation
```

Avoid:

* Giant empty areas
* Excessively tall cards
* Repeated hero sections
* Large decorative spacing
* Full-width content when a readable max-width would be better

Long-form academic text should maintain a comfortable reading width.

---

# 16. Component Consistency

Maintain the existing structural pattern where it remains useful:

```text
Panel
  ↓
Heading
  ↓
Description/content
  ↓
Field/choice/action
```

However, do not force every component into the same visual box.

Use hierarchy appropriately:

* Forms
* Reading content
* Metadata
* Navigation
* Status information
* Actions

should have visually distinct but related treatments.

---

# 17. Button Hierarchy

Establish clear action hierarchy.

### Primary action

Use the forest-green brand color.

Examples:

```text
Continue
Generate
Save
Submit
```

### Secondary action

Use neutral surface/border styling.

Examples:

```text
Back
Cancel
Review
```

### Destructive action

Use muted danger styling.

Do not make every button visually dominant.

---

# 18. Status Badges

The existing semantic collision between:

```text
UNSUPPORTED
MAJOR
```

must remain resolved.

These statuses may both use a muted danger/warning family, but their semantics must remain distinguishable.

Do not rely solely on color.

Where appropriate, use:

* Label
* Icon
* Context
* Distinct styling

to communicate meaning.

---

# 19. Loading / Save States

The workflow should provide clear feedback for asynchronous actions.

Examples:

```text
Saving...
Saved ✓
Unable to save
Generating...
Generated
```

Loading states should not cause major layout shifts.

Buttons performing asynchronous actions should prevent accidental duplicate submissions where appropriate.

---

# 20. Codebase Hygiene

Remove confirmed dead code/assets.

If confirmed unused:

```text
src/App.css
src/assets/hero.png
src/assets/react.svg
```

may be removed.

Replace the default:

```text
/public/vite.svg
```

favicon with a minimal project-specific favicon.

The favicon should visually align with the academic/document identity and forest-green accent.

Do not add unnecessary image assets merely for decoration.

---

# 21. Preserve Existing Functionality

During the refactor:

* Existing form behavior must continue working.
* Existing validation must continue working.
* Existing API calls must continue working.
* Existing generated content must continue working.
* Existing navigation logic must continue working.
* Existing state persistence must continue working.
* Existing keyboard interactions must not regress.

UI refactoring must not introduce business-logic regressions.

---

# 22. Implementation Strategy

Before modifying files:

1. Inspect the existing frontend architecture.
2. Identify all shared UI components.
3. Identify all step components.
4. Identify global CSS rules.
5. Identify existing design tokens.
6. Identify existing navigation/state logic.
7. Identify all form fields and determine whether each is short-form or long-form.
8. Identify responsive behavior currently implemented.
9. Identify unused assets and CSS only after verifying references.

Do not start by blindly rewriting `index.css`.

---

# 23. Recommended Implementation Order

Implement in this order:

### Phase 1 — Design tokens

* Backgrounds
* Text colors
* Borders
* Forest-green brand tokens
* Semantic statuses
* Radius
* Typography

### Phase 2 — Form density

* Remove global 140px textarea height
* Add short/long field variants
* Improve input sizing
* Add focus states

### Phase 3 — Header

* Replace oversized Hero
* Introduce compact document header
* Preserve important metadata

### Phase 4 — Step navigation

* Redesign stepper
* Add completed/current/upcoming states
* Add navigation behavior
* Handle unsaved changes if applicable

### Phase 5 — Interaction

* Hover
* Focus
* Active
* Disabled
* Loading
* Error
* Success states
* Transitions

### Phase 6 — Responsive

* Desktop
* Tablet
* Mobile

### Phase 7 — Cleanup

* Remove dead CSS
* Remove unused assets
* Replace favicon
* Remove unnecessary dependencies if discovered

---

# 24. Visual Direction

The final result should feel like:

```text
Academic
Editorial
Professional
Calm
Focused
Dense but readable
Document-oriented
```

It should NOT feel like:

```text
Generic SaaS dashboard
Marketing landing page
Highly decorative AI application
Glassmorphism UI
Excessively rounded UI
Color-heavy dashboard
```

The existing editorial identity should remain recognizable after the redesign.

---

# 25. Final Acceptance Criteria

The implementation is considered successful when:

### Visual

* [ ] The UI feels significantly cleaner and more professional.
* [ ] Existing academic/editorial identity remains recognizable.
* [ ] Forest green remains a restrained brand accent.
* [ ] Neutral surfaces dominate the interface.
* [ ] Shadows are minimal.
* [ ] Border/radius usage is consistent.
* [ ] Typography has a clear UI/content/technical hierarchy.

### Forms

* [ ] Short textareas no longer occupy 140px unnecessarily.
* [ ] Long-form textareas have appropriate dedicated sizing.
* [ ] Form controls have clear focus-visible states.
* [ ] Form density is improved without becoming cramped.

### Navigation

* [ ] Header no longer consumes excessive vertical space.
* [ ] Step navigation is compact.
* [ ] Completed steps can be reviewed.
* [ ] Current step is visually obvious.
* [ ] Upcoming steps are distinguishable.
* [ ] Navigation does not overflow on narrow screens.

### Interaction

* [ ] Buttons have hover/focus/active/disabled states.
* [ ] Async actions have loading feedback.
* [ ] Save state is communicated.
* [ ] Error/success states are visually clear.
* [ ] Motion is subtle and respects reduced-motion preferences.

### Responsive

* [ ] Desktop layout works correctly.
* [ ] Tablet layout works correctly.
* [ ] Mobile layout does not create horizontal overflow.
* [ ] Step navigation adapts appropriately to narrow screens.
* [ ] Long content does not break the layout.

### Accessibility

* [ ] Keyboard navigation works.
* [ ] `:focus-visible` states are visible.
* [ ] Important information is not communicated through color alone.
* [ ] Text contrast is sufficient.
* [ ] Interactive elements have appropriate semantic behavior.

### Code quality

* [ ] `src/App.css` removed if confirmed unused.
* [ ] Unused assets removed if confirmed unused.
* [ ] Default Vite favicon replaced.
* [ ] No unnecessary dependencies introduced.
* [ ] No unnecessary architecture changes made.

### Regression

* [ ] Existing business logic remains unchanged.
* [ ] Existing API behavior remains unchanged.
* [ ] Existing form behavior remains unchanged.
* [ ] Existing workflow behavior remains unchanged.
* [ ] `npm run build` succeeds.
* [ ] No new build warnings are introduced.
* [ ] No obvious console errors remain.

---

# 26. Final Instruction to the Coding Agent

Before implementation, inspect the existing codebase and compare the current implementation against this specification.

Do not blindly implement every example literally.

Use the specification as a **design and UX contract**, while adapting implementation details to the existing component architecture.

Prioritize:

1. Correct UX behavior
2. Preservation of existing functionality
3. Visual consistency
4. Accessibility
5. Responsive behavior
6. Maintainable implementation

If an existing implementation already satisfies a requirement, do not rewrite it unnecessarily.

If a design decision is ambiguous, prefer the solution that:

* preserves the existing academic/editorial identity,
* reduces visual noise,
* improves information hierarchy,
* improves usability,
* minimizes implementation complexity,
* and avoids unnecessary dependencies.

After implementation, verify the acceptance criteria and report:

* Files changed
* Components changed
* CSS/design-token changes
* Navigation/interaction changes
* Responsive changes
* Removed assets/files
* Build/test result
* Any remaining UX limitations
