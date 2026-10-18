import sqlite3
from flask import current_app, g


def db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


def init_db():
    db().executescript('''
    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL,
      board TEXT NOT NULL, specification TEXT NOT NULL, topic TEXT NOT NULL,
      document_type TEXT NOT NULL, year TEXT NOT NULL, source TEXT NOT NULL,
      rights TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(document_id UNINDEXED, page UNINDEXED, text);
    CREATE TABLE IF NOT EXISTS questions (
      id INTEGER PRIMARY KEY, subject TEXT, topic TEXT, difficulty TEXT,
      kind TEXT, prompt TEXT, options TEXT, answer TEXT, explanation TEXT,
      marks INTEGER, tolerance REAL DEFAULT 0, provenance TEXT);
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY, started REAL, duration INTEGER, question_ids TEXT,
      submitted REAL, score INTEGER, total INTEGER, elapsed INTEGER);
    CREATE TABLE IF NOT EXISTS responses (
      session_id TEXT REFERENCES sessions(id), question_id INTEGER REFERENCES questions(id),
      answer TEXT, score INTEGER, PRIMARY KEY(session_id, question_id));
    CREATE TABLE IF NOT EXISTS poetry_notes (
      poem TEXT PRIMARY KEY, notes TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    ''')
    # Additive migrations preserve databases created by the mathematics prototype.
    columns = {row['name'] for row in db().execute('PRAGMA table_info(responses)')}
    if 'status' not in columns:
        db().execute("ALTER TABLE responses ADD COLUMN status TEXT NOT NULL DEFAULT 'automatic'")
    columns = {row['name'] for row in db().execute('PRAGMA table_info(sessions)')}
    if 'expired' not in columns:
        db().execute('ALTER TABLE sessions ADD COLUMN expired INTEGER NOT NULL DEFAULT 0')
    from .questions import SEED
    from .english import ENGLISH_SEED
    for question in SEED + ENGLISH_SEED:
        if db().execute('SELECT 1 FROM questions WHERE subject=? AND prompt=?', (question[0], question[4])).fetchone():
            continue
        db().execute('''INSERT INTO questions
          (subject,topic,difficulty,kind,prompt,options,answer,explanation,marks,tolerance,provenance)
          VALUES (?,?,?,?,?,?,?,?,?,?,?)''', question)
    db().commit()
