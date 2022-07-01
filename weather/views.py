from django.views.generic import TemplateView
from weather.jobs import geocoding, one_call


class WeatherView(TemplateView):
    template_name = 'weather.html'

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q')
        if q:
            lat, lon = geocoding(q)
        else:
            lat, lon = self.request.GET.get('lat'), self.request.GET.get('lon')

        context = one_call(lat, lon)
        return context
