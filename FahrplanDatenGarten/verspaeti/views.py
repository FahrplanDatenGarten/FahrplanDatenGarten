import base64
from io import BytesIO

from django.core.cache import cache
from django.views.generic import TemplateView
from matplotlib import pyplot


class IndexView(TemplateView):
    template_name = "verspaeti/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verspaeti_data_cache = cache.get('verspaeti_data')
        if verspaeti_data_cache is not None:
            colors = ('#63a615', '#ec0016')
            labels = ('Pünktlich', 'Zu spät')
            values = [
                verspaeti_data_cache['num_current_journeys'] -
                verspaeti_data_cache['num_delayed_journeys'],
                verspaeti_data_cache['num_delayed_journeys']]
            plot_figure, plot_axes = pyplot.subplots(figsize=(5, 6))

            plot_wedges, _, plot_autotexts = pyplot.pie(
                values,
                colors=colors,
                autopct='%1.1f%%')

            plot_axes.legend(
                plot_wedges,
                labels,
                loc="lower center",
                fontsize="xx-large",
                bbox_to_anchor=(0.5, -0.1)
            )
            pyplot.setp(plot_autotexts, size=20)
            pyplot.axis('equal')
            plot_temporary_file = BytesIO()
            pyplot.savefig(plot_temporary_file, format='png')
            context['plot_image_base64'] = base64.b64encode(
                plot_temporary_file.getvalue()).decode('utf-8')

            context['journeys_delayed'] = verspaeti_data_cache['num_delayed_journeys'],
            context['biggest_delay_name'] = verspaeti_data_cache['biggest_delay_name']
            context['biggest_delay_time'] = verspaeti_data_cache['biggest_delay_time']
            context['average_delay'] = verspaeti_data_cache['average_delay']
        else:
            context['error_message'] = "Wir rechnen noch gerade die Statistiken zusammen, bitte versuche es in ein paar Minuten erneut. Wenn das Problem bestehen bleibt, melde dich bitte per E-Mail an bug_web<at>fahrplandatengarten.de"
        return context
