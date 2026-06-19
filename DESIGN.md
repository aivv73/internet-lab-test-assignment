<!-- SEED: re-run $impeccable document once there's code to capture the actual tokens and components. -->
---
name: InternetLab Developer Landing API
description: A quietly confident developer landing experience that proves backend thinking through a working AI-integrated API.
---

# Design System: InternetLab Developer Landing API

## 1. Overview

**Creative North Star: "The Conservatory Field Notebook"**

This design system should feel like a precise technical field notebook written inside a dim conservatory: systematic, observant, and quietly confident. It is a brand surface for a junior backend developer who wants to prove production-adjacent judgment, not perform visual hype. The landing page should make implementation details feel understandable, tactile, and reviewable.

The aesthetic direction is committed but not loud. A deep moss-green anchor carries identity across the hero, calls to action, and selected proof moments, while neutral surfaces keep documentation, API examples, and form states easy to scan. Motion should be responsive rather than theatrical: the interface acknowledges actions, transitions cleanly, and respects reduced-motion users.

The system explicitly rejects the typical AI-generated SaaS landing page: generic heroes, repeated identical cards, gradient text, vague automation promises, and decorative AI sparkle. Visual decisions should help reviewers understand backend architecture, failure handling, and reliability.

**Key Characteristics:**

- Deep technical calm, not hacker darkness.
- Evidence-first hierarchy: API behavior, lifecycle, tests, and fallback states are visually easy to find.
- Committed moss-green identity balanced by high-readability neutral surfaces.
- Responsive motion for feedback and orientation, never choreography for its own sake.
- Practical polish that supports the backend story.

## 2. Colors

The palette is anchored by a deep moss-green direction and will be resolved in OKLCH during implementation.

### Primary

- **Conservatory Moss** (`oklch(0.350 0.110 140.0)` seed; final implementation token to be resolved): The primary brand anchor. Use for hero emphasis, primary CTAs, active states, lifecycle highlights, and small proof accents. It should feel botanical and technical, not “forest green on cream.”

### Secondary

- **Technical Amber** (`[to be resolved during implementation]`): A restrained secondary accent for warnings, queued states, and outbox/fallback explanations. It should read as instrument-panel clarity, not decorative warmth.

### Neutral

- **Pure White / Near-White Workspace** (`[to be resolved during implementation]`): Default reading surface for documentation-heavy content, forms, API examples, and README-like explanations.
- **Ink Green-Black** (`[to be resolved during implementation]`): Primary text color. Must reach strong contrast against the background and carry a slight relationship to the moss anchor.
- **Muted Ink** (`[to be resolved during implementation]`): Secondary text. Must remain readable; do not use pale gray for elegance.
- **Rule Line** (`[to be resolved during implementation]`): Subtle dividers for structured technical sections and API contract blocks.

### Named Rules

**The Committed Moss Rule.** Moss green must carry identity in key surfaces and moments, but it must not become generic forest-on-cream. The background should stay clean and readable; brand warmth comes from the primary and accent roles, not beige page wash.

**The No Gradient Text Rule.** Emphasis comes from hierarchy, weight, color blocks, and proof content. Gradient text is prohibited.

## 3. Typography

**Display Font:** `[technical-humanist sans to be chosen at implementation]`  
**Body Font:** `[technical-humanist sans to be chosen at implementation]`  
**Label/Mono Font:** Optional; use only for code/API snippets, not as a lazy “developer” costume.

**Character:** The typography should feel systematic, precise, and readable under review pressure. A single well-chosen technical-humanist sans family is preferred over a decorative display/body pairing. If a mono is introduced, it must be functional for code samples and metrics only.

### Hierarchy

- **Display** (`[to be resolved]`, fluid clamp, tight but not cramped): Hero statements and one or two major proof claims. Letter-spacing must not go tighter than `-0.04em`.
- **Headline** (`[to be resolved]`): Section-level claims such as “Full backend lifecycle” or “Graceful failure by design.”
- **Title** (`[to be resolved]`): API endpoint names, architecture blocks, form panels, and test/result summaries.
- **Body** (`[to be resolved]`): Explanatory prose. Keep line length around `65–75ch` and preserve comfortable line-height.
- **Label** (`[to be resolved]`): Short technical metadata, endpoint methods, status codes, and state tags. Avoid repeating tiny uppercase labels above every section.

### Named Rules

**The Review-Speed Rule.** Typography must help a reviewer skim: stack, endpoint, fallback, and test result should be identifiable within seconds.

**The No Terminal Costume Rule.** Monospace is for API/code content only. Do not make the whole brand look like a hacker terminal.

## 4. Elevation

This system is flat by default and layered through tone, spacing, and crisp rules. Shadows should be rare and stateful: a focused form, an active button, or an elevated interactive panel may lift slightly, but static content should not float as ghost cards.

### Named Rules

**The Flat Evidence Rule.** Proof content should feel placed, not decorated. Prefer structured panels, ruled groups, and clear spacing over soft decorative shadows.

**The No Ghost Card Rule.** Do not combine `1px` borders with wide soft shadows as decoration. Pick structure or lift, not both.

## 5. Components

### Buttons

- **Shape:** Confident, moderately rounded controls (`8–12px`, final token to be resolved). Avoid over-rounded card-like buttons.
- **Primary:** Filled Conservatory Moss with near-white text. Use for “Send message,” “View API docs,” or “Open GitHub.”
- **Hover / Focus:** Subtle lift or tonal shift, strong `:focus-visible` ring, no glow-heavy effects.
- **Secondary / Ghost:** Clear border or text-only treatment for lower-priority actions; never low-contrast gray.

### Chips

- **Style:** Compact status tags for `202 Accepted`, `queued`, `fallback_used`, `rate-limited`, and AI categories.
- **State:** Status colors must be semantic and accessible. Amber may signal queued/fallback; moss may signal accepted/sent.

### Cards / Containers

- **Corner Style:** Restrained corners (`12–16px` maximum for content panels).
- **Background:** Neutral reading surfaces with deliberate moss/amber accents where they clarify state.
- **Shadow Strategy:** Flat at rest. Use border or tonal contrast before shadow.
- **Internal Padding:** Generous enough for technical readability; avoid dense dashboard compression on the landing surface.

### Inputs / Fields

- **Style:** Clean, labeled fields with visible boundaries and generous hit targets.
- **Focus:** Moss focus ring or border shift with WCAG AA contrast.
- **Error / Disabled:** Error text must be explicit and readable; disabled states must not drop below accessible contrast.

### Navigation

- **Style:** Minimal top navigation with direct reviewer paths: API docs, GitHub, architecture, contact/demo form.
- **Mobile:** Collapse without hiding primary proof paths. The contact/API flow must remain easy to reach.

## 6. Do's and Don'ts

### Do:

- **Do** make the backend lifecycle visually explicit: validation, rate limiting, AI analysis, persistence, email fallback, response.
- **Do** use the committed moss-green identity for key proof moments and primary actions.
- **Do** keep body text high contrast and readable; muted text must still pass practical readability checks.
- **Do** show concrete API/status language such as `POST /api/contact`, `202 Accepted`, `429`, `queued`, and `fallback_used`.
- **Do** include reduced-motion alternatives for every animation.

### Don't:

- **Don't** create a typical AI-generated SaaS landing page with generic heroes, repeated identical cards, gradient text, and vague automation promises.
- **Don't** use gradient text. It is prohibited.
- **Don't** use a dark hacker/terminal cliché as shorthand for technical skill.
- **Don't** overstate the candidate as a senior enterprise consultant; the confidence should come from evidence and craft.
- **Don't** use identical card grids as the main content grammar. Vary rhythm and structure around the backend story.
- **Don't** use repeated tiny uppercase tracked labels above every section heading.
- **Don't** use wide side-stripe borders as accents on cards or callouts.
