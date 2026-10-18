"""Small server-side adapter for the OpenAI Responses API; no browser-held key."""
import json
import urllib.error
import urllib.request


class TutorUnavailable(Exception):
    pass


ASSESSMENT_SCHEMA = {
    'type':'object','additionalProperties':False,
    'properties':{
        'assessable':{'type':'boolean'}, 'mark':{'type':['integer','null']},
        'max_marks':{'type':'integer'},
        'justification':{'type':'string'}, 'strength':{'type':'string'},
        'improvement':{'type':'string'}, 'revision_task':{'type':'string'},
        'scheme_references':{'type':'array','items':{'type':'string'}},
    },
    'required':['assessable','mark','max_marks','justification','strength','improvement','revision_task','scheme_references'],
}


class OpenAITutor:
    def __init__(self, api_key, model='gpt-4.1-mini'):
        self.api_key = api_key
        self.model = model

    def reply(self, instructions, messages, schema=None):
        data = {'model':self.model, 'instructions':instructions,
                'input':messages, 'max_output_tokens':1000 if schema else 700, 'store':False}
        if schema:
            data['text'] = {'format':{'type':'json_schema','name':'rubric_assessment','strict':True,'schema':schema}}
        payload = json.dumps(data).encode()
        request = urllib.request.Request('https://api.openai.com/v1/responses', data=payload,
            headers={'Authorization':'Bearer '+self.api_key, 'Content-Type':'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise TutorUnavailable('The tutor response was too large. Please try a shorter question.')
            result = json.loads(body)
        except urllib.error.HTTPError as error:
            # Never display/log the remote error body: it may contain sensitive data.
            if error.code in (401,403):
                message = 'The AI connection was rejected. Ask your parent to check the API key and model access in Render.'
            elif error.code == 429:
                message = 'The AI service limit was reached. Ask your parent to check API billing or usage limits, then try again.'
            else:
                message = 'The AI service could not finish this request. Please try again shortly.'
            raise TutorUnavailable(message) from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise TutorUnavailable('The AI connection did not complete. Please try again shortly.') from None
        if not isinstance(result, dict) or result.get('status') != 'completed':
            raise TutorUnavailable('The tutor did not finish its answer. Please try a shorter question.')
        output = result.get('output')
        if not isinstance(output, list):
            raise TutorUnavailable('The AI service returned an unexpected response. Please try again.')
        parts = []
        for item in output:
            if not isinstance(item, dict) or item.get('type') != 'message':
                continue
            content = item.get('content')
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and part.get('type') == 'output_text' and isinstance(part.get('text'), str):
                    parts.append(part['text'])
        text = '\n'.join(parts)
        if not text.strip() or len(text) > 12000:
            raise TutorUnavailable('The tutor did not return a usable answer. Please rephrase your question.')
        return text.strip()

    def assess(self,instructions,messages):
        text = self.reply(instructions,messages,schema=ASSESSMENT_SCHEMA)
        try:
            return json.loads(text)
        except ValueError:
            raise TutorUnavailable('The AI did not return a valid rubric assessment. No mark has been saved.') from None
