# Python
import json

# Django
from django.http import HttpResponse
from simple_tags import models

def CompleteTagAjaxView(request, tag, limit):
	limit = int(limit)
	tags = models.Tag.complete_tag_name(tag=tag, limit=limit)
	answer = json.dumps(list(tags))
	return HttpResponse(answer, content_type="application/json")