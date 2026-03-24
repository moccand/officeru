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
