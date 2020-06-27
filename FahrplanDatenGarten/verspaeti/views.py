from django.core.cache import cache
from django.views.generic import TemplateView
from plotly.graph_objs import Pie
from plotly.offline import plot


class IndexView(TemplateView):
    template_name = "verspaeti/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verspaeti_data_cache = cache.get('verspaeti_data')
        if verspaeti_data_cache is not None:
            colors = ['#63a615', '#ec0016']
            labels = ['Pünktlich', 'Zu spät']
            values = [
                verspaeti_data_cache['num_current_journeys'] -
                verspaeti_data_cache['num_delayed_journeys'],
                verspaeti_data_cache['num_delayed_journeys']]
            plot_div = plot(
                [Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors))],
                output_type='div')

            context['plot_div'] = plot_div
            context['journeys_delayed'] = verspaeti_data_cache['num_delayed_journeys'],
            context['biggest_delay'] = verspaeti_data_cache['biggest_delay']
            context['biggest_delay_time'] = verspaeti_data_cache['biggest_delay_time']
            context['average_delay'] = verspaeti_data_cache['average_delay']
        else:
            context['error_message'] = "Wir rechnen noch gerade die Statistiken zusammen, bitte versuche es in ein paar Minuten erneut. Wenn das Problem bestehen bleibt, melde dich bitte per E-Mail an bug_web<at>fahrplandatengarten.de"
        return context
