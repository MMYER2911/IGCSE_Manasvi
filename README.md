# Manasvi learning studio

Recreated first milestone of the IGCSE AI Tutor: a local, single-learner development application. No external AI service or credentials required.

The interface currently runs only inside the cloud development machine. A loopback address on that machine does not open the app on a parent’s computer. No public website is deployed.

## Run (on the development machine)

```sh
cd /workspace/IGCSE_Manasvi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app tutor:create_app run --host 127.0.0.1 --port 5000
```

Use the browser interface to upload an authorised PDF or UTF-8 text document with subject, board, specification, topic, type, year, source and permission metadata. Search extracts indexed passages with page references. Scanned PDFs need OCR first; uploads are limited to 10 MB and 300 pages. Only extracted text and metadata are retained, not original files.

Begin on the home screen and choose English Literature or English Language. Guided subject pages link to topic practice, subject-filtered resources and the Literature poetry notebooks. The bank contains 21 original English examples and seven mathematics examples. Nine-category poetry notes persist separately for each supplied poem. Select a subject, topic, difficulty and duration; submit answers to save results and review guidance. Definite-answer items receive automatic marks; essays remain awaiting human review with no mark assigned and are excluded from automatic totals. No human-review marking workflow or live AI conversation is implemented. Questions and marking are not official board assessments. The countdown auto-submits while the page remains open; answers are not autosaved. The server enforces the deadline with five seconds of transport grace; late automatic responses receive zero marks, while extended responses are retained as late work for review.

```sh
.venv/bin/python -m pytest -q
```

Data and the local session key live in ignored `instance/`; back up that directory for local persistence. Keep the development server bound to loopback. This prototype has no user authentication or parent/student isolation and must not be deployed for real student data. Access control, retention/deletion tooling and production deployment are required before multi-user use.

See [architecture and phased delivery](docs/architecture.md). No scraping, AI generation, cloud-drive connection or external document transmission happens in this milestone.

Project coordination across conversations is tracked in [PROJECT.md](PROJECT.md).

English capabilities were recreated from the supplied handoffs because the other chat’s source ZIP was unavailable. Validation: 14 automated tests and six local HTTP entry points passed. No browser automation was performed.
