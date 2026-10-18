"""Small server-side adapter for the OpenAI Responses API; no browser-held key."""
import json
import urllib.error
import urllib.request


class TutorUnavailable(Exception):
    pass


class OpenAITutor:
    def __init__(self, api_key, model='gpt-4.1-mini'):
        self.api_key = api_key
        self.model = model

    def reply(self, instructions, messages):
        payload = json.dumps({'model':self.model, 'instructions':instructions,
                              'input':messages, 'max_output_tokens':700, 'store':False}).encode()
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
