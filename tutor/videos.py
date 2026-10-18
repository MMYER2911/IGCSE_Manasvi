"""YouTube metadata, evidence-backed manual curation, and opt-in embeds."""
import json
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from flask import Blueprint, abort, redirect, render_template, request, url_for
from .storage import db

bp = Blueprint('videos', __name__)
SUBJECTS = ('English Literature','English Language','Mathematics')


def youtube_id(url):
    try:
        if len(url)>2000:
            raise ValueError()
        parsed = urllib.parse.urlsplit(url.strip())
        if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError()
        if parsed.hostname == 'youtu.be':
            candidate = parsed.path.strip('/')
        elif parsed.hostname in ('youtube.com','www.youtube.com','m.youtube.com'):
            if parsed.path == '/watch':
                values = urllib.parse.parse_qs(parsed.query).get('v',[])
                candidate = values[0] if len(values)==1 else ''
            else:
                match = re.fullmatch(r'/(?:shorts|embed)/([A-Za-z0-9_-]{11})/?',parsed.path)
                candidate = match[1] if match else ''
        else:
            raise ValueError()
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}',candidate):
            raise ValueError()
        return candidate
    except ValueError:
        raise ValueError('Use a public HTTPS YouTube video link, not a playlist or channel link.') from None


def metadata(video_id):
    query = urllib.parse.urlencode({'url':'https://www.youtube.com/watch?v='+video_id,'format':'json'})
    try:
        with urllib.request.urlopen('https://www.youtube.com/oembed?'+query,timeout=12) as response:
            body = response.read(100001)
        if len(body)>100000:
            raise ValueError()
        result = json.loads(body)
        if not isinstance(result,dict) or not all(isinstance(result.get(k),str) and result[k].strip() for k in ('title','author_name')):
            raise ValueError()
        # Never render oEmbed's HTML. Construct the iframe ourselves from the validated ID.
        embed = isinstance(result.get('html'),str) and bool(re.search(r'<iframe\b',result['html'],re.IGNORECASE))
        return {'title':result['title'][:500],'channel':result['author_name'][:300],'embed_available':int(embed)}
    except (urllib.error.URLError,TimeoutError,OSError,ValueError):
        raise ValueError('YouTube metadata could not be checked. The video may be restricted, unavailable, or blocked by network policy. No recommendation has been created.') from None


def review_url(value):
    if not value:
        return ''
    try:
        url = urllib.parse.urlsplit(value)
        if url.scheme!='https' or not url.hostname or url.username or url.password:
            raise ValueError()
        if len(value)>1000:
            raise ValueError()
    except ValueError:
        raise ValueError('Use an HTTPS review-source URL without account credentials.') from None
    return value


def records(rows):
    return [dict(row,review=json.loads(row['review']) if row['review'] else None,
                 watch_url='https://www.youtube.com/watch?v='+row['youtube_id']) for row in rows]


def recommendations(subject,question_id=None,rubric_id=None,limit=3):
    sql = "SELECT v.* FROM learning_videos v WHERE v.subject=? AND v.status='recommended'"
    args = [subject]
    if question_id is not None:
        sql += ' AND EXISTS(SELECT 1 FROM video_question_links l WHERE l.video_id=v.id AND l.question_id=?)'
        args.append(question_id)
    if rubric_id is not None:
        sql += ' AND EXISTS(SELECT 1 FROM video_rubric_links l WHERE l.video_id=v.id AND l.rubric_id=?)'
        args.append(rubric_id)
    # Rank only reviewed teaching evidence, never views/likes or creator popularity.
    sql += " ORDER BY (CAST(json_extract(v.review,'$.accuracy') AS INTEGER)*4+CAST(json_extract(v.review,'$.relevance') AS INTEGER)*3+CAST(json_extract(v.review,'$.clarity') AS INTEGER)*2) DESC,v.id DESC LIMIT ?"
    args.append(limit)
    return records(db().execute(sql,args).fetchall())


@bp.route('/videos',methods=['GET','POST'])
def library():
    error = None
    if request.method == 'POST':
        try:
            subject = request.form.get('subject','')
            topic,focus = (request.form.get(k,'').strip() for k in ('topic','focus'))
            if subject not in SUBJECTS or not topic or not focus or len(topic)>200 or len(focus)>2000:
                raise ValueError('Choose a subject and describe the topic and learning need.')
            video_id = youtube_id(request.form.get('url',''))
            if db().execute('SELECT 1 FROM learning_videos WHERE youtube_id=? AND subject=?',(video_id,subject)).fetchone():
                raise ValueError('This video is already catalogued for that subject.')
            start = int(request.form.get('start_seconds','0'))
            end = int(request.form['end_seconds']) if request.form.get('end_seconds') else None
            if not 0 <= start <= 86400 or end is not None and not start < end <= 86400:
                raise ValueError('Choose a valid start time and an optional later end time (in seconds).')
            links = []
            for field,table in (('question_id','questions'),('rubric_id','marking_rubrics')):
                if request.form.get(field):
                    identity = int(request.form[field])
                    row = db().execute('SELECT subject FROM questions WHERE id=?',(identity,)).fetchone() if table=='questions' else db().execute('SELECT d.subject FROM marking_rubrics r JOIN documents d ON d.id=r.document_id WHERE r.id=?',(identity,)).fetchone()
                    if not row or row['subject']!=subject:
                        raise ValueError('Linked questions must belong to the selected subject.')
                    links.append((field,identity))
            details = metadata(video_id)
            cursor = db().execute('''INSERT INTO learning_videos(youtube_id,subject,topic,title,channel,focus,start_seconds,end_seconds,embed_available)
                VALUES (?,?,?,?,?,?,?,?,?)''',(video_id,subject,topic,details['title'],details['channel'],focus,start,end,details['embed_available']))
            for field,identity in links:
                table = 'video_question_links' if field=='question_id' else 'video_rubric_links'
                db().execute(f'INSERT INTO {table} VALUES (?,?)',(cursor.lastrowid,identity))
            db().commit()
            return redirect(url_for('videos.library'))
        except (ValueError,sqlite3.IntegrityError) as failure:
            db().rollback()
            error = 'This video is already catalogued for that subject.' if isinstance(failure,sqlite3.IntegrityError) else str(failure)
    return render_template('videos.html',videos=records(db().execute('SELECT * FROM learning_videos ORDER BY id DESC').fetchall()),
        subjects=SUBJECTS,error=error,questions=db().execute('SELECT id,subject,prompt FROM questions ORDER BY subject,id').fetchall(),
        rubrics=db().execute('SELECT r.id,d.subject,r.component,r.question_number FROM marking_rubrics r JOIN documents d ON d.id=r.document_id').fetchall())


@bp.route('/videos/<int:identity>/review',methods=['POST'])
def review(identity):
    row = db().execute('SELECT * FROM learning_videos WHERE id=?',(identity,)).fetchone()
    if not row:
        abort(404)
    try:
        reviewer,summary = (request.form.get(k,'').strip() for k in ('reviewer','summary'))
        if not reviewer or len(reviewer)>200 or not summary or len(summary)>3000 or request.form.get('watched')!='yes':
            raise ValueError('A named parent/teacher must watch the video and explain its strengths and limitations before recommending it.')
        scores = {k:int(request.form.get(k,'')) for k in ('accuracy','relevance','clarity','alignment')}
        if any(not 1<=value<=5 for value in scores.values()):
            raise ValueError('Rate each criterion from 1 to 5.')
        scope = request.form.get('scope','concept')
        spec = request.form.get('specification','').strip().upper()
        if scope not in ('concept','exam_specific'):
            raise ValueError('Choose concept explanation or exam-specific guidance.')
        specs = {'English Literature':{'4ET1'},'English Language':{'4EA1','4EB1'},'Mathematics':set()}
        if scope=='exam_specific' and spec not in specs[row['subject']]:
            raise ValueError('Confirm the applicable specification for exam-specific guidance.')
        if scope=='exam_specific':
            linked = db().execute('''SELECT d.specification FROM video_rubric_links l
                JOIN marking_rubrics r ON r.id=l.rubric_id JOIN documents d ON d.id=r.document_id
                WHERE l.video_id=?''',(identity,)).fetchall()
            if any(r['specification'].strip().upper()!=spec for r in linked):
                raise ValueError('Exam-specific video guidance must match every linked rubric’s specification.')
        evidence = dict(scores,reviewer=reviewer,summary=summary,scope=scope,specification=spec,
            independent_review_url=review_url(request.form.get('review_url','').strip()),
            checked_at=datetime.now(timezone.utc).isoformat(),basis='Parent/teacher watched video; independent source only if listed')
        required = ('accuracy','relevance','clarity','alignment') if scope=='exam_specific' else ('accuracy','relevance','clarity')
        status = 'recommended' if all(scores[k]>=4 for k in required) else 'reviewed_with_limitations'
        db().execute('UPDATE learning_videos SET status=?,review=? WHERE id=?',(status,json.dumps(evidence),identity))
        db().commit()
    except ValueError as failure:
        abort(400,str(failure))
    return redirect(url_for('videos.library'))


@bp.route('/videos/<int:identity>/watch',methods=['GET','POST'])
def watch(identity):
    row = db().execute('SELECT * FROM learning_videos WHERE id=?',(identity,)).fetchone()
    if not row:
        abort(404)
    video = records([row])[0]
    embed_url = None
    if request.method=='POST' and row['embed_available']:
        query = {'start':row['start_seconds'],'rel':0}
        if row['end_seconds'] is not None:
            query['end'] = row['end_seconds']
        embed_url = 'https://www.youtube-nocookie.com/embed/'+row['youtube_id']+'?'+urllib.parse.urlencode(query)
    return render_template('video_watch.html',video=video,embed_url=embed_url)
