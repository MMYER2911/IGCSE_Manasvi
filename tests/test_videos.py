import json
import urllib.error
import pytest
from tutor.storage import db
from tutor.videos import youtube_id,metadata,recommendations
from test_tutor import chat_client,form,Response

VIDEO='abcDEF_1234'


def candidate(client,monkeypatch,**changes):
    monkeypatch.setattr('tutor.videos.metadata',lambda video_id:{'title':'A clear explanation','channel':'Test educator','embed_available':1})
    data={'csrf':form(client)['csrf'],'url':'https://youtu.be/'+VIDEO,'subject':'English Literature',
        'topic':'An Inspector Calls','focus':'Explains how to develop a supported character interpretation.',
        'start_seconds':'30','end_seconds':'150'}
    data.update(changes)
    response=client.post('/videos',data=data)
    return response,data


def review_form(client,**changes):
    data={'csrf':form(client)['csrf'],'reviewer':'Parent','summary':'Clear explanation checked against the text. General concept teaching, not board-specific exam technique.',
        'watched':'yes','accuracy':'4','relevance':'5','clarity':'4','alignment':'1','scope':'concept'}
    data.update(changes)
    return data


def test_only_valid_youtube_video_urls():
    for url in ('https://youtu.be/'+VIDEO,'https://www.youtube.com/watch?v='+VIDEO+'&t=30',
                'https://m.youtube.com/watch?v='+VIDEO,'https://youtube.com/shorts/'+VIDEO):
        assert youtube_id(url)==VIDEO
    for url in ('http://youtu.be/'+VIDEO,'https://youtube.com.evil.test/watch?v='+VIDEO,
                'https://user@www.youtube.com/watch?v='+VIDEO,'https://youtube.com/playlist?list=123',
                'https://www.youtube.com/watch?v=short','https://youtu.be/'+VIDEO+'/extra',
                'https://www.youtube.com/watch?v='+VIDEO+'&v=other','https://['):
        with pytest.raises(ValueError):youtube_id(url)


def test_metadata_uses_only_canonical_video_url_not_html(monkeypatch):
    calls=[]
    def transport(url,timeout):
        calls.append((url,timeout))
        return Response(json.dumps({'title':'Video title','author_name':'Educator','html':'<iframe src="https://evil.test"><script>bad()</script></iframe>'}).encode())
    monkeypatch.setattr('urllib.request.urlopen',transport)
    result=metadata(VIDEO)
    assert result=={'title':'Video title','channel':'Educator','embed_available':1}
    assert calls[0][0].startswith('https://www.youtube.com/oembed?') and calls[0][1]==12
    assert 'html' not in result


def test_metadata_denial_is_not_a_verified_candidate(monkeypatch):
    def denied(*args,**kwargs):
        raise urllib.error.URLError('Private diagnostic details')
    monkeypatch.setattr('urllib.request.urlopen',denied)
    with pytest.raises(ValueError,match='No recommendation has been created') as caught:metadata(VIDEO)
    assert 'Private diagnostic details' not in str(caught.value)


def test_candidate_not_recommended_until_watched_review(chat_client,monkeypatch):
    client,_=chat_client
    response,_=candidate(client,monkeypatch)
    assert response.status_code==302
    with client.application.app_context():
        assert recommendations('English Literature')==[]
        identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    assert client.post(f'/videos/{identity}/review',data=review_form(client,watched='')).status_code==400
    assert client.post(f'/videos/{identity}/review',data=review_form(client)).status_code==302
    with client.application.app_context():
        videos=recommendations('English Literature')
        assert len(videos)==1 and videos[0]['review']['scope']=='concept'
        assert recommendations('English Language')==[]
    assert 'Concept explanation; exam-specific technique not verified' in client.get('/study/literature').text


def test_weak_review_not_promoted_and_exam_fit_required(chat_client,monkeypatch):
    client,_=chat_client
    candidate(client,monkeypatch)
    with client.application.app_context():identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    client.post(f'/videos/{identity}/review',data=review_form(client,accuracy='2'))
    with client.application.app_context():assert recommendations('English Literature')==[]
    assert client.post(f'/videos/{identity}/review',data=review_form(client,scope='exam_specific',specification='4EA1',alignment='5')).status_code==400
    assert client.post(f'/videos/{identity}/review',data=review_form(client,scope='exam_specific',specification='4ET1',alignment='5')).status_code==302
    with client.application.app_context():assert len(recommendations('English Literature'))==1


def test_embed_is_opt_in_strictly_constructed_and_has_fallback(chat_client,monkeypatch):
    client,_=chat_client
    candidate(client,monkeypatch)
    with client.application.app_context():identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    path=f'/videos/{identity}/watch'
    get=client.get(path)
    assert '<iframe ' not in get.text and 'Load YouTube player' in get.text
    assert client.post(path,data={}).status_code==400
    post=client.post(path,data={'csrf':form(client)['csrf']})
    assert f'https://www.youtube-nocookie.com/embed/{VIDEO}?start=30' in post.text
    assert 'end=150' in post.text and 'Watch on YouTube' in post.text
    assert 'referrerpolicy="strict-origin-when-cross-origin"' in post.text
    assert 'frame-src https://www.youtube-nocookie.com' in post.headers['Content-Security-Policy']
    assert "frame-src 'none'" in client.get('/').headers['Content-Security-Policy']
    with client.application.app_context():
        db().execute('UPDATE learning_videos SET embed_available=0');db().commit()
    assert '<iframe ' not in client.post(path,data={'csrf':form(client)['csrf']}).text


def test_exact_question_video_shown_after_submission_only(chat_client,monkeypatch):
    client,_=chat_client
    with client.application.app_context():
        q=db().execute("SELECT id,answer FROM questions WHERE subject='English Literature' AND topic='An Inspector Calls' AND kind='multiple_choice'").fetchone()
        qid,answer=q['id'],q['answer']
    candidate(client,monkeypatch,question_id=str(qid))
    with client.application.app_context():identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    client.post(f'/videos/{identity}/review',data=review_form(client))
    data={'csrf':form(client)['csrf'],'subject':'English Literature','topic':'An Inspector Calls','difficulty':'Foundation','duration':'5'}
    path=client.post('/practice',data=data).location
    assert 'A clear explanation' not in client.get(path).text
    client.post(path,data={'csrf':data['csrf'],str(qid):answer})
    assert 'A clear explanation' in client.get(path).text
    with client.application.app_context():assert recommendations('English Literature',question_id=999)==[]


def test_cross_subject_question_link_and_unsafe_review_url_rejected(chat_client,monkeypatch):
    client,_=chat_client
    response,_=candidate(client,monkeypatch,question_id='1')
    assert 'Linked questions must belong' in response.text
    candidate(client,monkeypatch)
    with client.application.app_context():identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    assert client.post(f'/videos/{identity}/review',data=review_form(client,review_url='javascript:bad()')).status_code==400
    assert client.post(f'/videos/{identity}/review',data=review_form(client,review_url='https://example.org/review')).status_code==302
    assert 'Reviewer-supplied independent review source' in client.get('/videos').text

from test_marking import marking_client,register,registration


def test_reviewed_video_attaches_to_exact_scheme_feedback(marking_client,monkeypatch):
    client,_,doc=marking_client
    rubric=register(client,doc)
    assert candidate(client,monkeypatch,rubric_id=str(rubric))[0].status_code==302
    with client.application.app_context():identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    client.post(f'/videos/{identity}/review',data=review_form(client,scope='exam_specific',specification='4ET1',alignment='4'))
    data=form(client);data.update(mode='mark',rubric_id=str(rubric),message='An analytical response.')
    assert client.post('/tutor/literature',data=data).status_code==302
    assert 'A clear explanation' in client.get('/tutor/literature').text


def test_video_exam_scope_matches_linked_language_route(marking_client,monkeypatch):
    client,_,doc=marking_client
    with client.application.app_context():
        db().execute("UPDATE documents SET subject='English Language',specification='4EB1' WHERE id=?",(doc,));db().commit()
    assert client.post('/marking',data=registration(client,doc,component='4EB1/01')).status_code==302
    with client.application.app_context():rubric=db().execute('SELECT id FROM marking_rubrics').fetchone()[0]
    assert candidate(client,monkeypatch,subject='English Language',rubric_id=str(rubric))[0].status_code==302
    with client.application.app_context():identity=db().execute('SELECT id FROM learning_videos').fetchone()[0]
    assert client.post(f'/videos/{identity}/review',data=review_form(client,scope='exam_specific',specification='4EA1',alignment='5')).status_code==400
    assert client.post(f'/videos/{identity}/review',data=review_form(client,scope='exam_specific',specification='4EB1',alignment='5')).status_code==302
