"""
backoffice/views/gestion_parcelles.py
───────────────────────────────────────
Vues CRUD pour les Parcelles + endpoint autocomplete.
"""
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from core.models import RuDetail, RuParcelle

from ..forms import RuParcelleForm
from .base import _parcelle_breadcrumbs, get_menu_alerts


class ParcellesAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        if len(q) < 2:
            return JsonResponse({'results': []})
        parcelles = (
            RuParcelle.objects
            .filter(identifiant__icontains=q)
            .values('id_parcelle', 'identifiant')
            [:15]
        )
        results = [
            {
                'id':    p['id_parcelle'],
                'label': str(p['identifiant']) if p['identifiant'] is not None else str(p['id_parcelle']),
                'codes': str(p['identifiant']) if p['identifiant'] is not None else '',
            }
            for p in parcelles
        ]
        return JsonResponse({'results': results})


class GestionParcellesView(ListView):
    template_name       = 'backoffice/gestion/parcelles.html'
    context_object_name = 'parcelles'
    paginate_by         = 25

    def get_queryset(self):
        qs = RuParcelle.objects.all().order_by('id_parcelle')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(identifiant__icontains=q)

        statut = self.request.GET.get('statut', '').strip()
        statuts_valides = {c[0] for c in RuParcelle.Statut.choices}
        if statut in statuts_valides:
            qs = qs.filter(statut=statut)

        sort = self.request.GET.get('sort', 'identifiant')
        dire = self.request.GET.get('dir', 'asc')
        cols = {'identifiant', 'insee_com', 'insee_com_absorbee', 'section', 'numero'}
        if sort in cols:
            qs = qs.order_by(f'-{sort}' if dire == 'desc' else sort)
        return qs

    def get_paginate_by(self, qs):
        v = self.request.GET.get('per_page', '25')
        return int(v) if v in ('25', '50', '100') else 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page']    = 'gestion:parcelles'
        ctx['breadcrumbs']    = [{'label': 'Gestion'}, {'label': 'Parcelles'}]
        ctx['menu_alerts']    = get_menu_alerts(self.request)
        ctx['statut_choices'] = RuParcelle.Statut.choices
        return ctx


class ParcelleAjouterView(View):
    template_name = 'backoffice/gestion/parcelle_ajouter.html'

    def _ctx(self, request, form):
        return {
            'active_page': 'gestion:parcelles',
            'breadcrumbs': _parcelle_breadcrumbs({'label': 'Nouvelle parcelle'}),
            'menu_alerts': get_menu_alerts(request),
            'form':        form,
        }

    def get(self, request):
        return render(request, self.template_name, self._ctx(request, RuParcelleForm()))

    def post(self, request):
        form = RuParcelleForm(request.POST)
        if form.is_valid():
            parcelle = form.save()
            return redirect('backoffice:parcelle_edit', pk=parcelle.pk)
        return render(request, self.template_name, self._ctx(request, form))


class ParcelleEditView(View):
    template_name = 'backoffice/gestion/parcelle_edit.html'

    def _details_regles_parcelle(self, parcelle):
        return list(
            RuDetail.objects.filter(id_parcelle=parcelle.pk)
            .order_by('id_detail')
            .values(
                'id_detail',
                'id_regle_id',
                'id_regle__code',
                'id_regle__libelle',
                'valeur',
                'date',
            )[:500]
        )

    def _ctx(self, request, parcelle, form, onglet, details_regles):
        return {
            'active_page':             'gestion:parcelles',
            'breadcrumbs':             _parcelle_breadcrumbs({'label': str(parcelle)}),
            'menu_alerts':             get_menu_alerts(request),
            'parcelle':                parcelle,
            'form':                    form,
            'onglet_actif':            onglet,
            'details_regles_parcelle': details_regles,
        }

    def _get_onglet(self, request):
        onglet = request.GET.get('onglet', 'parcelle')
        return onglet if onglet in ('parcelle', 'regles') else 'parcelle'

    def get(self, request, pk):
        parcelle = get_object_or_404(RuParcelle, pk=pk)
        onglet   = self._get_onglet(request)
        form     = RuParcelleForm(instance=parcelle)
        details  = self._details_regles_parcelle(parcelle)
        return render(request, self.template_name,
                      self._ctx(request, parcelle, form, onglet, details))

    def post(self, request, pk):
        parcelle = get_object_or_404(RuParcelle, pk=pk)
        onglet   = 'parcelle'
        form     = RuParcelleForm(request.POST, instance=parcelle)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('backoffice:parcelle_edit', args=[pk])}?onglet={onglet}"
            )
        details = self._details_regles_parcelle(parcelle)
        return render(request, self.template_name,
                      self._ctx(request, parcelle, form, onglet, details))


class ParcelleSupprimerView(View):
    def post(self, request, pk):
        parcelle = get_object_or_404(RuParcelle, pk=pk)
        label    = str(parcelle)
        parcelle.delete()
        messages.success(request, f'La parcelle « {label} » a été supprimée.')
        return redirect('backoffice:gestion_parcelles')
