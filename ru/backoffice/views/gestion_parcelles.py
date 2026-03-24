"""
backoffice/views/gestion_parcelles.py
───────────────────────────────────────
Vues CRUD pour les Parcelles + endpoint autocomplete.
"""
from django.contrib import messages
from django.db.models import Q
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from core.models import RuDetail, RuParcelle, RuRegle

from ..forms import RuParcelleForm, RuDetailParcelleAddForm
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


class ReglesParcelleAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        if len(q) < 2:
            return JsonResponse({'results': []})
        regles = (
            RuRegle.objects
            .filter(type_regle=RuRegle.TypeRegle.PARCELLE)
            .filter(Q(code__icontains=q) | Q(libelle__icontains=q))
            .values('id_regle', 'code', 'libelle')[:15]
        )
        results = [
            {
                'id': r['id_regle'],
                'label': r['code'] or str(r['id_regle']),
                'codes': r['libelle'] or '',
            }
            for r in regles
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

    def _details_regles_parcelle(self, request, parcelle):
        q = request.GET.get('q_detail', '').strip()
        qs = (
            RuDetail.objects
            .select_related('id_regle')
            .filter(
                id_parcelle=parcelle.pk,
                id_regle__type_regle='PARCELLE',
            )
        )
        if q:
            qs = qs.filter(
                Q(id_regle__phrase_chatbot__icontains=q)
                | Q(id_regle__libelle__icontains=q)
                | Q(id_regle__code__icontains=q)
                | Q(valeur__icontains=q)
            )
        return list(
            qs
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

    def _ctx(self, request, parcelle, form, onglet, details_regles, add_detail_form=None, show_add_detail_form=False):
        return {
            'active_page':             'gestion:parcelles',
            'breadcrumbs':             _parcelle_breadcrumbs({'label': str(parcelle)}),
            'menu_alerts':             get_menu_alerts(request),
            'parcelle':                parcelle,
            'form':                    form,
            'onglet_actif':            onglet,
            'details_regles_parcelle': details_regles,
            'add_detail_form':         add_detail_form or RuDetailParcelleAddForm(),
            'show_add_detail_form':    show_add_detail_form,
        }

    def _get_onglet(self, request):
        onglet = request.GET.get('onglet', 'parcelle')
        return onglet if onglet in ('parcelle', 'regles') else 'parcelle'

    def get(self, request, pk):
        parcelle = get_object_or_404(RuParcelle, pk=pk)
        onglet   = self._get_onglet(request)
        form     = RuParcelleForm(instance=parcelle)
        details  = self._details_regles_parcelle(request, parcelle)
        show_add_detail_form = request.GET.get('ajout') == '1' and onglet == 'regles'
        return render(request, self.template_name,
                      self._ctx(
                          request,
                          parcelle,
                          form,
                          onglet,
                          details,
                          add_detail_form=RuDetailParcelleAddForm(),
                          show_add_detail_form=show_add_detail_form,
                      ))

    def post(self, request, pk):
        parcelle = get_object_or_404(RuParcelle, pk=pk)
        if request.POST.get('action') == 'ajouter_detail':
            add_form = RuDetailParcelleAddForm(request.POST)
            if add_form.is_valid():
                max_id = RuDetail.objects.aggregate(m=Max('id_detail'))['m']
                RuDetail.objects.create(
                    id_detail=(max_id or 0) + 1,
                    id_parcelle=parcelle,
                    id_regle_id=add_form.cleaned_data['id_regle'],
                    valeur=add_form.cleaned_data.get('valeur', ''),
                    date=timezone.localdate(),
                )
                messages.success(
                    request,
                    "L'ajout du détail a bien été pris en compte.",
                    extra_tags='quick-dismiss',
                )
                return redirect(f"{reverse('backoffice:parcelle_edit', args=[pk])}?onglet=regles")
            details = self._details_regles_parcelle(request, parcelle)
            return render(
                request,
                self.template_name,
                self._ctx(
                    request,
                    parcelle,
                    RuParcelleForm(instance=parcelle),
                    'regles',
                    details,
                    add_detail_form=add_form,
                    show_add_detail_form=True,
                )
            )

        if request.POST.get('action') == 'supprimer_detail':
            detail_pk = request.POST.get('detail_pk')
            detail = get_object_or_404(
                RuDetail.objects.select_related('id_regle'),
                pk=detail_pk,
                id_parcelle=parcelle.pk,
                id_regle__type_regle='PARCELLE',
            )
            detail.delete()
            messages.error(request, f'La suppression du détail {detail_pk} a bien été prise en compte.')
            return redirect(f"{reverse('backoffice:parcelle_edit', args=[pk])}?onglet=regles")

        onglet   = 'parcelle'
        form     = RuParcelleForm(request.POST, instance=parcelle)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('backoffice:parcelle_edit', args=[pk])}?onglet={onglet}"
            )
        details = self._details_regles_parcelle(request, parcelle)
        return render(request, self.template_name,
                      self._ctx(request, parcelle, form, onglet, details))


class ParcelleSupprimerView(View):
    def post(self, request, pk):
        parcelle = get_object_or_404(RuParcelle, pk=pk)
        label    = str(parcelle)
        parcelle.delete()
        messages.success(request, f'La parcelle « {label} » a été supprimée.')
        return redirect('backoffice:gestion_parcelles')
