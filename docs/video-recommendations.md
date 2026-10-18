# Question-specific YouTube explanations

## Implemented capability

The Videos library checks a supplied public video URL through YouTube's oEmbed metadata endpoint, records its title/channel and optional section timestamps, and keeps it a candidate until a parent/teacher teaching-quality review is recorded. No real videos are seeded, endorsed or claimed reviewed in this repository.

A candidate can be linked during registration to a practice question and/or a registered mark-scheme question of the same subject. Reviewed recommendations appear on subject study pages, after submission of the linked practice question, and alongside AI feedback for the linked scheme question. Exact question mapping is explicit, not guessed from channel popularity. Ordinary chat includes a video-library link; the model does not watch videos or invent YouTube links.

The registry supports multiple database links per video, but the current authoring form attaches one practice question and one rubric question when creating a candidate. Editing/expanding existing mappings is not yet provided in the interface. A duplicate URL for the same subject is rejected without another metadata request.

## What counts as a useful review?

Review the relevant segment directly or use an authorised transcript and credible independent evidence. Check:

- **Accuracy:** quotations, interpretations, methods and worked examples against reliable source material. Reject invented quotations and unsupported examiner/grade claims.
- **Question relevance:** the exact concept, learning need or misconception, including the text/poem and question actually being studied. Record why the chosen segment helps.
- **Clarity:** an understandable explanation, useful examples and appropriate pace, leading back to an independent attempt rather than copying an answer.
- **Examination fit:** verify the specification and route when recommending exam technique. A concept explanation from another board can still be useful if labelled accordingly; it must not be presented as verified Edexcel examination guidance.
- **Evidence quality:** prioritise substantive named-teacher reviews and checkable learning outcomes. Creator promotion, view counts, likes, subscriber counts and anonymous positive comments are insufficient on their own. Record the review source and limitations rather than calling a video the best on those signals.
- **Applicability and availability:** inspect dates/edition claims where relevant, any meaningful criticism, section timestamps, caption accessibility and embedding availability. Newer publication alone does not establish higher quality; old conceptual explanations can remain useful.

The form records a reviewer name/role, an explicit watched-video confirmation, four 1–5 criteria, strengths/limitations, scope and an optional independent-review URL. These are user-declared observations, not automatically authenticated expertise or a peer-reviewed rating. No external review or comment is automatically fetched or verified. Without direct viewing, retain candidate status rather than claiming the video has been checked.

A concept recommendation needs accuracy, relevance and clarity ≥4. An exam-specific recommendation additionally needs alignment ≥4 and the applicable specification; it must match every linked rubric's specification. These are transparent curation heuristics, not an empirically validated quality score. Ranking weights accuracy, relevance and clarity; views and likes are never inputs.

## Embedding and copyright

Only validated HTTPS YouTube video IDs are accepted, not playlists, arbitrary iframe markup or external media hosts. oEmbed's HTML is never inserted into a page. The player URL is constructed from the validated ID and optional start/end seconds.

The watch page initially has no iframe. Load YouTube player explicitly requests a privacy-enhanced `www.youtube-nocookie.com` iframe; playback is not autoplayed. The browser connects to YouTube after this action. The iframe has an appropriate referrer policy and a narrowly scoped content-security-policy host. A normal Watch on YouTube link remains available if an uploader, region or account requirement blocks embedding. oEmbed availability does not guarantee that actual playback will work everywhere.

No audio, video, comments or captions are downloaded, rehosted or sent to the AI. No authentication, age gate or embedding restriction is bypassed. Provider/platform terms and uploader rights still apply. Video metadata and reviews are not automatically tutoring-source text, and the AI must not claim it has viewed the video.

## Research and configuration status — 19 October 2026 (Singapore)

The inspected running cloud policy still allows OneDrive and package-manager presets only. Pearson's domain was already in the pending draft. This change adds `www.youtube.com`, `youtube.com` and `www.youtube-nocookie.com` to that same draft, preserving the existing OneDrive/Pearson entries. Saving a draft does not enable current research; the parent must finish review and save/publish in the Codex Environment page.

No public YouTube video, independent review, comment set, transcript or classroom claim has been inspected by this task. There are no verified real recommendations yet. After policy application, begin with the specific English topics already prioritised: Mrs Birling/gender/responsibility, the supplied poetry framework and Language inference/analytical writing. Check metadata, accessible source material and credible reviewer evidence; do not infer teaching quality from oEmbed metadata. Direct content verification still requires actual viewing or an authorised accessible transcript; network access alone does not provide that capability.

The web app's metadata lookup runs on the configured server when a signed-in parent supplies a URL. Research in this Codex environment follows its own network policy. Do not use the deployed app as a proxy to circumvent cloud egress restrictions.

## Validation and remaining limits

67 automated tests pass. Added coverage includes strict URL validation, safe metadata parsing, errors without false verification, candidate/recommendation gates, weak-review exclusion, subject and route matching, explicit iframe loading, safe iframe construction, fallback links, exact-question post-submission recommendations and scheme-feedback recommendations. YouTube calls are simulated. No real metadata lookup, browser playback, independent-review research or calibrated recommendation quality is claimed.

The service remains a shared family preview without separate reviewer/student roles. Free-hosting data loss applies to the registry and reviews too. Persistent storage, scheduled rechecks and richer curation remain subsequent work.
