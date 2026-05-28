# Docs And Tests Readiness

## Purpose

Track the documentation, test, and example artifacts the `docs-tests-sync` and
`api-client-implementation` rules require to land with the feature.

## Interpretation Rule

- `Planned` means the artifact does not exist yet.
- `Checked in` means the artifact exists in the repo.
- `Verified` means the relevant gate passes against it.

## Current Snapshot

Snapshot date: `2026-05-28`

| Artifact | Status | Notes |
| --- | --- | --- |
| `tests/test_sentry.py` | Verified | 123 tests pass, including no-op, capture, breadcrumb, scrubbing, never-init, and default-off. |
| Coverage on `aryeo/sentry.py` | Verified | `--cov=aryeo` reports 97% on the module. |
| `docs/guides/sentry.md` | Checked in | Usage, opt-in, enrich-only model, and safety guarantees. |
| `docs/api-reference/sentry.md` | Checked in | mkdocstrings page for the reporter and options. |
| README section | Checked in | Opt-in usage block with `aryeo[sentry]`. |
| `examples/sentry_reporting.py` | Checked in | Runnable enrich-only example. |
| mkdocs nav entries for guide and reference | Checked in | Added under Guides and API Reference. |
| `mkdocs build --strict` passes | Verified | Strict build succeeds with the new pages. |

## Current Blockers

- None. Docs, tests, and examples landed with the runtime change.

## Current Conclusion

- All docs, tests, and examples for the feature are `checked in` and `verified`.
- The planning tree's own pages remain wired into nav separately.
