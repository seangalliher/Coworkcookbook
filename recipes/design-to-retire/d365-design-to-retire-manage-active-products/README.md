# D365 Manage active products Expert

A Dynamics 365 F&SCM expert scoped to the Manage active products area (a level-2 subdomain of Design to retire) - covers 8 L3 processes.

> ℹ **This is a Cowork custom skill.** Place the contents of the `skill/` folder under `Cowork/.claude/skills/d365-design-to-retire-manage-active-products/` in your OneDrive. Cowork auto-discovers custom skills at the start of each conversation.

## Business value

Save time and improve accuracy by giving Cowork a persistent expert context for the target domain - it knows the right entities, the USMF tenant data quirks, and the honest-degrade options before you even open a task.

## How to install

1. Open OneDrive in your browser or sync client.
2. Navigate to `/Cowork/.claude/skills/` (create the folder if it doesn't exist).
3. Create a subfolder named `d365-design-to-retire-manage-active-products`.
4. Download `skill/SKILL.md` from this recipe and place it inside the subfolder.
5. Start a new Cowork task - the skill is auto-loaded.

## How to use

Once the skill is installed, the bootstrap prompt below activates it for a single conversation:

![Placeholder screenshot](screenshots/01-placeholder.svg "Placeholder - replace with a real screenshot.")

## Skill contents

The skill file is in `skill/SKILL.md`. It includes:

- The real 22-tool D365 ERP MCP surface (data / form / action tools)
- USMF tenant data conventions (date eras, known entity gaps)
- Honest-degrade defaults so the agent stops instead of fabricating

## License

CC-BY-4.0 - see repo `LICENSE`.
