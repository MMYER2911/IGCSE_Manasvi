# Render family-preview deployment

Deployment is prepared in source, not automatically created or verified on Render. The first deployment is a temporary demonstration. Free Render compute has no persistent disk: uploads, notes, session keys and assessment results in SQLite may disappear on restarts/redeployments. Keep original documents elsewhere and do not rely on this preview for retained schoolwork. A paid instance alone does not persist data; durable storage must be explicitly configured and verified before real use.

## Configuration

- Repository: MMYER2911/IGCSE_Manasvi
- Branch: codex/consolidated-learning-studio
- Language: Python 3
- Root Directory: empty
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 60 'tutor:create_app()'`
- Compute: Free ($0/month) for the demonstration; do not select paid services without the parent's decision.
- Health Check Path, if the settings expose it: `/health`
- Environment variable: `TUTOR_PASSWORD` — a private passphrase of at least 16 characters, supplied directly in Render. Never paste it into chat, screenshots or Git. The app detects Render via its `RENDER=true` runtime variable and refuses to start without the passphrase.

Render supplies PORT. Do not add a hard-coded PORT. Keep the factory call and single worker as written: the preview's bounded login limiter and authentication version are process-local. The Flask development server is not used for this deployment. TLS terminates at Render; hosted session cookies use Secure, HttpOnly and SameSite=Lax.

## Access and limits

The shared passphrase protects application routes, including the library, notebooks, practice and results. Login and static assets are public. `/health` is public and returns a status only. Login requires a CSRF token and allows five attempts per connected peer per minute in the single process. Sign-out requires POST with a CSRF token. No raw password is saved in files; the configured passphrase is hashed in process. Authentication expires after 12 hours or process restart. Password changes take effect after restart and invalidate old login sessions.

This is shared family-preview access, not separate learner/parent accounts, SSO, password recovery or a fully hardened multi-user service. Model-backed tutoring is now implemented but needs its own API key and live verification; see ai-tutor.md. Drive syncing and semantic embedding retrieval remain absent.

`TUTOR_DATA_DIR` can optionally point to an explicitly provisioned persistent mount when a later storage decision is made. It stores the database and session key together. Do not point it outside an authorised mount or assume setting it creates a disk. Existing data needs a deliberate backup/migration; changing the path does not copy it.

## Verification

Nineteen automated tests cover the learning workflow, schema upgrades, private-route protection, CSRF, authentication/logout, cookie flags, login throttling, fail-closed hosted startup and configurable data directory. A separate Gunicorn hosted-mode smoke check uses generated throwaway credentials and temporary storage to verify health, private redirects and the login page. This verifies the production command locally, not the Render service.

After the parent starts deployment, inspect actual build/deploy logs. Verify `/health`, the unauthenticated redirect to login, correct/wrong passphrase behaviour, both English modules and a disposable practice session. Do not claim deployment, durable storage or parent-device access until those checks are observed.

## Subsequent AI connection

Keep `TUTOR_PASSWORD` for website access. `TUTOR_MODEL_API_KEY` separately connects the model; these are different secrets and should never be interchanged. After setting a valid key and saving/redeploying, verify one genuine tutor reply. Existing resources remain search-only until explicit permission for AI excerpts is enabled.
