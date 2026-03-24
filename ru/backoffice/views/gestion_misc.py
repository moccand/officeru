"""
backoffice/views/gestion_misc.py
──────────────────────────────────
Vues de gestion sans CRUD propre :
  - Mutations
  - Analyse des référentiels
  - Détails
"""
from django.views.generic import TemplateView

from .base import RuContextMixin


class GestionMutationsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/mutations.html'
    active_page   = 'gestion:mutations'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Mutations'}]


class GestionAnalyseReferentielsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/analyse_referentiels.html'
    active_page   = 'gestion:analyse_referentiels'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Analyse des Référentiels'}]


class GestionDetailsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/details.html'
    active_page   = 'gestion:details'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Détails'}]
