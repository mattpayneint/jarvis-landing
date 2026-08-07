# Matthew Payne Consulting — VSL Landing Pages

Three vertical-specific landing pages driving Meta/Instagram ad traffic to the VSL, feeding each vertical's Calendly link. Built 2026-08-07. An opt-in gate (`optin.html`) sits in front of them, added 2026-08-08.

- `optin.html` — email-capture gate. Ads should point here first, not directly at the vertical pages — decided 2026-08-08 that email must be captured *before* video access (not at booking) so the behavioral follow-up sequence can reach people who watch part of the VSL but never book. One vertical-aware template, not three separate files — pass `?v=vc`, `?v=advisor`, or `?v=attorney` on the ad's destination URL to swap headline copy and the post-submit redirect target. Defaults to `vc` if the param is missing.
- `vc.html` — Fund Managers / General Partners
- `advisor.html` — Financial Advisors / Wealth Managers
- `attorney.html` — Estate & Wealth-Focused Attorneys

## Before going live
1. Replace `PIXEL_ID` in each page's Meta Pixel script (including `optin.html`) with the real Pixel ID once the ad account exists.
2. Replace the video placeholder `<div class="placeholder">` with the real YouTube `<iframe>` embed (commented example already in each file) once the VSL is uploaded.
3. Replace `OPTIN_WEBHOOK_URL` in `optin.html` with the real n8n webhook URL once the email-capture workflow is built (see `project_infusionsoft_keap_audit_2026-08-07.md` / `project_meta_ads_media_buyer_2026-08-07.md` in Jarvis's memory — this is the still-unbuilt n8n rebuild of the old Keap nurture sequence).
4. Point ad destination URLs at `optin.html?v=<vertical>`, not the vertical pages directly.
5. Point a subdomain (e.g. `go.matthewpayneconsulting.com`) at GitHub Pages via CNAME, or use the default `*.github.io` URL.

See `/Users/matthewpayne/jarvis/ADS-STRATEGY.md` for the full ad strategy this supports.
