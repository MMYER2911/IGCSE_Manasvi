# Manasvi IGCSE preparation — shared project record

This repository is the shared project home for work from three conversations. Both other handoffs have now been received and their requirements reconciled here. The cloud-environment prototype is present locally. The English source ZIP could not be transferred from the other conversation. Its described capabilities have now been recreated here from the supplied requirements, rather than imported. Requirements consolidation and the recreated local milestone are complete; original-source equivalence and public deployment are not claimed.

## Goal and delivery order

Build a modular IGCSE learning assistant for Manasvi with a central learning library, source-grounded tutoring, authorised past-paper discovery, practice assessments, board-specific mock examinations, adaptive revision and parent reporting.

The first milestone prioritises document upload and indexing, a subject-specific question bank, interactive examination practice and recorded results. Advanced adaptive learning and full mocks follow later. See docs/architecture.md for the detailed capability roadmap and README.md for local operation.

The tutoring design uses a coordinator with a specialist subject agent for each subject, starting with English Literature and English Language. Guided subject study pages now exist; live AI tutor agents remain components to develop. Retain the mathematics examples as development fixtures while prioritising English. The English handoff uses the same Flask/SQLite stack, so no stack migration is required by the information received so far.

## One project, two complementary interfaces

Use **IGCSE Study Coach** as the learning-project name and `MMYER2911/IGCSE_Manasvi` as the code repository. The ChatGPT Project proposed in the third conversation provides the coordinator and separate subject tutor chats; the Flask prototype provides resource indexing, practice and stored results. They follow the same curriculum, teaching rules and roadmap. There is no automatic synchronisation, shared memory or running agent orchestration between them. A ChatGPT Project and persistent tutors have not been created by this workspace.

Reusable instructions are in docs/study-coach-instructions.md and the starter plan/session log template in docs/study-plan.md. These files are configuration drafts for use in the chosen interface, not proof of deployed tutors. Continue coordination in this conversation and avoid further independent development in the other chats while their changes are recovered.

## Working course details

- Board: Pearson Edexcel International GCSE, supplied in the third handoff.
- English Literature: 4ET1 is the working basis; exam year and examination/coursework route remain unconfirmed.
- English Language: A (4EA1) versus B (4EB1) remains unconfirmed. Start with shared reading and writing skills; do not assign route-specific papers or marks yet.
- Anthology: the handoff reports a 16-poem prescribed anthology and identifies Telephone Conversation as supplementary. Preserve all nine parent-supplied poems. Verify the applicable edition and school coverage before treating that list or the reported anthology mapping as authoritative.
- Exam date remains unconfirmed. Do not block general study or code recovery on these missing details or repeatedly ask for them.

## English requirements received

- Set texts: An Inspector Calls, Of Mice and Men, Macbeth.
- Poems: La Belle Dame sans Merci; The Tyger; Telephone Conversation; Do not go gentle into that good night; Poem at Thirty-Nine; If—; Piano; Sonnet 116; Remember.
- Poetry notebook framework: meaning/themes, language, imagery, structure, form, speaker, mood/atmosphere, personal response, and links to other poems.
- Teacher tasks: ten key quotations for An Inspector Calls; Mrs Birling knowledge organiser; June 2022 questions 1–3; homework-booklet assignments, including pages 7 and 10. The exact paper and booklet are unavailable; do not infer their contents.
- Keep Literature and Language study modules separate and route both through the coordinator. Use authorised resources and citations when live retrieval is implemented.
- Automatically mark definite-answer questions. Save essays as awaiting human review and exclude them from automatic-score denominators; do not treat unreviewed work as zero marks. Model guidance and review checklists are distinct from awarded marks. Later AI-assigned marks must be provisional.
- Use the working course details above and confirm the remaining route, edition and examination details before claiming full examination alignment. These details do not block recovering and integrating the prototype code.

The original English handoff reported 21 original English questions, poetry notebooks, subject-filtered resource search, subject-level results and eleven tests. Those original files were unavailable. This workspace now has a separate recreation: 21 newly authored English questions, nine-category notebooks, subject-filtered search, subject-labelled results and explicit human-review states. Fourteen tests pass here; this does not validate the other chat’s source. No original source links or school attachments accompanied the handoff. See docs/english-handoff.md for the implementation inventory and merge checks.

The study-coach handoff reports review of `Knowledge Organiser - Gender - Inspector Calls.docx` in its own conversation. The document itself is not attached here. Its reported coverage includes gender, patriarchy, class, characters, quotations, dramatic methods and context. Use the summary as planning context only; verify quotation wording and act references against the play before memorisation. Official Pearson URLs supplied in that handoff are recorded in docs/study-coach-handoff.md; their verification was reported there, not independently repeated here. Supplementary poem resource URLs have not been supplied.

## Current implementation

- Python Flask, SQLite and FTS5; server-rendered HTML/CSS/JavaScript.
- PDF/selectable-text and UTF-8 text extraction, document metadata and page-referenced search.
- Seven original mathematics examples plus 21 recreated original English questions (15 Literature, six Language); subject/topic/difficulty/duration filters.
- Timed submissions, deterministic definite-answer marking, answer explanations and persisted results. Essays are stored as awaiting human review with null marks and excluded from automatic totals.
- Separate Literature/Language study pages, nine-category persistent poetry notebooks and subject-filtered resource retrieval.
- Additive SQLite upgrades preserve existing mathematics records and install new examples idempotently.
- Fourteen automated tests passed after recreation; six local HTTP routes were verified (home, Literature, Language, poetry, practice and resources). No browser automation was performed.
- Local single-learner prototype. Authentication, parent access, AI tutoring/RAG, official-paper discovery, cloud-drive integration, rubric-based essay marking, full mocks and adaptive recommendations are not implemented.

At consolidation inspection, the application files were untracked and the local Git branch had no commits. Files in this workspace are not evidence of a GitHub push or of a published cloud snapshot. Preserve existing work when reconciling other branches or copies.

The available local `origin/main` reference contains only an initial README commit (`1b986ee`). It does not contain the English implementation. This is a local reference inspection, not a fresh remote fetch.

## Learning-material scope

The user identified `C:\Users\Munish Myer\OneDrive\Personal\Manasvi\Year 10` as the source folder and supplied its OneDrive sharing link in this conversation. That Windows path is not accessible from this cloud machine.

Access is authorised only to the linked Year 10 folder and its descendants. Do not enumerate or import other OneDrive folders or account roots. Keep the sharing link out of public repository files and logs. Respect permission and licensing restrictions. Do not broaden the folder's sharing settings to make access work.

The last attempted link request failed at the cloud network proxy before OneDrive access could be assessed. Additions for `1drv.ms` and `onedrive.live.com` were saved in the environment draft; publication and successful folder access were not verified. No OneDrive materials have been downloaded or indexed by this conversation.

## Reconcile the other conversations

For each other conversation obtain:

1. Its requirements, decisions and unanswered questions.
2. Repository, branch and commit identifiers, or attached files if code was not saved remotely.
3. What is implemented versus proposed, tests run and known failures.
4. Technology choices, configuration requirements and external integrations, without secret values.

Compare these with the current prototype before selecting a final stack. Preserve useful work and identify conflicts explicitly. Maintain one requirements/status record and one prioritised roadmap in this repository. Do not claim a merge is complete until the other work is available and verified.

## Immediate next actions

- No further ZIP transfer is required. The recreated English capabilities are now in this workspace; the original source is optional for later comparison.
- Provide one accessible interface through a separate deployment step, with authentication and appropriate private data storage before real student use. The current server is loopback-only inside the cloud environment; it is not a URL the parent can open on their own computer.
- Record the implementation in Git and report remote persistence separately; local files are not evidence of a push.
- Verify access to the specified Year 10 folder before ingestion; do not treat a saved network draft as successful access.

## External reference collection

The parent requested web research for IGCSE resources. Candidate official Pearson references and their verification/access status are recorded in docs/reference-library.md. The initial official-page request was denied by the environment network proxy; a Pearson domain addition was saved to the configuration draft. No current contents or search results were verified, and no linked documents were imported. Resume official-source research after the network configuration is applied.

## Deployment preparation

Render family-preview configuration is in docs/render-deployment.md. Gunicorn and a mandatory hosted-mode shared passphrase gate are implemented; private routes require login, cookie flags and CSRF are enforced, and login attempts are limited in the single worker. Nineteen tests pass. This is not a separate parent/student identity system. No actual Render deployment is yet verified. Free-hosting SQLite data is disposable; durable storage remains a separate prerequisite for retained schoolwork.
