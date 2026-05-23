# Contributing

Thanks for your interest in the Cowork Cookbook!

## How recipes ship today (v1)

Recipes in v1 are **admin-curated**. Maintainers author recipes via the web app's admin UI, which opens a PR against this repo. Reviews and merges happen here on GitHub so the audit trail lives with the content.

Community PRs from external contributors are a planned **v2** feature (tracked in the [web app repo issues](https://github.com/seangalliher/CoworkCookBookWebApp/issues?q=label%3Atype%3Adeferred-v2)). We accept issues filed via the templates today.

## Reporting issues

Use the templates in `.github/ISSUE_TEMPLATE/`:
- **Recipe request** — propose a new recipe
- **Recipe broken** — flag a recipe that no longer works
- **Taxonomy update** — propose a change to the business-process tree

For security disclosures, see [`SECURITY.md`](SECURITY.md). Do **not** file security issues publicly.

## Repo conventions

### Licensing

Two licenses apply:
- **Content** (markdown, YAML, BPMN, screenshots) — [CC-BY-4.0](LICENSE)
- **Code** (skill companion files, scripts) — [MIT](LICENSE-CODE)

When you contribute, you agree your contribution is under the matching license.

### Recipe layout

Every recipe is a folder under `recipes/<process-area>/<recipe-slug>/`. See `recipes/source-to-pay/sample-recipe/` for a worked example. The schema is `schemas/recipe.schema.json`.

### Slugs

Slugs are kebab-case and **permanent**. If a slug needs to change, add an entry to `taxonomy/redirects.yaml` so the old URL keeps resolving.

### Image alt text

Every image referenced in a recipe markdown file **must** have non-empty alt text. CI fails the PR otherwise.

### Skill packages

Custom skills follow the [Cowork skill format](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork#cowork-skills):
- Folder with `SKILL.md` (uppercase, YAML frontmatter `name` + `description`)
- Up to 20 companion files
- 10 MB total, 1 MB for `SKILL.md`

CI builds `skill.zip` and a SHA-256 hash.

## Branch protection on `main`

The following rules are enforced:
- Pull request required (no direct pushes)
- At least one maintainer approval (CODEOWNERS-routed)
- All required status checks must pass (`validate` workflow)
- Linear history (no merge commits)
- Force-pushes and branch deletion disabled

## Code of conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).
