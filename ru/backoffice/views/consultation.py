"""
backoffice/views/consultation.py
─────────────────────────────────
Vues de la section Consultation.
"""
from django.views.generic import TemplateView

from .base import RuContextMixin


class ConsultationCarteView(RuContextMixin, TemplateView):
    template_name = 'backoffice/consultation/carte.html'
    active_page   = 'consultation:carte'
    breadcrumbs   = [{'label': 'Consultation'}, {'label': 'Carte'}]


class ConsultationParcellesView(RuContextMixin, TemplateView):
    template_name = 'backoffice/consultation/parcelles.html'
    active_page   = 'consultation:parcelles'
    breadcrumbs   = [{'label': 'Consultation'}, {'label': 'Parcelles'}]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # TODO : remplacer par de vraies requêtes BDD
        ctx['nb_parcelles']         = 86590
        ctx['nb_en_modif']          = 123
        ctx['derniere_publication'] = None
        ctx['parcelles']            = []
        ctx['communes']             = ['75101', '75108', '75112', '75116']
        ctx['sections']             = ['AB', 'AC', 'BA', 'BB', 'CA']
        return ctx
