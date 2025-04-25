
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
# Create your views here.



class IndexPageView(TemplateView):
    template_name = 'home_module/index_page.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = 'data'
        return context


def site_header_component(request):

    return render(request, 'shared/site_header_component.html' )


def site_footer_component(request):
    return render(request, 'shared/site_footer_component.html')

        


