# D365 Forecast to plan Expert

A Dynamics 365 Finance & Supply Chain Management expert scoped to the Forecast to plan end-to-end process - covers 5 L2 areas and 45 L3 processes from the Microsoft Business Process Catalog.

> ℹ **This is a Cowork custom skill.** Place the contents of the `skill/` folder under `Documents/Cowork/skills/d365-forecast-to-plan/` in your OneDrive. Cowork auto-discovers custom skills at the start of each conversation.

## How to install

The recipe page above ships a one-click **Download skill.zip** button (extracted from this repo's `skill.zip` + `skill.zip.sha256` for tamper-evidence). To install:

1. Click **Download skill.zip** on the recipe page.
2. Extract the archive - you get a folder named `d365-forecast-to-plan/` containing `SKILL.md`.
3. Drop that folder into your OneDrive at `Documents/Cowork/skills/`.
4. Start a new Cowork conversation - the skill loads automatically.

**Manual fallback**: navigate to `/Documents/Cowork/skills/` in OneDrive, create a subfolder named `d365-forecast-to-plan`, download `skill/SKILL.md` from the source repo, drop it in.
## How to use

Once the skill is installed, the bootstrap prompt below activates it for a single conversation:

![Cowork /skills audit confirming this skill loads](screenshots/01-cowork-audit.png "Cowork /skills audit on 2026-05-24 confirming all 30 d365-* skills load as personal skills from Documents/Cowork/skills/")

## Skill contents

The skill file is in `skill/SKILL.md`. It includes:

- The real 22-tool D365 ERP MCP surface (data / form / action tools)
- USMF tenant data conventions (date eras, known entity gaps)
- Honest-degrade defaults so the agent stops instead of fabricating

## License

CC-BY-4.0 - see repo `LICENSE`.
