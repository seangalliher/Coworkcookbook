# Cowork Cookbook — Recipes

A community catalog of prompt and skill "recipes" for **Microsoft Copilot Cowork**, organized along Microsoft's [Business Process Catalog](https://learn.microsoft.com/en-us/dynamics365/guidance/business-processes/overview).

This repository is the **source of truth** for the [Cowork Cookbook](https://github.com/seangalliher/CoworkCookBookWebApp) web app. Recipes live here as files; the website is a rendered/indexed view.

> **Not affiliated with Microsoft.** Microsoft 365 Copilot, Cowork, and Dynamics 365 are trademarks of Microsoft Corporation. Use here is nominative fair use to describe interoperability.

## What is a recipe?

A recipe is a folder under `recipes/<process-area>/<recipe-slug>/` containing:

- `recipe.yaml` — metadata (title, summary, plugin, process tags, provenance fields, license)
- `prompt.md` — the copyable prompt
- `README.md` — full description, prerequisites, step-by-step
- `screenshots/` — at least one screenshot or a YouTube link
- `skill/` (optional) — a Cowork custom skill (`SKILL.md` + companion files), per [Cowork skills docs](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork#cowork-skills)

See `schemas/recipe.schema.json` for the canonical schema and `recipes/source-to-pay/sample-recipe/` for a worked example.

## Repo layout

```
recipes/                  # one folder per recipe
taxonomy/                 # business-process + cowork-skill taxonomies + BPMN files
schemas/                  # JSON Schemas (recipe, taxonomy, skills)
.github/                  # CI, templates, governance
```

## Licensing

- **Recipe content** (markdown, prompts, taxonomy, BPMN, screenshots): [Creative Commons Attribution 4.0 (CC-BY-4.0)](LICENSE).
- **Code** (skill companion files, scripts): [MIT](LICENSE-CODE).
- Each recipe's `recipe.yaml` may override via the `license:` field.

## Branch protection

`main` is protected: PRs require maintainer review, CI must pass, force-push and direct push are disallowed. Configuration is documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Contributing

In v1, recipes are admin-curated. The PR flow exists for maintainers; community PRs are tracked as a v2 feature (see the web app repo).

If you spot a broken or incorrect recipe, please file an issue using the templates in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

To report a security issue privately, see [`SECURITY.md`](SECURITY.md).

## Related links

- Web app repo: https://github.com/seangalliher/CoworkCookBookWebApp
- PRD: `Vibes/PRD-Cowork-Cookbook.md` in the web app repo
- Microsoft Copilot Cowork: https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/
- Business Process Catalog: https://learn.microsoft.com/en-us/dynamics365/guidance/business-processes/overview
