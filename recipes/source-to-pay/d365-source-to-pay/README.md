# D365 Source to pay Expert

A Dynamics 365 Finance & Supply Chain Management expert scoped to the Source to pay end-to-end process - covers 6 L2 areas and 42 L3 processes from the Microsoft Business Process Catalog.

> ℹ **This is a Cowork custom skill.** Place the contents of the `skill/` folder under `Documents/Cowork/skills/d365-source-to-pay/` in your OneDrive. Cowork auto-discovers custom skills at the start of each conversation.

## Business value

Save time and improve accuracy by giving Cowork a persistent expert context for the target domain - it knows the right entities, the USMF tenant data quirks, and the honest-degrade options before you even open a task.

## How to install

**Option A - One-click ZIP (recommended)**

1. [Download `d365-source-to-pay.zip`](https://github.com/seangalliher/Coworkcookbook/raw/main/recipes/source-to-pay/d365-source-to-pay/skill/dist/d365-source-to-pay.zip)
2. Extract the archive - you get a folder named `d365-source-to-pay/` containing `SKILL.md`.
3. Drop that folder into your OneDrive at `Documents/Cowork/skills/`.
4. Start a new Cowork conversation - the skill loads automatically.

**Option B - Manual**

1. Open OneDrive in your browser or sync client.
2. Navigate to `/Documents/Cowork/skills/` (create the folder if it doesn't exist).
3. Create a subfolder named `d365-source-to-pay`.
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
