import json

from rest_framework.renderers import JSONRenderer


class ArticleJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Render the articles in a structured manner for the end user.
        """
        return json.dumps({
            'article': data
        })
