# Ajax class
import json
import time
from django.http import HttpResponse

class JsonMixin(object):
    content_type = "application/json"

    def render_json_answer(self, data, *args, **kwargs):
        """ Recieves dict. and gives back HttpResponse object with json data """
        data = json.dumps(data)
        return HttpResponse(data, self.content_type)

class JsonFormMixin(JsonMixin):
    http_method_names = ['post']

    def form_invalid(self, form, send_json=True, *args, **kwargs):
        """ Returns as dict (or sends HttpResponse with json data).
            send_json will say should be data converted and sent, or just returned. Default: True.
        """
        response = {
            'success':False,
            'form':form.as_table(),
        }
        return self.render_json_answer(response) if send_json else response 

    def form_valid(self, form, send_json=True, *args, **kwargs):
        """ Like the form_invalid, but parameter success will be true and form will be saved. """
        # Model instance does not have all required attr's yet ('cause they can't be taken from form)
        form.instance.date = time.strftime('%Y-%m-%d %H:%M:%S')
        form.instance.board_id = self.board

        # Saving the the object
        self.object = form.save()

        # New, clean form
        form = self.form_class()

        response = {
            'success':True,
            'form':form.as_table(),
        }
        return self.render_json_answer(response) if send_json else response 