# Manasvi learning studio

Recreated first milestone of the IGCSE AI Tutor: a local, single-learner development application. Practice and resource search work without external credentials. AI conversation requires a separately billed OpenAI API key configured privately on the server.

The interface currently runs only inside the cloud development machine. A loopback address on that machine does not open the app on a parent’s computer. No public website is deployed.

## Run (on the development machine)

```sh
cd /workspace/IGCSE_Manasvi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app tutor:create_app run --host 127.0.0.1 --port 5000
```

Use the browser interface to upload an authorised PDF or UTF-8 text document with subject, board, specification, topic, type, year, source and permission metadata. Search extracts indexed passages with page references. Scanned PDFs need OCR first; uploads are limited to 10 MB and 300 pages. Only extracted text and metadata are retained, not original files.

Begin on the home screen and choose English Literature or English Language. Guided subject pages link to topic practice, subject-filtered resources and the Literature poetry notebooks. The bank contains 21 original English examples and seven mathematics examples. Nine-category poetry notes persist separately for each supplied poem. Select a subject, topic, difficulty and duration; submit answers to save results and review guidance. Definite-answer items receive automatic marks; essays remain awaiting human review with no mark assigned and are excluded from automatic totals. No human-review marking workflow is implemented. Literature and Language now have model-backed conversation routes; an API key and successful live connection are still required. Questions and marking are not official board assessments. The countdown auto-submits while the page remains open; answers are not autosaved. The server enforces the deadline with five seconds of transport grace; late automatic responses receive zero marks, while extended responses are retained as late work for review.

```sh
.venv/bin/python -m pytest -q
```

Data and the local session key live in ignored `instance/`; back up that directory for local persistence. Keep the development server bound to loopback. Local mode has no login by default and must stay bound to loopback. Render mode requires a private family passphrase before startup; it still has no separate parent/student accounts. Durable storage, retention/deletion tooling and stronger identity controls are required before relying on it for retained student work.

See [architecture and phased delivery](docs/architecture.md). No scraping or cloud-drive syncing is implemented. AI conversation sends messages and explicitly approved document excerpts to OpenAI only when configured and invoked. Uploads default to search-only; AI permission is a separate opt-in.

Project coordination across conversations is tracked in [PROJECT.md](PROJECT.md).

English capabilities were recreated from the supplied handoffs because the other chat’s source ZIP was unavailable. Validation: 14 automated tests and six local HTTP entry points passed. No browser automation was performed.

## Hosted family preview

Render deployment settings, passphrase setup, free-hosting data-loss limits and verification are documented in [docs/render-deployment.md](docs/render-deployment.md). Gunicorn is included. The app refuses to boot on Render without `TUTOR_PASSWORD` (at least 16 characters). Set its value securely in Render, never in source or chat. There is no deployed website verified yet. The current suite has 19 passing tests.

## AI tutor connection

Subject cards now open AI tutoring conversations. See [docs/ai-tutor.md](docs/ai-tutor.md) to connect `TUTOR_MODEL_API_KEY` in Render and verify the first real reply. Without a key, the tutor shows a setup state. Model integration is tested with simulated responses; live API behaviour is not yet verified. The latest suite contains 37 tests. The default model is `gpt-4.1-mini`; API usage is billed separately from ChatGPT subscriptions.

## Check answers against a scheme

Use Mark schemes to register an exact paper/question against a permitted upload, then choose Check answer in the tutor. The score is provisional, supported by scheme-page references, and kept separate from automatic practice results. Missing, mismatched or unassessable rubrics receive no score. See [docs/mark-scheme-assessment.md](docs/mark-scheme-assessment.md). The current suite has 57 passing tests using simulated model responses; official online currency and real AI marking remain unverified.

## Explanation videos

Videos supports public YouTube metadata lookup, explicit parent/teacher review, exact-question links and opt-in embedded playback with a fallback link. Only sufficiently reviewed entries become recommendations; no real videos are seeded or vetted yet. See [docs/video-recommendations.md](docs/video-recommendations.md). The current suite has 67 tests with simulated provider responses. Cloud research remains blocked until the pending network change is applied.
