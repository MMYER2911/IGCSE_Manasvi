# Mark-scheme-based assessment

## Delivered workflow

The Mark schemes page lets a parent/teacher register an exact question against an authorised, AI-approved uploaded Pearson scheme. The AI tutor has separate Study chat (qualitative feedback) and Check answer modes. Check answer requires an explicit registered question, not a guess based on the student's answer or text-search relevance.

Matching records retain subject, board, specification, component/variant, year, examination session, question number, exact question wording, maximum marks, selected PDF pages and the parent/teacher confirmation time. A component with a different specification prefix is rejected. Language A/B rubrics remain distinct; selecting a rubric does not establish that the student's overall course route has been confirmed.

## How to use

1. In Resources upload a scheme you have permission to use, with type Mark scheme, subject English Literature/English Language, board Pearson Edexcel, specification 4ET1/4EA1/4EB1, a four-digit year and its original HTTPS URL on qualifications.pearson.com. Enable AI excerpts only if permissions allow sending the content to the provider.
2. Open Mark schemes. Register one exact question with the component, session, wording, maximum marks and all applicable rubric pages. Include relevant general principles and level descriptors as well as question-specific guidance. PDF page numbers may differ from printed page numbers. Example selection syntax: `1, 8-9`.
3. Confirm the printed identifiers and complete rubric against the paper and scheme. This is a parent/teacher assertion; the shared family preview does not authenticate a distinct teacher role or independently certify the document.
4. In the subject tutor choose Check answer, select the registered question and paste the student's answer. The selected question wording is shown so the task is explicit.
5. The model receives the selected question and all selected scheme chunks, without unrelated schemes or earlier chat history. It returns structured assessment data. Validated results show a provisional mark, justification, strength, priority improvement, revision task and scheme-page references. A teacher can review these; they are not official examiner marks.

The source-host check establishes only that the declared URL uses the expected host, not that the uploaded file genuinely came from that URL. Parent/teacher confirmation and licensing are still prerequisites. No official schemes are bundled as fixtures; tests use explicitly original synthetic rubric text.

## Which version applies?

The most recently published exam paper's scheme is not automatically the right scheme. For a June 2022 paper use the exact June 2022 component/variant scheme, incorporating any verified later correction to that same scheme. For current exam preparation, separately check the specification/assessment objectives and any applicable board updates for the learner's exam series and route. Never substitute a newer exam year's indicative content or grade boundaries for an older question.

An internet-informed catalogue should record the official source, issue/revision, applicability and actual verification date, then recheck board updates. This preview does not yet perform automatic web discovery, scheduled refreshes or verified edition comparison. It does not claim that a registered upload is the latest scheme. All current entries are labelled parent/teacher-confirmed with online currency unverified.

## Research status: 19 October 2026 (Singapore)

The enforced cloud network policy still permits OneDrive and package-manager presets but not qualifications.pearson.com. The previously saved configuration draft does include the Pearson domain; it has not reached the running policy. The earlier official-page request was denied by the network proxy. With no meaningful network state change, that unchanged request was not repeated.

Official candidate specification and sample-assessment URLs are listed in reference-library.md from the other conversation's handoff. They have not been independently fetched here. Current official mark schemes, examiner reports, errata, specification issues and the latest public series remain unverified. Do not infer publication dates or current status from filenames or model memory.

To resume research, apply the pending Pearson domain change in the Codex cloud Environment page using Save draft and Publish. This is separate from Render's Environment variables. Recheck runtime policy and make a read-only official-site request after the change. Respect authentication, access restrictions, terms and copyright; do not obtain locked recent papers by bypassing access controls. Researching a public document does not itself authorise copying it or sending it to a model.

## Guardrails and limits

- Missing/wrong-subject/revoked rubrics never call the marking model or assign a score.
- The complete selected page set must have indexed text. More than 12 pages or 16000 characters is rejected with an explanation, not silently truncated. An authorised focused extract can be used if it retains every applicable rule.
- The model must declare whether the supplied rubric is assessable. If incomplete it returns no mark; the server rejects a score for an unassessable response.
- Server validation requires an integer score between zero and the registered maximum, the same maximum allocation, complete feedback fields and actual selected-source labels for marked responses. Unknown source labels, out-of-range marks and malformed assessments are not stored as successful assessments.
- AI marks are saved with a task-identity snapshot in the conversation, separately from deterministic practice results. They do not silently change the existing assessment scores or close human-review tasks.
- Study chat is instructed to avoid numerical marks and direct marking requests to Check answer mode. As with all model instructions, factual compliance still needs evaluation; this is not a guarantee that every generated sentence is correct.
- API assessments request strict JSON schema and up to 1000 output tokens; model compatibility, billing and live access must be verified with the configured account. Real model quality/calibration and semantic correctness of citations have not been evaluated.
- Free Render storage can reset across redeployments, including registered schemes and marks. Do not rely on it as durable assessment storage.

## Validation

57 automated tests pass. Added checks cover exact component/session/question registration, confirmation, page completeness, nontruncation, subject/access filters, pinned older-paper schemes, unassessable responses, bounds/types/maximum validation, required scheme references, stored task snapshots, duplicate submissions and structured API request shape. Providers are simulated; no live AI marking or internet verification is claimed. Existing tests cover private access, uploads, study practice, history and notebooks.
