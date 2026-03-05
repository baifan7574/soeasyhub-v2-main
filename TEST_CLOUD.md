# Cloud Production Test Guide

## 1. Local Pre-flight Check
Before pushing to GitHub, run the configuration test locally:

```bash
cd soeasyhub-v2
python test_config.py
```

Ensure all keys show as `***` or partial values, and you see "Configuration Validated".

## 2. Triggering Cloud Build
You have two options to run the production pipeline:

### Option A: Scheduled (Automatic)
The system is configured to run every 2 hours automatically.

### Option B: Manual Trigger (Immediate)
1. Go to your GitHub Repository -> **Actions** tab.
2. Select **Matrix Factory & GSC Tools** on the left.
3. Click **Run workflow** dropdown on the right.
4. Select `production` from the **Task to run** list.
5. Click **Run workflow**.

## 3. Monitoring
- Click on the active workflow run to see live logs.
- **Phase 1 (Matrix Scout)** will show keyword mining progress.
- **Phase 3-5** (Refiner, Composer, Reporter) are grouped in the second job `Refine, Deploy, and Commit`.

## 4. Verification
After the workflow completes:
1. Check the **Artifacts** section of the run for `production-assets` (zip file containing generated PDFs/reports).
2. Visit `https://soeasyhub.com` to see if new content is live (Cloudflare Worker deployment).
