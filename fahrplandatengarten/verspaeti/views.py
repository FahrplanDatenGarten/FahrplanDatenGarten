from django.core.cache import cache
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "verspaeti/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verspaeti_data_cache = cache.get('verspaeti_data')
        if verspaeti_data_cache is not None:

            context['journeys_delayed'] = verspaeti_data_cache['num_delayed_journeys'],
            context['biggest_delay_name'] = verspaeti_data_cache['biggest_delay_name']
            context['biggest_delay_time'] = verspaeti_data_cache['biggest_delay_time']
            context['average_delay'] = verspaeti_data_cache['average_delay']
            context['plot_image_base64'] = verspaeti_data_cache['plot_image_base64']
        else:
            context['error_message'] = "Wir rechnen noch gerade die Statistiken zusammen, bitte versuche es in ein paar Minuten erneut. Wenn das Problem bestehen bleibt, melde dich bitte per E-Mail an bug_web<at>fahrplandatengarten.de"
        return context
