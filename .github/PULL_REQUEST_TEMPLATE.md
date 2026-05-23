<!--
Thanks for contributing to the Cowork Cookbook!
Please tick the boxes that apply and remove sections that don't.
-->

## Summary

<!-- One-line description of the change. -->

## Type of change

- [ ] New recipe
- [ ] Recipe update / fix
- [ ] Taxonomy / BPMN change
- [ ] Schema / CI / governance change
- [ ] Documentation

## Checklist (for recipe PRs)

- [ ] `recipe.yaml` validates against `schemas/recipe.schema.json`
- [ ] All provenance fields populated (`generated_by`, `reviewed_by`, `last_verified_on`, `verified_against_cowork_build`)
- [ ] If `mutates_data: true`, a `VERIFICATION.md` is included describing sandbox verification
- [ ] Every image has non-empty alt text
- [ ] Custom `skill/` (if present) honors Cowork limits: `SKILL.md` ≤ 1 MB, ≤ 20 companion files, ≤ 10 MB total
- [ ] `uses_skills` accurately lists OOTB / plugin / custom skills the recipe relies on
- [ ] Slug is permanent — if renaming, a redirect entry was added to `taxonomy/redirects.yaml`

## Notes for reviewers

<!-- Anything reviewers should know? Sandbox tenant used? Cowork build number? Screenshots TBD? -->
