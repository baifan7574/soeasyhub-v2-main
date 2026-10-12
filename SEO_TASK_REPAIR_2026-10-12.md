# SoEasyHub SEO task repair — 2026-10-12

## What this local repair changes

- `seo_pusher.py` reads the live `https://soeasyhub.com/sitemap.xml`, then selects only the three reviewed Texas nursing `/p/` guides. It does not query Supabase or take the latest 200 arbitrary records.
- Missing/empty/malformed sitemap, DNS/timeout/HTTP failures, missing core guides, blocked robots, noindex, wrong canonical, invalid page content, failed submission, corrupt state, or failed state/report writes return a nonzero exit. An error does not report zero new URLs.
- Google Indexing API code, credentials references and packages are removed from this task. Ordinary Article content is outside its supported JobPosting / VideoObject BroadcastEvent use.
- The default command only performs public GET checks. IndexNow requires explicit `--submit-indexnow`, page validation and a matching existing public ownership file. HTTP 200 means received; HTTP 202 means received with key validation pending. Neither proves crawling or indexing.
- Accepted notifications record full-page SHA-256 fingerprints. `healthy_no_changes` means all current source/robots/pages were checked and matched the previous accepted baseline. A missing baseline makes all three eligible for notification; it does not prove they are newly published.
- Robots checks deliberately fail conservatively if any bot group's Disallow pattern could cover a core guide, even with an Allow exemption. Wildcards and terminal `$` are recognized. This task does not implement a complete crawler's robots priority rules; conflicting rules require review.

## Workflow behavior proposed for review

The existing 02:00 UTC daily cadence is retained in the local workflow. Pushes and PRs run offline tests only. The production job is restricted to scheduled/manual runs on the default branch. Manual dispatch defaults to read-only; scheduled runs explicitly notify IndexNow for changed, validated guides.

The workflow uses no Supabase or Google credentials, installs no third-party Python packages, and does not commit, push, write databases or deploy a Worker. A unique cache key preserves each run's accepted fingerprint state. An exact cache lookup confirms the save; failure marks both the job and evidence report as errors. Reports are uploaded even when checks fail. GitHub cache can expire or be evicted: a subsequent run transparently reports `baseline_present: false` and can notify the three guides again. This is a notification ledger, not an indexing measurement.

The remote workflow has not been changed or run as part of this repair. Publishing this local workflow would change the existing scheduled job's behavior; obtain the requested authorization before pushing/merging or running a production notification.

## Read-only verification

```powershell
python -B -m unittest discover -s tests -p 'test_seo_pusher.py' -v
python -B seo_pusher.py --report-file <review-output>/seo-health.json
node --check worker.js
node --check core-pages.js
node verify-core-recovery.mjs
git diff --check -- seo_pusher.py .github/workflows/seo_pusher.yml
```

Do not add `--submit-indexnow` to a verification command without authorization for the external notification. The default state location is `.seo/state.json`; the default report location is `.seo/report.json`. The CLI never reads credentials from environment variables.

## Source and rollback context

Actual local project: `D:\quicktoolshub\rader\soeasyhub美国跨州合规报告\soeasyhub-v2`. Local `master` is `82ec352802cee3f2acc52842d41e05195747de6d`; current Worker/core-page recovery changes are outside that commit. Existing staged gsc/matrix changes and modified/untracked Worker files must be preserved.

Worker configuration names `soeasyhub-v2`, entry `worker.js`, account `c70f291b77fbc02a6f2090ebe4abdd44`, routes `soeasyhub.com/*` and `www.soeasyhub.com/*`. The 10/1 handoff records deployed version `23a77260-aadb-4873-9ef1-81803db00517`. That is historical evidence. Current Cloudflare version ID was not authenticated in this execution environment; read-only Wrangler listing required unavailable authentication. No authentication was changed.

Safe pre-edit backup and SHA-256 manifest: `C:\Users\bai\Documents\Codex\2026-10-12\task-2\soeasyhub-seo-repair\backup` and `backup-manifest.json`. For this task's rollback restore only the backed-up `seo_pusher.py` and `.github/workflows/seo_pusher.yml` and remove only this repair's new test/handoff files. Retain current `worker.js`, `core-pages.js`, `wrangler.toml`, and unrelated changes. The original SEO behavior in the backup is faulty; restoring it is an emergency rollback, not a healthy final state.

## Validation limits and smallest publishing step

51 offline regression tests passed under Python 3.10.11, including accepted/rejected notifications and state failures. An independent reviewer reran the same suite and found no remaining blocking code issue. The existing Worker/core-page syntax and database-outage isolation tests passed. YAML parsing and the embedded workflow report step were checked locally: an unconfirmed cache save produces an error report and exit 1. These local checks do not execute GitHub Actions or its cache service.

Public GET evidence at 2026-10-12 10:02:46 UTC recorded 200 for the homepage, packet, sitemap, robots, ownership file and all three guides. Homepage and guides reported `X-SoEasyHub-Content: static-core-20261001`. The sitemap had exactly the expected nine URLs. Robots allowed the guides; the existing public ownership key matched. A prior read-only script check verified all three canonical URLs and noindex absence and made no notification.

The local Worker generates exactly the live sitemap/robots/ownership-file bytes. Public HTML byte hashes differ from local generated HTML; the cause has not been confirmed. The observed marker, routes and historical handoff establish the recovery-family evidence, not an authenticated exact current bundle/version match. Subsequent GET attempts encountered intermittent TLS/transport failures in this execution environment; these failures are not zero metrics. Do not deploy or replace Worker code based on the local `master` commit.

No real IndexNow POST has been tested. Current Cloudflare active version ID, GSC indexing, Supabase recovery, purchases and revenue remain unverified. For Cloudflare, inspect the existing account's **Workers & Pages → soeasyhub-v2 → Deployments** (and the selected version details): active deployment/version ID, creation time, traffic percentage, deployment source and script/modules including `core-pages.js`. Confirm the domains/routes page still maps `soeasyhub.com/*` and `www.soeasyhub.com/*`. This needs existing account access, not new tokens, changed permissions or a new deployment.

After authorization, publish only the SEO script, workflow, tests and this handoff in a focused draft PR. Review the workflow change's production effect before merging. No Cloudflare deployment is needed. Do not include local Worker recovery changes or run any factory/database-write workflow. After an authorized merge, inspect a read-only manual run's report first; an external notification or scheduled execution requires the approved production scope.

References: [Google Indexing API scope](https://developers.google.com/search/apis/indexing-api/v3/using-api), [IndexNow response meaning](https://www.indexnow.org/documentation), [cache save warnings](https://github.com/actions/cache/blob/v4/src/saveImpl.ts), [cache exact lookup inputs](https://github.com/actions/cache/blob/v4/restore/action.yml).
