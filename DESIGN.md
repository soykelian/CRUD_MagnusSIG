---
name: Magnus SIG
description: Interfaz de inventario clara, sobria y centrada en operaciones reales.
colors:
  primary: "#2e3192"
  primary-strong: "#252875"
  primary-soft: "#eaebf8"
  cyan: "#269dd8"
  orange: "#ff931e"
  ink: "#25284f"
  text: "#343952"
  muted: "#59617a"
  faint: "#68718a"
  line: "#e2e5ef"
  canvas: "#f5f6fa"
  paper: "#ffffff"
  danger: "#b83d3d"
  warning: "#986414"
typography:
  display:
    fontFamily: "Segoe UI, Noto Sans, Arial, sans-serif"
    fontSize: "clamp(24px, 2vw, 30px)"
    fontWeight: 550
    lineHeight: 1.18
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Segoe UI, Noto Sans, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Segoe UI, Noto Sans, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 600
rounded:
  sm: "6px"
  md: "9px"
  lg: "12px"
spacing:
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "30px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    padding: "0 13px"
    height: "36px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0 11px"
    height: "38px"
  panel:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: "17px"
---

## Overview

Magnus SIG is an operational inventory workspace. Its visual direction follows the supplied Nexo references: white working surfaces on a quiet cool-gray canvas, compact persistent navigation, a centered workspace search, and content organized around real stock and traceability. The Magnus logo's indigo, cyan, and orange identity sets the interface palette.

**The Data First Rule.** Every metric, list, chart, and status comes from persisted system records; an empty database produces an honest empty state.

## Colors

Indigo anchors primary actions, selected navigation, and inventory charts. Cyan supports secondary chart series, input focus, and secondary highlights. Orange emphasizes attention states and a third chart series. Use the three brand colors in a balanced way across metric cards, charts, and section accents; keep large content surfaces white so dense inventory data stays readable. Red marks exhausted stock and destructive actions. Success states may use semantic green. Ink, muted text, borders, canvas, and paper maintain contrast without competing with inventory information.

**The Indigo Action Rule.** Indigo marks an action that changes or advances inventory. Keep alerts semantic so color is never their only signal.

## Typography

Use the platform sans-serif stack for predictable rendering on the local Windows environment. Page titles lead at 24–30px; section titles sit around 16px; body copy stays at 15px and supporting labels and metadata remain at least 12px. Tabular values use lining numerals when available.

## Layout

On desktop, a narrow left navigation rail sits beside a flexible content area and a 58px top bar. Use a fluid main column with a secondary summary rail where it helps a task. On narrow screens, move navigation above the page content, allow its links to scroll horizontally, and stack secondary panels. Tables retain readable columns inside their own horizontal scroll region rather than widening the full page.

**The One Scroll Rule.** The page scrolls vertically; a wide table may scroll horizontally within its own panel.

## Elevation & Depth

Prefer a fine border and a soft, low shadow for cards and tables. Keep navigation and forms flat. Do not use dark panels as decoration.

## Shapes

Panels use restrained 9–12px corners. Controls use 6–7px corners; status labels use small rounded chips. Borders are light and consistent.

## Components

Primary buttons use brand indigo with white text. Secondary buttons are white with a light border. Inputs have visible labels, a white surface, and a cyan keyboard-focus ring. Data tables use quiet headers, clear row separation, and direct actions. Sidebar items use a pale indigo selected state. Stock labels distinguish available, low, and exhausted units with both color and text.

## Do's and Don'ts

- Do make the next operational action obvious and keep product, stock, and category counts tied to database queries.
- Do show an empty state when a list has no records.
- Do retain visible keyboard focus and mobile table containment.
- Don't present invented sample products or sales activity as real.
- Don't use a gradient, glow, or dark panel to decorate a data surface.
- Don't use color alone to communicate stock state.
