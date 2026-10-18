# AI tutoring: implementation and connection

## What changed

Literature and Language now have real chat workflows backed by a server-side OpenAI Responses API adapter. Home-screen subject cards lead to the chat. Study priorities, practice and notebooks remain separate features. This adds model integration code; it does not create an API credential, establish billing or prove a live provider response has succeeded.

No usable model key is configured in the inspected cloud environment. The Render configuration is not readable from this workspace. Until a valid key is configured on Render and a reply succeeds, the honest status is **implemented and tested with simulated provider responses; live AI connection unverified**. A missing key produces a visible setup state and disables sending, rather than pretending a scripted starter is an AI reply.

## Parent setup on Render

1. Use an OpenAI API account with billing and access to the selected model. ChatGPT subscriptions do not include API usage. Manage API budgets in the provider account.
2. In the existing Render service's Environment settings, check whether `TUTOR_MODEL_API_KEY` or `OPENAI_API_KEY` already exists. Reuse a working binding; do not create duplicates. The app prefers `TUTOR_MODEL_API_KEY` and accepts `OPENAI_API_KEY` as a fallback.
3. If absent, add `TUTOR_MODEL_API_KEY` and enter the key privately in Render. Never put it in chat, source code, screenshots or a browser-side script. Keep the existing `TUTOR_PASSWORD` unchanged.
4. Save and redeploy. The model defaults to `gpt-4.1-mini`; optional `TUTOR_MODEL` selects another Responses-compatible model that accepts the configured output-token limit.
5. Open the website, sign in and choose an English subject. Send one short message. Verify a generated reply and an interactive follow-up before claiming AI works. If auth, billing, quota or connectivity fails, the UI reports the problem without exposing provider error bodies.

API use is separate from Render hosting. It is incurred when sending messages, not when opening the page. No API charges have been incurred by the test suite. Actual model availability, output quality, latency and charges have not been verified without a key.

## Subject tutor behaviour

Each subject has its own persistent conversation, with the latest conversation resumed after sign-in in this single-family app. All users of the shared passphrase can access the same learner's work. A new-conversation action starts a separate thread; it does not delete old records. Recent successful turns provide bounded conversational context, not unlimited memory or a full adaptive study model.

Instructions preserve the consolidated teaching approach: one focused question, hints first, recall/practice/feedback/revision, supported interpretations, no invented quotations or official questions, original practice labels, and provisional AI marks only when an appropriate rubric is available. Literature uses the supplied texts/poems and 4ET1 working basis; Language A/B remains unresolved. AI conversation does not write automatic assessment scores or silently mark essays as complete.

## Retrieval and document permission

- Existing and newly uploaded documents default to **search only**. Upload/index permission is not treated as permission to transmit text externally.
- The parent can enable AI excerpts in an upload or on a library card by explicitly confirming permission to share relevant excerpts with OpenAI. It can be disabled again without deleting local search data.
- When the student sends a message, FTS5 retrieves up to four matching chunks from the exact subject and only AI-approved documents. A prior question helps resolve short follow-ups. School files, cloud-drive folders and web pages absent from this database are not silently accessed.
- Instructions and API input include bounded excerpts, titles and page references. Raw source URLs and declared licence text are not sent as source metadata. The user's message and recent successful conversation turns are sent to OpenAI.
- Replies identify cited excerpts with stable chunk labels such as `[S1]`; the UI shows the actual stored title, page, source and excerpt. Unknown citation labels are rejected. This checks citation identity, not semantic entailment or every factual claim.
- If a reply cites no uploaded source, the UI labels it general study guidance. It does not claim to be grounded in school notes. Documents are untrusted reference data, not instructions overriding tutor behaviour.
- Disabling AI excerpts prevents new retrieval and suppresses earlier turns that cited the document from future model context. Prior local replies remain visible; revocation does not recall material already processed by the provider.

This is lexical retrieval-augmented tutoring, not semantic embedding search or live web browsing. Public reference catalogue links have not automatically been indexed. OneDrive sync remains absent and any future access remains restricted to Year 10 and descendants.

## Reliability and storage

Messages are limited to 3000 characters; API output to 700 tokens; provider socket timeout to 25 seconds. The provider request uses `store:false`, which disables Responses object storage, not all provider retention. Consult provider data terms for the applicable account. The app does not add credentials to the browser or include provider failure bodies in responses/logs.

Before calling the API, a unique request token reserves the turn in SQLite. A duplicate form submission cannot invoke the model twice. Concurrent requests in the same conversation are blocked; abandoned pending turns expire after 90 seconds. A shared limit of ten new turns per minute bounds bursts across this single-family preview. Failed turns do not enter future model context. Calls have no automatic retries; a user-initiated new attempt can incur another API charge.

Conversations, citations and permission flags live in the same SQLite data directory. They can be lost on Render Free restarts/redeployments. Durable storage, separate parent/learner identities, retention/deletion controls and model-quality evaluation remain necessary before relying on the service for retained student work.

## Validation

The automated suite checks source/subject permission filters, cited reply persistence, history/resume, duplicate requests, failures, invalid citations, output escaping, revocation, separate subject threads, new-conversation/CSRF behaviour, input/concurrency/burst limits, explicit missing-key handling and request/response/error handling for the OpenAI adapter. Provider transport is simulated: no real model, credential or paid API call is used. Existing assessment/login/upload tests remain included.

An actual Render model reply, factual/citation quality evaluation and full browser tutoring flow remain unverified until configuration and functional testing.

## Subsequent exact-scheme assessment

Check answer mode now supplies an explicitly registered paper/question and complete rubric page selection, requests structured output and validates provisional marks before recording them. Study chat remains qualitative. See mark-scheme-assessment.md for workflow, metadata confirmation, score validation and the still-blocked official internet verification. No live AI assessment is claimed.
