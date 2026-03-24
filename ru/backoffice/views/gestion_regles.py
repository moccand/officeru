"""
backoffice/views/gestion_regles.py
────────────────────────────────────
Vues CRUD pour les Règles.
"""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from core.models import RuDetail, RuRegle

from ..forms import RuRegleForm
from .base import _regle_breadcrumbs, get_menu_alerts


class GestionReglesView(ListView):
    template_name       = 'backoffice/gestion/regles.html'
    context_object_name = 'regles'
    paginate_by         = 25

    def get_queryset(self):
        qs = RuRegle.objects.all().order_by('id_regle')
        q  = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(code__icontains=q)
                | Q(libelle__icontains=q)
                | Q(phrase_chatbot__icontains=q)
            )
        sort = self.request.GET.get('sort', 'code')
        dire = self.request.GET.get('dir', 'asc')
        cols = {
            'code', 'libelle', 'doc_urba', 'autorite',
            'standard_cnig', 'type_cnig', 'code_cnig', 'sous_code_cnig',
        }
        if sort in cols:
            qs = qs.order_by(f'-{sort}' if dire == 'desc' else sort)
        return qs

    def get_paginate_by(self, qs):
        v = self.request.GET.get('per_page', '25')
        return int(v) if v in ('25', '50', '100') else 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = 'gestion:regles'
        ctx['breadcrumbs'] = [{'label': 'Gestion'}, {'label': 'Règles'}]
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        return ctx


class RegleAjouterView(View):
    template_name = 'backoffice/gestion/regle_ajouter.html'

    def _ctx(self, request, form):
        return {
            'active_page': 'gestion:regles',
            'breadcrumbs': _regle_breadcrumbs({'label': 'Nouvelle règle'}),
            'menu_alerts': get_menu_alerts(request),
            'form':        form,
        }

    def get(self, request):
        return render(request, self.template_name, self._ctx(request, RuRegleForm()))

    def post(self, request):
        form = RuRegleForm(request.POST)
        if form.is_valid():
            regle = form.save()
            return redirect('backoffice:regle_edit', pk=regle.pk)
        return render(request, self.template_name, self._ctx(request, form))


class RegleEditView(View):
    template_name = 'backoffice/gestion/regle_edit.html'

    def _ctx(self, request, regle, form, onglet, details):
        return {
            'active_page':    'gestion:regles',
            'breadcrumbs':    _regle_breadcrumbs({'label': str(regle)}),
            'menu_alerts':    get_menu_alerts(request),
            'regle':          regle,
            'form':           form,
            'onglet_actif':   onglet,
            'details_regle':  details,
        }

    def _get_onglet(self, request):
        onglet = request.GET.get('onglet', 'regle')
        return onglet if onglet in ('regle', 'valeurs') else 'regle'

    def _details(self, regle):
        return list(
            RuDetail.objects.filter(id_regle=regle.pk)
            .order_by('id_detail')
            .values(
                'id_detail',
                'id_parcelle_id',
                'id_parcelle__identifiant',
                'valeur',
                'date',
            )[:500]
        )

    def get(self, request, pk):
        regle   = get_object_or_404(RuRegle, pk=pk)
        onglet  = self._get_onglet(request)
        form    = RuRegleForm(instance=regle)
        details = self._details(regle)
        return render(request, self.template_name,
                      self._ctx(request, regle, form, onglet, details))

    def post(self, request, pk):
        regle  = get_object_or_404(RuRegle, pk=pk)
        onglet = 'regle'
        form   = RuRegleForm(request.POST, instance=regle)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('backoffice:regle_edit', args=[pk])}?onglet={onglet}"
            )
        details = self._details(regle)
        return render(request, self.template_name,
                      self._ctx(request, regle, form, onglet, details))


class RegleSupprimerView(View):
    def post(self, request, pk):
        regle = get_object_or_404(RuRegle, pk=pk)
        label = str(regle)
        regle.delete()
        messages.success(request, f'La règle « {label} » a été supprimée.')
        return redirect('backoffice:gestion_regles')
