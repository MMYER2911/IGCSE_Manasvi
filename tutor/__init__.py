import json
import os
import secrets
import time
from pathlib import Path
from flask import Flask, abort, redirect, render_template, request, session, url_for
from .storage import db, init_db
from .resources import extract
from .questions import mark
from .english import SUBJECTS, POEMS, FRAMEWORK
from .access import init_access
from .tutoring import init_tutoring
from .marking import bp as marking_bp
from .videos import bp as videos_bp, recommendations


def create_app(config=None):
    data_dir = os.environ.get('TUTOR_DATA_DIR')
    app = Flask(__name__, instance_relative_config=True,
                **({'instance_path':str(Path(data_dir).resolve())} if data_dir else {}))
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    key_file = Path(app.instance_path) / 'session.key'
    if not key_file.exists():
        key_file.write_bytes(secrets.token_bytes(32))
        key_file.chmod(0o600)
    hosted = os.environ.get('RENDER', '').lower() == 'true'
    app.config.update(SECRET_KEY=key_file.read_bytes(), DATABASE=str(Path(app.instance_path) / 'tutor.sqlite'),
                      HOSTED=hosted, ACCESS_PASSWORD=os.environ.get('TUTOR_PASSWORD'),
                      SESSION_COOKIE_SECURE=hosted,
                      MAX_CONTENT_LENGTH=10 * 1024 * 1024, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_HTTPONLY=True)
    if config:
        app.config.update(config)

    @app.teardown_appcontext
    def close_db(error):
        conn = __import__('flask').g.pop('db', None)
        if conn:
            conn.close()

    @app.before_request
    def csrf():
        if request.endpoint == 'health':
            return
        if 'csrf' not in session:
            session['csrf'] = secrets.token_hex(24)
        if request.method == 'POST' and not secrets.compare_digest(request.form.get('csrf', ''), session['csrf']):
            abort(400, 'Invalid form token. Reload the page.')

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        frames = 'https://www.youtube-nocookie.com' if request.endpoint=='videos.watch' else "'none'"
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; form-action 'self'; frame-src "+frames
        response.headers['Cache-Control'] = 'no-store'
        return response

    init_access(app)
    init_tutoring(app)
    app.register_blueprint(marking_bp)
    app.register_blueprint(videos_bp)

    @app.route('/health')
    def health():
        db().execute('SELECT 1')
        return {'status':'ok'}

    @app.route('/')
    def home():
        return render_template('home.html', docs=db().execute('SELECT count(*) FROM documents').fetchone()[0],
          questions=db().execute('SELECT count(*) FROM questions').fetchone()[0],
          results=db().execute('''SELECT sessions.*,
            (SELECT group_concat(DISTINCT q.subject) FROM responses r JOIN questions q ON q.id=r.question_id WHERE r.session_id=sessions.id) AS subjects,
            (SELECT count(*) FROM responses r WHERE r.session_id=sessions.id AND r.status='awaiting_review') AS pending
            FROM sessions WHERE submitted IS NOT NULL ORDER BY submitted DESC''').fetchall(),
          subjects=SUBJECTS)

    @app.route('/study/<slug>')
    def study(slug):
        if slug not in SUBJECTS:
            abort(404)
        return render_template('study.html', subject=SUBJECTS[slug], slug=slug,videos=recommendations(SUBJECTS[slug]['name']))

    @app.route('/poetry', methods=['GET', 'POST'])
    def poetry():
        poem = request.form.get('poem') if request.method == 'POST' else request.args.get('poem', POEMS[0])
        if poem not in POEMS:
            abort(404)
        if request.method == 'POST':
            notes = {key:request.form.get(key, '').strip() for key, _ in FRAMEWORK}
            if any(len(value) > 8000 for value in notes.values()):
                abort(400, 'Each notebook section must be at most 8000 characters.')
            db().execute('''INSERT INTO poetry_notes(poem,notes) VALUES (?,?)
                ON CONFLICT(poem) DO UPDATE SET notes=excluded.notes,updated_at=CURRENT_TIMESTAMP''', (poem, json.dumps(notes)))
            db().commit()
            return redirect(url_for('poetry', poem=poem, saved='1'))
        row = db().execute('SELECT * FROM poetry_notes WHERE poem=?', (poem,)).fetchone()
        return render_template('poetry.html', poem=poem, poems=POEMS, framework=FRAMEWORK,
            notes=json.loads(row['notes']) if row else {}, updated=row['updated_at'] if row else None)

    @app.route('/resources', methods=['GET', 'POST'])
    def resources():
        error = None
        if request.method == 'POST':
            fields = ['title','subject','board','specification','topic','document_type','year','source','rights']
            metadata = [request.form.get(field, '').strip() for field in fields]
            upload = request.files.get('file')
            if not all(metadata) or not upload or request.form.get('authorised') != 'yes':
                error = 'Complete all metadata and confirm permission to upload.'
            elif any(len(value) > 500 for value in metadata):
                error = 'Metadata fields must be 500 characters or fewer.'
            else:
                try:
                    chunks = extract(upload.filename, upload.read())
                except Exception:
                    error = 'Cannot extract this file. Use a valid, unlocked PDF with selectable text (up to 300 pages) or UTF-8 .txt, within the text limit.'
                else:
                    with db():
                        cursor = db().execute('INSERT INTO documents (' + ','.join(fields) + ',allow_ai) VALUES (' + ','.join('?' for _ in fields) + ',?)', metadata + [int(request.form.get('allow_ai') == 'yes')])
                        db().executemany('INSERT INTO chunks(document_id,page,text) VALUES (?,?,?)', [(cursor.lastrowid, page, text) for page, text in chunks])
                    return redirect(url_for('resources'))
        query = request.args.get('q', '').strip()[:200]
        subject = request.args.get('subject', '').strip()[:100]
        hits = []
        if query:
            # Quote tokens so user text cannot become FTS query syntax.
            expression = ' OR '.join('"' + token.replace('"','""') + '"' for token in query.split())
            hits = db().execute('''SELECT documents.*, chunks.page, chunks.text FROM chunks
              JOIN documents ON documents.id=chunks.document_id WHERE chunks MATCH ?
              AND (?='' OR documents.subject=?) ORDER BY rank LIMIT 30''', (expression, subject, subject)).fetchall()
        return render_template('resources.html', error=error, query=query, hits=hits,
          subject=subject, subjects=[r[0] for r in db().execute('SELECT DISTINCT subject FROM documents ORDER BY subject')],
          documents=db().execute("SELECT * FROM documents WHERE ?='' OR subject=? ORDER BY id DESC", (subject,subject)).fetchall())

    @app.route('/resources/<int:document_id>/ai-access', methods=['POST'])
    def resource_ai_access(document_id):
        enabled = request.form.get('allow_ai') == 'yes'
        if enabled and request.form.get('authorised') != 'yes':
            abort(400, 'Confirm permission to send excerpts to the AI provider.')
        updated = db().execute('UPDATE documents SET allow_ai=? WHERE id=?', (int(enabled), document_id))
        db().commit()
        if not updated.rowcount:
            abort(404)
        return redirect(url_for('resources'))

    @app.route('/practice', methods=['GET','POST'])
    def practice():
        if request.method == 'POST':
            try:
                duration = int(request.form.get('duration', '10'))
            except ValueError:
                abort(400)
            if duration not in (5,10,20,30):
                abort(400)
            sql, args = 'SELECT id FROM questions WHERE subject=?', [request.form.get('subject')]
            for field in ('topic','difficulty'):
                if request.form.get(field):
                    sql += ' AND ' + field + '=?'
                    args.append(request.form[field])
            ids = [row['id'] for row in db().execute(sql + ' ORDER BY RANDOM() LIMIT 10', args)]
            if not ids:
                abort(400, 'No questions match those filters.')
            sid = secrets.token_urlsafe(24)
            db().execute('INSERT INTO sessions(id,started,duration,question_ids) VALUES (?,?,?,?)', (sid,time.time(),duration*60,json.dumps(ids)))
            db().commit()
            return redirect(url_for('attempt', sid=sid))
        subjects = [r[0] for r in db().execute('SELECT DISTINCT subject FROM questions ORDER BY subject')]
        selected = request.args.get('subject', 'English Literature')
        if selected not in subjects:
            abort(400, 'Unknown subject.')
        return render_template('practice.html', subjects=subjects, selected=selected,
          topics=[r[0] for r in db().execute('SELECT DISTINCT topic FROM questions WHERE subject=? ORDER BY topic',(selected,))])

    @app.route('/attempt/<sid>', methods=['GET','POST'])
    def attempt(sid):
        record = db().execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
        if not record:
            abort(404)
        ids = json.loads(record['question_ids'])
        questions = [dict(db().execute('SELECT * FROM questions WHERE id=?',(qid,)).fetchone()) for qid in ids]
        remaining = max(0, int(record['started'] + record['duration'] - time.time()))
        if request.method == 'POST' and record['submitted'] is None:
            now = time.time()
            # Five-second transport grace; later answers receive no marks.
            expired = now > record['started'] + record['duration'] + 5
            answers = [(q, request.form.get(str(q['id']), '')) for q in questions]
            if any(len(a) > 10000 for _, a in answers):
                abort(400, 'Answers must be at most 10000 characters each.')
            graded = [(q,a,mark(q,a)) for q,a in answers]
            with db():
                updated = db().execute('UPDATE sessions SET submitted=?,score=?,total=?,elapsed=?,expired=? WHERE id=? AND submitted IS NULL',
                  (now,sum(score if not expired else 0 for q,a,score in graded if score is not None),
                   sum(q['marks'] for q,a,score in graded if score is not None),
                   min(max(0,int(now-record['started'])),record['duration']),int(expired),sid))
                if updated.rowcount:
                    db().executemany('INSERT INTO responses(session_id,question_id,answer,score,status) VALUES (?,?,?,?,?)',
                        [(sid,q['id'],a,None if score is None else (0 if expired else score),
                          'awaiting_review' if score is None else 'automatic') for q,a,score in graded])
            return redirect(url_for('attempt', sid=sid))
        for q in questions:
            q['choices'] = json.loads(q['options'])
        responses = {r['question_id']:dict(r) for r in db().execute('SELECT * FROM responses WHERE session_id=?',(sid,))}
        return render_template('attempt.html', record=record, questions=questions, remaining=remaining, responses=responses,
            subject=questions[0]['subject'], pending=sum(r['status']=='awaiting_review' for r in responses.values()),
            question_videos={q['id']:recommendations(q['subject'],question_id=q['id']) for q in questions} if record['submitted'] is not None else {})

    with app.app_context():
        init_db()
    return app
