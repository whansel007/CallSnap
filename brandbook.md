# CallSnap Brandbook

This document defines the visual style for the CallSnap UI.

## Voice and tone
- Clear and calm: reduce friction, keep copy short.
- Helpful and direct: explain what will happen, not how it works.
- Friendly and focused: avoid playful slang or heavy jargon.

## Color palette
- Background: `#f3f1ed` (warm paper)
- Text primary: `#2d2a26` (ink)
- Text secondary: `#5f5a54` (muted ink)
- Primary action: `#f7d070` (sun)
- Primary hover: `#e7c15f`
- Secondary action: `#9cc5a1` (sage)
- Secondary hover: `#86b28c`
- Utility button: `#e6e2dc` (stone)
- Utility hover: `#d7d1ca`

## Typography
- Title: Georgia, 22, bold
- Section: Georgia, 12, bold
- Body: Georgia, 11
- Buttons: Segoe UI, 11 bold (primary/secondary), Segoe UI, 10 (utility)

## Layout
- Window size: 520x360
- Page background: `#f3f1ed`
- Outer padding: 24px
- Header spacing: top 24px, bottom 12px
- Content spacing: top 8px, bottom 20px
- Button spacing: 10px between primary actions, 6px between utilities
- Label wrapping: use `wraplength=460`, `justify="left"`

## Components
- Primary action button: flat, full width, sun palette
- Secondary action button: flat, full width, sage palette
- Utility buttons: flat, full width, stone palette
- Section label: "Utilities" in section style

## UI implementation
- Name every widget before packing or placing it; avoid chaining `.pack()` on creation.

## Iconography (optional)
- If added, keep monochrome icons in `#2d2a26` and align left with text.

## Motion
- Minimal: no animations by default; avoid distracting effects.
