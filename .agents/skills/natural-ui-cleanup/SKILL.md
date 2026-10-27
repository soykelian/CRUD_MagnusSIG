---
name: natural-ui-cleanup
description: Remove generic or AI-generated visual patterns from an existing website while preserving its brand, content, functionality, routes, and information architecture. Use for focused frontend cleanup and polish, not for a full redesign.
metadata:
  short-description: Refine generic-looking interfaces
---

# Natural UI Cleanup

Make an existing interface feel intentional, restrained, and specific to its product. Do not redesign the whole website unless the requested cleanup cannot be done within its current structure.

## Preserve first

- Brand identity, content, routes, information architecture, and working behavior.
- Business rules and existing responsive behavior.
- The current font unless there is a clear, task-related reason to change it.

## Remove generic visual patterns

Inspect the interface for elements that appear decorative or template-generated without serving a product purpose:

- Sparkles, magic wands, robots, generic assistant bubbles, and "AI" or "Powered by AI" labels.
- Random blobs, neural-network motifs, excessive gradients, glows, glass effects, or floating decorations.
- Repetitive icon-title-description cards, unnecessary badges, emojis, placeholder illustrations, and generic dashboard widgets.
- Excessive rounded cards and pill-shaped controls where simpler sections, rows, or buttons would communicate better.

Ask whether each element would still belong if the product had been designed without AI. Remove or simplify elements that exist only as decoration. Do not replace them with another generic AI-looking element.

## Keep the design authored

- Keep elements that communicate useful information, clarify an action, reinforce the brand, or improve navigation.
- Prefer familiar controls, clear typography, intentional spacing, simple borders, and subtle shadows.
- Use color for brand, hierarchy, action, status, and emphasis. Preserve the existing palette; do not add arbitrary neon or blue-purple gradients.
- Maintain a clear type hierarchy: page heading, section heading, component title, body, then quiet metadata.
- Create a useful spacing rhythm. Group related information and give primary content more room than secondary details.
- Use one coherent icon family. Remove decorative icons and unused imports; do not mix libraries without a deliberate existing reason.
- Convert unnecessary cards to a section, row, list item, or text block when containment does not help comprehension.

Do not make the interface bland. Retain distinctive, functional design choices that a designer could have made intentionally.

## Scope and implementation

- Make focused changes to the existing frontend and component structure.
- Preserve forms, buttons, navigation, validation, permissions, and business logic.
- Remove only code made unused by the cleanup, such as dead classes, animations, icon imports, or components.
- Remove dependencies only when they are clearly unused and safe to remove.
- Avoid rewriting working business logic or expanding the requested scope.

## Responsive and accessibility review

When implementing cleanup, inspect representative desktop and mobile layouts, including narrow widths around 320-390px, tablet around 768px, and desktop around 1024px and wider. Check that navigation, forms, buttons, focus states, readable contrast, and overflow remain usable. Adjust the exact viewport set to the project's existing breakpoints when appropriate.

## Visual verification

Before finishing a frontend cleanup:

1. Run the application using the project's documented development workflow.
2. Inspect the affected pages at desktop and mobile sizes.
3. Check for overflow, broken controls, and contrast or focus regressions.
4. Search the affected frontend for leftover AI labels, assistant-themed decorations, sparkle/wand/robot icons, and unused imports or styles. Treat search matches as leads to inspect, not automatic deletion targets.
5. Summarize the visible changes and the verification performed.

Do not claim a full-site audit if only a subset of pages was reviewed. Avoid adding or running automated tests unless the user asks for tests or the repository's applicable instructions require them.

## Final review question

Could a professional designer have intentionally made this interface this way? Keep purposeful, brand-specific elements; remove or simplify elements that look algorithmically generated without a product reason.
