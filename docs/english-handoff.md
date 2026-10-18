# English conversation handoff

Source: parent-provided summary pasted into the consolidation conversation. Requirements accepted into PROJECT.md; implementation claims remain unverified until code is available.

## Reported additions

| Capability | Handoff report | Consolidation workspace |
| --- | --- | --- |
| Foundation | Existing Flask/SQLite app extended | Same foundation present |
| Literature and Language | Separate study modules and future agent instructions | Not present |
| Question bank | 21 original English questions plus seven maths examples | Seven maths examples present |
| Resource search | Subject-filtered lexical search with page citations | Page-referenced search present; subject filter absent |
| Practice | Subject/topic/difficulty/duration filters | Filters present; only mathematics seeded |
| Reporting | Subject-level scores and saved answers | Mathematics results and answers present |
| Poetry notebooks | Persistent fields for all nine framework categories | Not present |
| Extended responses | Model guidance, checklists and human-review state | Not present |
| Validation | Eleven automated tests pass; no browser automation | Six-test suite present; English test files absent |

The reported local path is `/workspace/IGCSE_Manasvi`. An identical path in another chat does not prove the machines or files are shared. No branch or commit identifying the English additions was supplied. The available local origin/main reference contains only an initial README.

## Agreed limitations and roadmap

The handoff describes guided study modules, not live AI agents, and lexical retrieval, not full RAG. It bundles neither official papers nor copyrighted full texts. It remains a single-local-learner prototype without production authentication or separate parent accounts.

The proposed later phases agree with the existing roadmap: identity and permissions; cited live subject tutoring; scoped drive/OneNote connectors; compliant official-board resource discovery; board-specific practice and mocks; provisional rubric-based AI marking with review; adaptive topic mastery and study plans; evidence-based parent reporting. The Year 10-only OneDrive restriction remains in force for all integrations.

## Code handoff needed

Supply a repository branch/commit containing the changes, or attach an archive of application source, tests, dependency declarations and documentation. Exclude `.venv`, `instance/`, databases, session keys, credentials, caches and uploaded school documents. Keep the originals until integration is verified.

## Integration checks once code arrives

1. Preserve both implementations and compare routes, schemas, templates, seed logic and dependency changes before editing.
2. Reconcile any schema changes without deleting local data. Verify existing databases gain English questions rather than relying on an empty-table seed condition.
3. Confirm Literature and Language filtering, question provenance, and subject labels in practice and results.
4. Check that essay responses persist in an awaiting-review state and never enter automatic-score denominators before review.
5. Verify all nine poetry fields persist and remain separate by poem; escape notebook text in rendered pages.
6. Run the combined tests, including the reported additional English tests, and verify representative practice, notebook and results flows. Report actual test counts.

## Pending materials and details

The later study-coach handoff identifies Pearson Edexcel as the working board and 4ET1 as the provisional Literature specification. Exam year/route, anthology edition, Language A (4EA1) versus B (4EB1), and examination date remain unconfirmed. The June 2022 paper, booklet pages 7 and 10, and other authorised school materials were not attached. The gender organiser was reportedly reviewed in that separate conversation but its file is unavailable here. Official links are now recorded in study-coach-handoff.md; supplementary parent resource URLs remain unavailable.

## Subsequent recreation

The original source archive could not be transferred. Rather than requiring more file-transfer steps from the parent, the described English capabilities were recreated in this workspace from the handoff requirements. There are now 21 newly authored English examples, guided Literature/Language modules, persistent nine-category poetry notebooks, subject-filtered search and explicit human-review responses. Fourteen tests and six local HTTP page checks pass. This is not a verified import or a claim that the new questions match the original ones. Source recovery is no longer a prerequisite for this milestone; the original inventory above remains historical provenance.
