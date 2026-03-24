"""
backoffice/views/gestion_misc.py
──────────────────────────────────
Vues de gestion sans CRUD propre :
  - Mutations
  - Gestion avancée (onglets)
  - Analyse des référentiels
"""
from django.views.generic import TemplateView

from .base import RuContextMixin


_ONGLETS_GESTION_AVANCEE = frozenset({
    'details_parcelles',
    'details_alignements',
    'associations_masse',
})


class GestionMutationsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/mutations.html'
    active_page   = 'gestion:mutations'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Mutations'}]


class GestionAvanceeView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/gestion_avancee.html'
    active_page   = 'gestion:avancee'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Gestion avancée'}]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        onglet = self.request.GET.get('onglet', 'details_parcelles')
        ctx['onglet_actif'] = (
            onglet if onglet in _ONGLETS_GESTION_AVANCEE else 'details_parcelles'
        )
        return ctx


class GestionAnalyseReferentielsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/analyse_referentiels.html'
    active_page   = 'gestion:analyse_referentiels'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Analyse des Référentiels'}]
