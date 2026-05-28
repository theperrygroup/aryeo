# Foundation

Durable design decisions for the Sentry reporting integration. These docs
outrank trackers and execution notes when they overlap.

## Documents

| Document | Owns |
| --- | --- |
| `integration-model-adr.md` | The enrich-only model, never-init rule, no-op contract, and opt-in surface. |
| `data-safety-and-scrubbing-adr.md` | Token and PII scrubbing policy, allowed fields, and redaction defaults. |
| `optional-dependency-and-versioning-adr.md` | The `aryeo[sentry]` extras boundary, lazy import rule, and the planned `0.2.0` bump. |

## Read Order

1. `integration-model-adr.md` for the shape of the feature.
2. `data-safety-and-scrubbing-adr.md` for the hard safety constraints.
3. `optional-dependency-and-versioning-adr.md` for packaging and release impact.

## Cross-References

These shared repo rules govern this initiative and are not duplicated here:

- `.cursor/rules/release-quality-contract.mdc`
- `.cursor/rules/docs-tests-sync.mdc`
- `.cursor/rules/api-client-implementation.mdc`
- `.cursor/rules/api-source-of-truth.mdc`
