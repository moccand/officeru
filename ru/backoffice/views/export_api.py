"""
backoffice/views/export_api.py
────────────────────────────────
Vues Export et API (Swagger).
"""
from django.views.generic import TemplateView

from .base import RuContextMixin

_ONGLETS_API_SWAGGER = frozenset({'swagger', 'configuration'})


class ExportExportsInternetView(RuContextMixin, TemplateView):
    template_name = 'backoffice/export/exports_internet.html'
    active_page   = 'export:exports_internet'
    breadcrumbs   = [{'label': 'Export'}, {'label': 'Exports Internet'}]


class ApiSwaggerView(RuContextMixin, TemplateView):
    template_name = 'backoffice/api/swagger.html'
    active_page   = 'api:swagger'
    breadcrumbs   = [{'label': 'API'}, {'label': 'Swagger et configuration'}]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        onglet = self.request.GET.get('onglet', 'swagger')
        ctx['onglet_actif'] = onglet if onglet in _ONGLETS_API_SWAGGER else 'swagger'
        return ctx
