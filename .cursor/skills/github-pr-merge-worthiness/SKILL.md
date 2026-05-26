---
name: github-pr-merge-worthiness
description: Audit open GitHub pull requests for theperrygroup/aryeo, decide whether they are worth merging, fix clear blockers for valuable PRs, safely merge PRs that pass repo gates, and close PRs that are unsafe or not recommended. Use when the user asks to review open PRs, decide whether PRs should be merged, merge worthwhile PRs, close bad PRs, clean up the PR queue, or inspect https://github.com/theperrygroup/aryeo/pulls.
---

# GitHub PR Merge Worthiness

## Use This Skill

Use this as the default repo-local workflow when the user wants open pull
requests reviewed for merge-worthiness. The default outcome is active queue
management: merge PRs that are clearly worth merging, close PRs that are
clearly unsafe or not recommended, and automatically start fixing clear blockers
for worthwhile PRs instead of returning only a status report.

This skill is write-capable only when the user asked for PR queue cleanup,
merge-worthiness action, merging, closing, or fixing blockers. Merging and
closing still require concrete evidence from GitHub metadata, CI, code diff,
and repo rules.

Repository:

- owner/repo: `theperrygroup/aryeo`
- PR list: `https://github.com/theperrygroup/aryeo/pulls`
- primary merge base: `main`
- package: typed Python API client for the Aryeo API

## Read First

Before acting, read these repo rules:

- `.cursor/rules/api-client-implementation.mdc`
- `.cursor/rules/release-quality-contract.mdc`
- `.cursor/rules/docs-tests-sync.mdc`
- `.cursor/rules/api-source-truth.mdc`

Before changing API behavior, also read:

- `docs/planning/aryeo-api-client/foundation/api-source-of-truth.md`
- `docs/planning/aryeo-api-client/foundation/source-of-truth-matrix.md`

Use GitHub CLI for all PR, check, review, merge, and close operations. Do not
force-push, bypass required checks, publish releases, or commit local changes
unless the user explicitly asked for that action.

## Start With A Queue Snapshot

Fetch open PRs and enough metadata to classify them:

```bash
gh pr list --repo theperrygroup/aryeo --state open --limit 100 --json number,title,author,isDraft,baseRefName,headRefName,headRepositoryOwner,headRepository,mergeStateStatus,reviewDecision,updatedAt,url
```

For each candidate PR, inspect details before deciding:

```bash
gh pr view <number> --repo theperrygroup/aryeo --json number,title,body,author,isDraft,baseRefName,headRefName,headRepositoryOwner,headRepository,headRefOid,mergeStateStatus,mergeable,reviewDecision,commits,files,additions,deletions,changedFiles,labels,assignees,reviewRequests,statusCheckRollup,latestReviews,closingIssuesReferences,url
gh pr diff <number> --repo theperrygroup/aryeo
gh pr checks <number> --repo theperrygroup/aryeo --watch=false
```

For multiple PRs, rank first by likely library value and merge readiness:

- small, focused, repo-owned fixes with green CI
- bug fixes, security fixes, release blockers, CI fixes, docs build fixes, or
  packaging fixes
- endpoint/client additions that include code, tests, docs, examples when
  user-facing usage changes, and planning tracker updates
- changes that keep generated API artifacts and source-of-truth docs aligned
- stale, broad, duplicative, failing, or unclear PRs later

## Auto-Work Before Reporting

Do not stop after classifying a valuable PR as "blocked" when the next safe
engineering action is clear. Start working on the highest-confidence blocker
immediately, then continue the merge-worthiness workflow after verification.

Automatically proceed when the blocker is one of these repo-local issues:

- CI fails on formatting, import order, lint, typing, packaging, docs build,
  dependency audit, or a small stale test assertion.
- The PR branch is only behind `main` and GitHub can update it safely.
- A resource endpoint change is missing the matching focused test, docs page,
  example update, or planning tracker update and the intended behavior is clear
  from checked-in API sources.
- Versioning is inconsistent across `pyproject.toml`, `aryeo/__init__.py`, and
  release workflow expectations for a releasable change.
- Several open PRs share the same inherited blocker; fix the shared blocker
  once on `main` or the most appropriate repo-owned branch, then re-check the
  queue.

Pick the work target conservatively:

- Prefer fixing inherited/shared failures on `main` when multiple PRs are
  blocked by the same `main` failure.
- Prefer checking out and fixing the PR branch when the failure is introduced by
  that PR's diff and the head branch is in `theperrygroup/aryeo`.
- Do not push to fork branches unless the user explicitly asked and permissions
  allow it; otherwise prepare the local fix and report the exact push blocker.
- Treat PR branch checkouts as temporary. Note the current branch before
  checkout and return to local `main` before final handoff.

After any fix, run the focused checks that reproduce the failure, check lints
for edited files, commit only when the user requested a commit, and re-check the
affected PRs. If the fix lands on `main`, refresh or update PR branches as
needed and poll CI until the next concrete blocker appears.

Only return a blocker-only report when the next action is unsafe, destructive,
requires missing permissions, depends on a product/API-contract decision, or
needs author context that is not present in the PR.

## Merge-Worthiness Criteria

A PR is worth merging only when all required gates pass:

- It targets `main` unless the user explicitly asked for a different base.
- It is not a draft.
- It is mergeable or can be made mergeable by safely updating from base.
- Required checks are passing after any base refresh.
- Review state is acceptable for the repo: approved or no blocking requested
  changes, and no unresolved review threads that block correctness.
- The diff is understandable and has a clear purpose.
- Python code has thorough type hints and Google-style docstrings where public
  or non-trivial functions/classes are added or changed.
- Endpoint/client changes land under `aryeo/` flat resource modules and keep
  `aryeo/resources/` as compatibility re-export modules only.
- Endpoint/client changes include synchronized tests, docs, examples when
  user-facing usage changes, and owning planning docs under
  `docs/planning/aryeo-api-client/`.
- API behavior is backed by the source-of-truth order in
  `.cursor/rules/api-source-truth.mdc`; contradictions are recorded in the
  planning tree before coding.
- Release-intended changes keep `pyproject.toml`, `aryeo/__init__.py`, and
  release workflow expectations aligned on semantic versioning.
- It does not include secrets, credential material, `.env`, local-only files,
  cache files, build output, or accidental artifacts.
- It does not weaken CI/release validation for formatting, import order, lint,
  typing, tests, package build, strict docs build, or dependency/security audit.
- Risky changes to generated models/enums, OpenAPI artifacts, pagination,
  authentication, packaging, or release automation have focused verification
  evidence.

## Safe Merge Path

For PRs that pass the criteria:

1. Confirm merge state and check status immediately before merging:

```bash
gh pr view <number> --repo theperrygroup/aryeo --json headRefOid,mergeStateStatus,mergeable,reviewDecision,statusCheckRollup
gh pr checks <number> --repo theperrygroup/aryeo --watch=false
```

2. If the PR is only blocked because the branch is behind `main`, update it:

```bash
gh pr update-branch <number> --repo theperrygroup/aryeo
```

After updating, poll CI in short intervals until checks pass or a real blocker
appears.

3. Determine the merge method from repo settings and recent merged PRs. Prefer
the repository's established method. If only one method is enabled, use that.
Do not use force pushes or bypass required checks.

Useful read-only checks:

```bash
gh repo view theperrygroup/aryeo --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,deleteBranchOnMerge
gh pr list --repo theperrygroup/aryeo --state merged --limit 10 --json number,title,mergedAt,mergeCommit
```

4. Merge non-interactively with the chosen method, deleting the branch when the
repo allows it:

```bash
gh pr merge <number> --repo theperrygroup/aryeo --merge --delete-branch
```

Use `--squash` or `--rebase` instead of `--merge` only when that is the
established or only enabled repo method.

5. After merge, report the PR number, title, URL, merge method, merge commit SHA
when available, and any new `main` CI run that starts.

## Close Path

Close PRs that are unsafe or not recommended when there is concrete evidence,
not just uncertainty. Add a concise comment explaining the reason.

Close a PR when one or more of these are true:

- It is spam, malicious, includes secrets, or introduces obvious security risk.
- It targets the wrong base or stale architecture and is not salvageable.
- It duplicates already-landed work.
- It is abandoned and failing, with no clear small repair path.
- It removes required repo guardrails such as strict docs, typing, tests,
  packaging checks, dependency audit, version alignment, or planning docs.
- It introduces broad API semantics the user has not approved or that conflict
  with checked-in API sources without recording the contradiction.
- It has unresolved requested changes or failing checks that indicate the design
  should not land, not merely that a small fix is needed.
- The diff is dominated by generated, cache, local, vendored, build, or
  unrelated churn.

Close with:

```bash
gh pr close <number> --repo theperrygroup/aryeo --comment "$(cat <<'EOF'
Closing this because it is not recommended to merge in its current form.

Reason:
- <specific evidence from CI/reviews/diff/repo rules>

This can be reopened or replaced if the underlying issue is addressed in a focused PR.
EOF
)"
```

Do not close when the evidence only says "needs a small fix." In that case,
either fix the PR locally if it is repo-owned and safe, or classify it as
blocked with the exact fix needed.

## Fix-Locally Path

If a PR is valuable but blocked by a clear repo-local issue:

- Fetch the PR branch only after confirming the branch source and that the work
  is safe to inspect.
- If the same failure is already present on `main`, fix the inherited failure on
  `main` first rather than patching every PR branch.
- Work without overwriting unrelated local changes.
- Run focused checks for any code, docs, or workflow edit.
- Push only when the PR branch is in this repository or the user explicitly
  asked for a fork branch update and permissions allow it.
- Do not leave the local checkout on the PR branch. A PR branch checkout is a
  temporary inspection or repair workspace; the final local branch should be
  `main` unless a concrete blocker prevents returning.

Useful commands:

```bash
git branch --show-current
gh pr checkout <number> --repo theperrygroup/aryeo
PR_BRANCH="$(git branch --show-current)"
git status -sb
# After inspection or PR-branch fixes:
git switch main
git merge --ff-only "$PR_BRANCH"
```

Run the narrowest relevant local checks first, then broaden when the change
affects shared behavior:

```bash
black --check --diff --line-length=88 .
isort --check-only --diff --profile=black --line-length=88 .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
mypy aryeo/ --strict --ignore-missing-imports
pytest --cov=aryeo --cov-report=term-missing
mkdocs build --strict
python -m build
python -m twine check dist/*
pip-audit
```

Use `python tools/verify_live_integrations.py` only when live integration
evidence is relevant and required credentials/fixture IDs are available. Do not
introduce mutating live checks as part of PR triage unless the user explicitly
approved that behavior.

## Escalate Instead Of Acting

Stop before merge or close only for concrete blockers:

- missing GitHub permissions
- merge method cannot be determined and multiple methods are enabled
- required product decision or API-contract decision
- destructive release, publish, or irreversible external service action
- evidence conflict between CI, reviews, local diff, and source-of-truth docs
- the PR appears valuable but needs author context not present in the PR

When stopping, provide the exact PR number, blocker, evidence gathered, and the
specific action that would make the next step safe.

## Final Report

Return a compact queue summary:

- merged PRs with numbers, titles, URLs, merge methods, and merge SHAs
- closed PRs with numbers, titles, URLs, and specific close reasons
- PRs left open with exact blockers or next actions
- CI, review, source-of-truth, and local verification evidence used for each
  decision
- commands run and any commands that were blocked by permissions
