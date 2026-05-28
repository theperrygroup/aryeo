# Trackers

Focused readiness trackers for the Sentry reporting initiative.

## Documents

| Tracker | Lens |
| --- | --- |
| `readiness-overview.md` | Aggregate phase readiness across the whole initiative. |
| `data-safety-readiness.md` | Highest-risk lens: token and PII leakage guarantees. |
| `docs-tests-readiness.md` | Docs, tests, and examples sync per the repo rules. |

## Grade Rules

- `Planned`: only a proposal or roadmap item exists.
- `In Progress`: some artifact landed but the slice is unfinished.
- `Complete`: the tracked planning or prerequisite slice is checked in.
- `Live`: checked-in code and proof show the runtime behavior exists.
- `Blocked`: the next step is known but cannot proceed honestly yet.

## Interpretation Rule

- `Complete` here means a planning or prerequisite slice is checked in.
- It does not mean the Sentry feature is live in the shipped package.
- Runtime truth still comes from checked-in code under `aryeo/`.

## Update Rules

- Update the focused tracker first, then `readiness-overview.md`, then the
  execution ledger.
- Keep these trackers in sync with `execution/execution-plan.md`.
