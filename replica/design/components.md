# UI Component Design Specifications

Clean-room design system specifications for the Icecream Ebook Reader replica.  
Grounded in `replica/recon.md` (Screens S01A–S12, Components C01–C10) and validated against WCAG 2.2 AA / AAA design tokens (`tokens.json`).

---

## 1. Button (`IceButton`)

Universal interactive trigger supporting standard button roles, tool icons, and destructive actions.

- **Variants**:
  - `primary`: Solid accent fill for main calls to action ("+ Add Book", "Start Reading", "Save Note").
  - `secondary`: Neutral surface with border for supporting actions ("Cancel", "Select image").
  - `ghost`: Transparent background with text/icon only ("Select all", "Clear search").
  - `danger`: Outline/filled danger red for irreversible actions ("Delete book", "Clear all bookmarks").
  - `tool-icon`: Square frameless button for toolbars with embedded SVG icon (`20x20` px).
- **Sizes**:
  - `sm`: Height `28px`, padding `0 10px`, font `sm/500`, radius `sm (5px)`.
  - `md`: Height `36px`, padding `0 14px`, font `base/500`, radius `sm (5px)`.
  - `lg`: Height `44px`, padding `0 20px`, font `md/600`, radius `md (8px)`.
  - `icon`: Fixed `32x32px` or `36x36px`, radius `sm (5px)` or `pill`.
- **States**:
  - `default`: Normal appearance per variant.
  - `hover`: Subtle brightness/lightness shift; background transitions over `fast (120ms)`.
  - `active` / `pressed`: Background inset shift + scale `0.98`.
  - `focus-visible`: `2px solid var(--color-accent)` with `2px` offset.
  - `disabled`: Opacity `0.45`, cursor `not-allowed`, non-interactive.
  - `loading`: Retains width, displays animated spinner, hides label from visual DOM while preserving `aria-label`.
- **Tokens**:
  - Primary: `bg accent`, `hover accent-hover`, `text on-accent`, `radius sm`, `font sm/600`.
  - Secondary: `bg surface`, `hover surface-hover`, `border border`, `text text`.
  - Danger: `bg transparent`, `border danger`, `text danger`, `hover bg-danger text-on-accent`.
- **Accessibility (a11y)**:
  - Native `<button>` / `QPushButton`.
  - `aria-disabled="true"` when inactive; keyboard activatable via `Enter` and `Space`.
  - Visible focus ring always enabled for keyboard navigation.
- **Used on**: S01A, S01B, S02, S03, S05, S07, S08, S09, S11, S12.

---

## 2. Text Input & Search Field (`IceLineEdit`)

Single-line text entry field with optional leading search icon and trailing clear button.

- **Variants**:
  - `standard`: Boxed text entry for forms and dialogs (Title, Author, Preferences).
  - `search`: Pill/rounded box with embedded magnifying glass SVG and trailing clear `X`.
- **Sizes**:
  - `sm`: Height `30px`, font `sm (13px)`, padding `4px 10px`.
  - `md`: Height `36px`, font `base (14px)`, padding `6px 12px`.
- **States**:
  - `default`: White surface with `border-input (1px)`.
  - `hover`: Border tint shifts toward `text-muted`.
  - `focus`: `2px solid var(--color-accent)` with `0px` outline.
  - `disabled`: Surface tinted `surface`, text `text-muted`, cursor `not-allowed`.
  - `error`: `1px solid var(--color-danger)`, error tooltip or label below.
  - `has-value`: Trailing clear `X` button appears on hover or focus.
- **Tokens**:
  - `bg bg`, `text text`, `border border-input`, `focus-border accent`, `radius sm`, `font base/400`.
- **Accessibility (a11y)**:
  - Associated `<label>` or `accessibleName`.
  - Search input role `searchbox`; clear button has `aria-label="Clear search"`.
  - `Escape` key clears text; `Enter` commits search or filter.
- **Used on**: S01A, S01B, S05, S08, S09, S10.

---

## 3. Book Cover Card (`BookCardWidget` - C03)

Interactive visual card displaying book cover, format pill, favorite state, and reading progress in S01A.

- **Dimensions**: Fixed `160px` width $\times$ `240px` height.
- **Sub-Components**:
  - `ThumbnailFrame`: `150x200px` image container with `4px` border radius and `card` shadow.
  - `FormatBadge`: Absolute positioned top-left pill (`EPUB`, `PDF`, `MOBI`).
  - `FavoriteToggle`: Absolute positioned top-right star icon (`20x20px`).
  - `TitleLabel`: Font `sm/600`, max 2 lines with elision (`...`).
  - `AuthorLabel`: Font `xs/400`, color `text-muted`, 1 line elided.
  - `ProgressBar`: `3px` horizontal progress indicator at bottom of thumbnail.
- **States**:
  - `default`: Base elevation, favorite star transparent unless book is favorited.
  - `hover`: Elevates +2px (`shadow-card-hover`), favorite star becomes visible, border glows.
  - `selected`: `2px solid var(--color-accent)` outline, top-right checkmark badge displayed.
  - `dragging`: Opacity `0.75`, shadow `popover`.
  - `no-cover`: Renders stylized SVG book placeholder with title and format monogram.
- **Tokens**:
  - `bg surface`, `text text`, `text-muted text-muted`, `radius md`, `shadow card`, `progress success`.
- **Accessibility (a11y)**:
  - Role `article` or `listitem` with `aria-label="[Title] by [Author], [Progress]% read"`.
  - Double-click or `Enter` opens book; `Space` toggles selection.
- **Used on**: S01A (Library Shelf Grid).

---

## 4. Library Table View (`BookTableView` - C04)

High-density metadata grid supporting sorting and batch selection in S01B.

- **Structure**:
  - Fixed header row with sortable column headers: `Title`, `Author`, `Date Added`, `Notes`, `Progress`, `Format`.
  - Alternating rows (`#ffffff` and `var(--color-surface)`).
- **Sub-Components**:
  - `CoverThumbnailDelegate`: `24x32px` micro-thumbnail preceding title text.
  - `NotesBadge`: Counter pill rendering note count (`12px` font, rounded pill).
  - `ProgressBarDelegate`: Inline progress bar with percentage label.
- **States**:
  - `row-default`: Light or alternating surface.
  - `row-hover`: Background `var(--color-surface-hover)`.
  - `row-selected`: Background `var(--color-accent)`, text `var(--color-on-accent)`.
  - `column-sorted`: Header renders directional arrow SVG icon (ascending/descending).
- **Tokens**:
  - `bg bg`, `alt-bg surface`, `border border`, `selected accent`, `text text`, `header-text text-muted`.
- **Accessibility (a11y)**:
  - Table role `grid` with full keyboard arrow navigation.
  - Headers announce sort state (`aria-sort="ascending"`).
- **Used on**: S01B (Library Catalog Table).

---

## 5. Navigation Sidebar (`MainWindow_SideBar` - C01)

Permanent left-docked application navigation panel.

- **Dimensions**: Fixed width `220px`, full application height.
- **Sub-Components**:
  - `LogoHeader`: Application icon and wordmark title.
  - `CategoryList`: List of system folders (`All`, `Recently Read`, `Read`, `Favorites`, `Deleted`).
  - `FormatsSection`: Expandable tree item showing formats (EPUB, PDF, etc.) with book count pills.
  - `UserFolders`: Dynamic user categories with context menu (Rename, Delete).
  - `AddFolderButton`: Compact button "+ Add Category".
  - `BottomUtilityBar`: Pinned footer icons for "Settings" and "Help".
- **States**:
  - `item-default`: Transparent background, text `sidebar-text-muted`.
  - `item-hover`: Background `sidebar-surface`, text `sidebar-text`.
  - `item-active` / `selected`: Background `accent`, text `on-accent`, font weight `600`.
- **Tokens**:
  - `bg sidebar-bg`, `surface sidebar-surface`, `text sidebar-text`, `text-muted sidebar-text-muted`, `border sidebar-border`.
- **Accessibility (a11y)**:
  - Role `navigation`.
  - Up/Down arrow keys navigate items; `Enter` activates category filter.
- **Used on**: S01A, S01B.

---

## 6. Library Top Action Bar (`LibraryHeaderBar` - C02)

Top utility toolbar providing core library management actions.

- **Dimensions**: Height `56px`, full width minus sidebar.
- **Sub-Components**:
  - "+ Add Book" button (Primary Accent).
  - "+ Add Folder" button (Secondary).
  - Instant Search Field (`IceLineEdit` search variant with debounce).
  - View Switcher: Segmented button group toggling Grid (S01A) vs. Table (S01B).
- **States**:
  - `default`: White background with bottom border.
  - `searching`: Clear `X` visible inside search input; table/grid actively filtered.
- **Tokens**:
  - `bg bg`, `border border`, `height 56px`, `spacing 8px`.
- **Used on**: S01A, S01B.

---

## 7. Library Operations Footer (`LibraryFooterBar` - C05)

Contextual sliding tray appearing when books are selected or background jobs execute.

- **Dimensions**: Height `48px`, pinned to bottom edge.
- **Sub-Components**:
  - `SelectionCounter`: "%1 books selected".
  - `ActionGroup`: "Select all", "Clear selection", "Add to category", "Delete".
  - `JobProgressGroup`: Background import/export progress bar with item count and Pause/Cancel buttons.
- **States**:
  - `hidden`: Off-screen translation `translateY(100%)`.
  - `visible`: Slides up via `motion-drawer (260ms)`.
  - `in-trash`: "Delete" transforms to "Restore" and "Purge permanently".
- **Tokens**:
  - `bg surface`, `border border`, `shadow popover`, `motion drawer`.
- **Used on**: S01A, S01B.

---

## 8. Reader Top Toolbar (`ReadingToolBar` - C06)

Floating top control bar in reader canvas with autohide support in fullscreen.

- **Dimensions**: Height `48px`, horizontal floating bar.
- **Sub-Components**:
  - Left group: Back to Library (`Esc`), Separator.
  - Center-left group: TOC (`Ctrl+T`), Bookmarks (`Ctrl+B`), Notes (`Ctrl+N`), Search (`Ctrl+F`).
  - Center-right group: Zoom Out, Reset (100%), Zoom In, Fit Page / Fit Width.
  - Right group: TTS Play/Pause (`F7`), Stop (`F8`), Print (`Ctrl+P`), Quick Settings gear.
- **States**:
  - `visible`: Docked at top with `rgba(255, 255, 255, 0.95)` backdrop blur.
  - `autohidden`: Slides off-screen in fullscreen; reveals on mouse approach within `20px` of top edge.
  - `themed`: Background and icon colors synchronize with active reading theme (Day, Night, Sepia, Dark Sepia).
- **Tokens**:
  - `bg reader-surface`, `border reader-border`, `text reader-text`.
- **Used on**: S02 (Reader Window).

---

## 9. Reader Scrubber Footer (`ReadingFooterBar` - C07)

Translucent bottom scrubber providing reading progress slider and page jumping.

- **Dimensions**: Height `40px`, pinned to bottom of S02.
- **Sub-Components**:
  - `PageCounter`: Text label "Page: %1 / %2".
  - `ScrubberSlider`: Custom horizontal track with chapter ticks.
  - `JumpBackLink`: Dynamic link "Back to page %1" following a bookmark or TOC leap.
- **States**:
  - `default`: Translucent bar over bottom page margin.
  - `scrubbing`: Hover thumbnail or page tooltip follows mouse cursor along slider track.
  - `autohidden`: Fades out in fullscreen mode.
- **Tokens**:
  - `slider-groove border`, `slider-fill accent`, `slider-handle accent`, `text reader-text`.
- **Used on**: S02.

---

## 10. Reading Canvas (`ReadingCanvas`)

Central document display area handling reflowable typography and fixed vector pages.

- **Sub-Components**:
  - `ReflowView`: Dual-column or single-column paginated text canvas.
  - `FixedPageView`: PDF/CBZ viewport with smooth pan and zoom.
  - `LeftMarginClickZone` / `RightMarginClickZone`: 15% width invisible side areas triggering previous/next page on click.
  - `DimOverlay`: Fullscreen black overlay widget with adjustable alpha (0–80%) for night reading.
- **States**:
  - `single-column`: Single centered column with dynamic margins.
  - `two-column`: Open book spread with subtle central gutter line.
  - `loading`: Semi-transparent overlay with spinning `ReadingSpinner`.
  - `dimmed`: Dim overlay active at user-specified percentage.
- **Themes**:
  - Day: Background `#ffffff`, Text `#1a1d20`.
  - Night: Background `#181a1f`, Text `#e2e4e8`.
  - Sepia: Background `#faf3e0`, Text `#3d2e1e`.
  - Dark Sepia: Background `#2b241e`, Text `#ddd1be`.
- **Tokens**:
  - `reader-bg`, `reader-text`, `reader-gutter`.
- **Used on**: S02.

---

## 11. Sliding Side Drawer (`SideDrawer`)

Off-canvas side panel sliding smoothly over the reading canvas.

- **Dimensions**: Width `340px`, full viewport height.
- **Variants**:
  - Left Drawer: Table of Contents (S04).
  - Right Drawer: Bookmarks (S03), Notes & Highlights (S05), In-Book Search (S10).
- **Sub-Components**:
  - `DrawerHeader`: Title label, counter badge, close button (`X`).
  - `DrawerBody`: Scrollable item list (TOC tree, bookmark cards, annotation list, search results).
  - `DrawerFooter`: Action buttons ("Clear all", "Export to HTML").
- **States**:
  - `closed`: Hidden off-canvas via horizontal translate.
  - `open`: Slides in over `260ms` (`motion-drawer`) with soft shadow overlay.
- **Tokens**:
  - `bg surface`, `border border`, `shadow popover`, `motion drawer`.
- **Accessibility (a11y)**:
  - Role `dialog` with focus trapped inside drawer while open.
  - `Esc` key closes drawer and returns focus to reader canvas.
- **Used on**: S03, S04, S05, S10.

---

## 12. Text Selection Bubble (`NotePopup` - C08)

Floating contextual popup appearing adjacent to selected text.

- **Dimensions**: Width `280px`, height `auto`.
- **Sub-Components**:
  - `PaletteSwatches`: 4 circular color swatches (Yellow `#ffe270`, Green `#a8f29a`, Cyan `#7be5f8`, Pink `#ffa0c5`).
  - `ActionIcons`: Add Note (pencil), Copy, Google, Wikipedia, Translate.
  - `InlineCommentPanel`: Expandable multi-line text input with "SAVE" and "CANCEL" buttons.
- **States**:
  - `compact`: Palette swatches and quick action icons only.
  - `expanded`: Inline comment editor active.
  - `dismissed`: Disappears when clicking outside or pressing `Esc`.
- **Tokens**:
  - `bg bg`, `border border`, `shadow popover`, `radius md`.
- **Used on**: S02 (Text selection in S06).

---

## 13. In-Reader Quick Settings Popover (`QuickSettingsPopover` - S07)

Non-modal floating card for live typography and theme adjustments.

- **Dimensions**: Width `320px`, padding `16px`.
- **Sub-Components**:
  - `ThemeSelector`: 4 radio pills for Day, Night, Sepia, Dark Sepia.
  - `FontFamilySelect`: Dropdown list of installed and embedded fonts.
  - `FontSizeControls`: Stepper (`-` / `+`) with point size display.
  - `LineSpacingControls`: 3 spacing options (Tight, Normal, Loose).
  - `ColumnModeSwitch`: Segmented toggle (Single vs. Double column).
  - `AlignmentSwitch`: 4 buttons (Justify, Left, Center, Right).
  - `DimmerSlider`: Horizontal slider adjusting screen dimming percentage (0–80%).
- **Tokens**:
  - `bg surface`, `border border`, `shadow popover`, `radius md`.
- **Used on**: S02, S07.

---

## 14. Custom Frameless Shell (`IceWindow` / `IceDialog` - C09)

Top-level desktop window container with custom styled title bar and native DWM resize borders.

- **Sub-Components**:
  - `TitleBar`: Application icon, window title, minimize button, maximize/restore button, close button.
  - `WindowResizeGrip`: Transparent edge hit-testing zones for native 8-direction resizing.
- **States**:
  - `normal`: Floating window with OS drop shadow.
  - `maximized`: Title bar buttons swap maximize for restore icon; edge padding removed.
  - `fullscreen`: Title bar hidden.
- **Tokens**:
  - `bg bg`, `border border`, `title-text text`.
- **Used on**: Main Window, S08, S09, S11, S12.

---

## 15. Format & Status Badges (`FormatBadge`, `StatusPill`)

Compact visual tags indicating ebook format or reading status.

- **Variants**:
  - `format-epub`: Blue tint pill (`bg #e6f0ff`, `text #1f5fdb`).
  - `format-pdf`: Red tint pill (`bg #ffebe6`, `text #c92a2a`).
  - `format-mobi`: Orange tint pill (`bg #fff2e6`, `text #b35900`).
  - `format-fb2`: Green tint pill (`bg #e6f9f0`, `text #1b7a4b`).
  - `format-cbz`: Purple tint pill (`bg #f3e8ff`, `text #7c3aed`).
  - `format-txt`: Gray tint pill (`bg #f0f3f8`, `text #525b6a`).
- **Dimensions**: Height `18px`, padding `0 6px`, font `xs (11px)`, radius `xs (3px)`.
- **Used on**: S01A (Book cards), S01B (Table format column).

---

## 16. Scrubber Slider (`IceSlider`)

Enhanced horizontal slider for chapter and page navigation.

- **Structure**:
  - `Track`: `4px` height horizontal bar with filled progress portion.
  - `ChapterTicks`: Subtle vertical tick marks along track marking chapter start boundaries.
  - `Thumb`: `14px` circular handle (`16px` on hover) with `2px` white border.
  - `HoverTooltip`: Floating speech bubble displaying target page number and chapter title under cursor.
- **Tokens**:
  - `track-bg border`, `track-fill accent`, `thumb accent`, `radius pill`.
- **Used on**: S02 (Scrubber footer), S07 (Dimming slider), S08 (TTS volume/speed).
