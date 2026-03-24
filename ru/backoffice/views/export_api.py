"""
backoffice/views/export_api.py
────────────────────────────────
Vues Export et API (Swagger, Configuration).
"""
from django.views.generic import TemplateView

from .base import RuContextMixin


class ExportExportsInternetView(RuContextMixin, TemplateView):
    template_name = 'backoffice/export/exports_internet.html'
    active_page   = 'export:exports_internet'
    breadcrumbs   = [{'label': 'Export'}, {'label': 'Exports Internet'}]


class ApiSwaggerView(RuContextMixin, TemplateView):
    template_name = 'backoffice/api/swagger.html'
    active_page   = 'api:swagger'
    breadcrumbs   = [{'label': 'API'}, {'label': 'Swagger'}]


class ApiConfigurationView(RuContextMixin, TemplateView):
    template_name = 'backoffice/api/configuration.html'
    active_page   = 'api:configuration'
    breadcrumbs   = [{'label': 'API'}, {'label': "Configuration de l'API"}]
