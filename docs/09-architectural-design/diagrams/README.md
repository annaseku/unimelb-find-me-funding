# Diagrams

Editable draw.io sources. **These files are the source of truth** — edit them,
don't redraw. Open at [app.diagrams.net](https://app.diagrams.net)
(File → Open From → Device) or with the draw.io extension in VS Code.

| File | Diagram | Answers |
|---|---|---|
| `high-level-architecture.drawio` | One-page overview for clients and presentations | Supervisor feedback: "one overall system design diagram"; the diagram to open first |
| `system-architecture.drawio` | Layered system architecture, module level | Checklist item 9 |
| `component-diagram.drawio` | Modules and their interfaces | Checklist item 9 (architectural design) |
| `deployment-diagram.drawio` | GitHub Pages, Render, Supabase, Gemini, GitHub Actions | Checklist item 12 (deployment) |
| `er-diagram.drawio` | Physical schema plus the logical model inside `opportunity_json` | Checklist item 9; database design |
| `domain-class-diagram.drawio` | Pydantic models across crawl → normalise → rank → serve | Checklist item 9; checklist item 10 (coding) |
| `sequence-search-funding.drawio` | Sequence — a user searches for funding | Checklist item 9; traces a user story to components |
| `sequence-crawl-ingest.drawio` | Sequence — scheduled crawl and ingest | Checklist item 9; shows the robots.txt gate |
| `activity-ranking.drawio` | How a search becomes a ranked page of results | Checklist item 9; explains the ranking engine |
| `state-opportunity-lifecycle.drawio` | One opportunity from discovery to soft-deleted closure | Checklist item 9; scheduler and retention behaviour |
| `use-case-diagram.drawio` | Use case diagram, Weeks 1–6 scope | Checklist item 7 (requirements) |

## Publishing to Confluence

Ready-made 2x PNG exports of every diagram live in `png/` — attach those to the
matching Confluence page. To re-export after an edit, use File → Export as
(PDF or PNG, zoom 200%) and attach to the matching
Confluence page, or paste the file into the draw.io Confluence macro. Keep the
`.drawio` source here so the next change is an edit, not a redraw.

The Confluence [Architecture Overview] page also renders the layered diagram
natively from a Mermaid block, because the site has the Mermaid app installed.
Where the two disagree, this folder wins.

[Architecture Overview]: https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/30834690

## Conventions

- Title, "Last Updated" date and a `//` scope note at the top of every diagram.
- Solid arrow = call or data flow; dashed arrow = return, dependency or external fetch.
- Bump the version in the title block whenever a diagram changes meaning.
- One colour per layer, the same in every diagram: blue = presentation, green = API and ranking,
  yellow = crawler and normaliser, purple = data access, red = database, grey = external.
- Edges are routed through explicit waypoints with labels offset beside the line, so nothing
  crosses a box or sits on top of another label. Keep it that way when adding arrows.
- Every cell needs a unique id. Duplicate ids silently overwrite each other —
  this bit us once on the state diagram, where transition ids collided with the
  title and made the header disappear.

## Known inconsistency to resolve

`render.yaml` cites `docs/09-architectural-design/adr/ADR-003-deployment-architecture.md`, but the file
on disk is `ADR-003-normaliser.md`. One of the two is wrong — worth settling
before the ADRs are published to Confluence, since ADR-004 was going to cover
hosting and persistence.
