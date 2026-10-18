"""Original English practice and curriculum configuration; no official extracts."""
import json

POEMS = (
    'La Belle Dame sans Merci', 'The Tyger', 'Telephone Conversation',
    'Do not go gentle into that good night', 'Poem at Thirty-Nine',
    'If—', 'Piano', 'Sonnet 116', 'Remember',
)
FRAMEWORK = (
    ('meaning', 'Meaning / themes'), ('language', 'Language'), ('imagery', 'Imagery'),
    ('structure', 'Structure'), ('form', 'Form'), ('speaker', 'Speaker'),
    ('mood', 'Mood / atmosphere'), ('response', 'Personal response'),
    ('connections', 'Links to other poems'),
)
SUBJECTS = {
    'literature': {
        'name': 'English Literature',
        'course': 'Pearson Edexcel · 4ET1 working basis; year and examination/coursework route unconfirmed',
        'intro': 'Explore character, ideas and writers’ choices. Explain your interpretation, then support it with evidence.',
        'tasks': [
            'Build ten verified An Inspector Calls quotation entries: speaker, theme, importance and optional methods.',
            'Create a Mrs Birling knowledge organiser, then write and revise one analytical paragraph.',
            'Study each supplied poem using all nine notebook categories.',
            'Return to June 2022 questions 1–3 and booklet tasks when the exact paper and pages are supplied.',
        ],
        'opening': 'At the beginning of the play, what is one difference between Sheila’s and Mrs Birling’s attitudes towards other women?',
    },
    'language': {
        'name': 'English Language',
        'course': 'Pearson Edexcel · Language A (4EA1) or Language B (4EB1) not yet confirmed',
        'intro': 'Start with shared reading and writing skills. Use a short diagnostic to identify one useful next step.',
        'tasks': [
            'Reading: inference, evidence selection, language and structure.',
            'Writing: audience, purpose, tone, planning and organisation.',
            'Revision: vocabulary, sentence control, spelling and punctuation.',
            'Use route-specific comparison, summary and exam tasks once the course is confirmed.',
        ],
        'opening': 'A school wants to improve its library. Who would read your proposal, and what would you want them to do?',
    },
}


def example(subject, topic, kind, prompt, answer, explanation, options=()):
    return (subject, topic, 'Foundation' if kind == 'multiple_choice' else 'Higher', kind,
            prompt, json.dumps(options), answer, explanation, 1 if kind == 'multiple_choice' else 10,
            0, 'Original tutor-created practice · not an official examination question')


ENGLISH_SEED = [
    example('English Literature', poem, 'essay',
            f'Using your authorised copy of {poem}, explain how one choice of language or imagery develops an idea. Include a precise reference and discuss an alternative interpretation.',
            'No single model answer. A supported interpretation requires review.',
            'Review checklist: clear idea; accurate reference from your copy; analysis of a specific choice; effect on meaning; supported alternative. Do not invent quotations.')
    for poem in POEMS
]
for title, prompt, correct, options, guidance in [
    ('An Inspector Calls', 'Which approach best supports an interpretation of Mrs Birling?',
     'Analyse a verified detail and explain how it supports the interpretation.',
     ['State a judgement without evidence.', 'Analyse a verified detail and explain how it supports the interpretation.', 'List context without linking it to the play.'],
     'A precise reference and explanation connect the writer’s choices to your argument.'),
    ('Of Mice and Men', 'What makes an essay plan about loneliness more useful?',
     'Organising claims with relevant evidence and analysis.',
     ['Retelling every event in order.', 'Organising claims with relevant evidence and analysis.', 'Using unverified quotations.'],
     'Organise the essay around a developing argument; avoid replacing analysis with plot summary.'),
    ('Macbeth', 'How can context strengthen an analytical paragraph?',
     'Connect relevant context to a specific interpretation of the text.',
     ['Add unrelated historical facts.', 'Connect relevant context to a specific interpretation of the text.', 'Use context instead of textual evidence.'],
     'Context is useful when it explains or complicates the textual interpretation.'),
]:
    ENGLISH_SEED.append(example('English Literature', title, 'multiple_choice', prompt, correct, guidance, options))
    ENGLISH_SEED.append(example('English Literature', title, 'essay',
        f'Using your authorised copy of {title}, explain how a character’s attitude reveals a larger theme. Develop one analytical paragraph with accurate evidence.',
        'No single model answer. A supported interpretation requires review.',
        'Review checklist: focused claim; verified evidence; analysis of method; link to theme; coherent explanation. Accept other interpretations supported by the text.'))

for topic, prompt, correct, options, writing in [
    ('Reading skills', 'An original practice sentence reads: “Mira checked the clock for the fifth time.” Which inference is best supported?',
     'She may be anxious about the time.',
     ['She may be anxious about the time.', 'She has definitely missed a train.', 'She dislikes all clocks.'],
     'Write an original opening of 100–150 words in which a character is waiting. Suggest an emotion through details instead of naming it.'),
    ('Audience and purpose', 'You are proposing a library improvement to the headteacher. Which approach is most appropriate?',
     'A clear, respectful proposal supported by reasons.',
     ['An unexplained list of demands.', 'A clear, respectful proposal supported by reasons.', 'A private diary entry with no proposal.'],
     'Write a 100–150 word proposal to your headteacher for one library improvement. Identify the audience, purpose and desired action before writing.'),
    ('Writing and revision', 'Which revision improves the clarity of “The club was useful it helped me read more”?',
     'The club was useful because it helped me read more.',
     ['The club was useful it helped me read more more.', 'The club was useful because it helped me read more.', 'Useful club helped.'],
     'Write a 100–150 word account of learning a new skill. Revise two sentences for clarity and explain your changes.'),
]:
    ENGLISH_SEED.append(example('English Language', topic, 'multiple_choice', prompt, correct,
        'Use evidence, purpose and clear expression; avoid claims the material does not support.', options))
    ENGLISH_SEED.append(example('English Language', topic, 'essay', writing,
        'Open response: there is no single correct wording. Human review required.',
        'Review checklist: fulfil the task; address audience and purpose; organise ideas; choose precise vocabulary; control sentences and punctuation. Identify a strength, one improvement and a revision task.'))
