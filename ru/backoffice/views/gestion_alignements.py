"""
backoffice/views/gestion_alignements.py
─────────────────────────────────────────
Vues CRUD pour les Alignements.
"""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from core.models import RuAlignement, RuParcelle, RuVoie

from ..forms import AlignementForm
from .base import _alignement_breadcrumbs, get_menu_alerts


def _alignement_parcelle_autocomplete_prefill(alignement):
    """
    Libellé / sous-ligne pour le bloc parcelle dans alignement_edit,
    en cohérence visuelle avec l'autocomplete.
    """
    pid = getattr(alignement, 'id_parcelle_id', None) or None
    if not pid:
        return {
            'parcelle_ac_visible': False,
            'parcelle_ac_label':   '',
            'parcelle_ac_codes':   '',
        }
    row = RuParcelle.objects.filter(pk=pid).values('id_parcelle', 'identifiant').first()
    if row:
        ident_val = row.get('identifiant')
        label = str(ident_val) if ident_val is not None else str(row['id_parcelle'])
        if not (label or '').strip():
            label = str(row['id_parcelle'])
        codes = str(ident_val) if ident_val is not None else ''
    else:
        label = str(pid)
        codes = ''
    return {
        'parcelle_ac_visible': True,
        'parcelle_ac_label':   label,
        'parcelle_ac_codes':   codes,
    }


class GestionAlignementsView(ListView):
    template_name       = 'backoffice/gestion/alignements.html'
    context_object_name = 'alignements'
    paginate_by         = 25

    def get_queryset(self):
        qs = RuAlignement.objects.select_related('id_voie').order_by('id_alignement')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(adresse_debut__icontains=q) |
                Q(adresse_fin__icontains=q)
            )
        voie_pk = self.request.GET.get('voie', '')
        if voie_pk:
            qs = qs.filter(id_voie=voie_pk)

        parite = self.request.GET.get('parite', '')
        if parite in ('0', '1', '2'):
            qs = qs.filter(parite=int(parite))

        sort = self.request.GET.get('sort', 'id_alignement')
        dire = self.request.GET.get('dir', 'asc')
        cols = {'id_alignement', 'id_voie', 'numero_debut',
                'numero_fin', 'parite', 'commune', 'date'}
        if sort in cols:
            qs = qs.order_by(f'-{sort}' if dire == 'desc' else sort)
        return qs

    def get_paginate_by(self, qs):
        v = self.request.GET.get('per_page', '25')
        return int(v) if v in ('25', '50', '100') else 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = 'gestion:alignements'
        ctx['breadcrumbs'] = [{'label': 'Gestion'}, {'label': 'Alignements'}]
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        voie_pk = self.request.GET.get('voie', '')
        if voie_pk:
            ctx['voie_filtree'] = RuVoie.objects.filter(pk=voie_pk).first()
        return ctx


class AlignementAjouterView(View):
    template_name = 'backoffice/gestion/alignement_ajouter.html'

    def _ctx(self, request, form, voie_initiale=None):
        return {
            'active_page':   'gestion:alignements',
            'breadcrumbs':   _alignement_breadcrumbs({'label': 'Nouvel alignement'}),
            'menu_alerts':   get_menu_alerts(request),
            'form':          form,
            'voie_initiale': voie_initiale,
        }

    def get(self, request):
        voie_initiale = None
        voie_pk = request.GET.get('voie', '')
        if voie_pk:
            voie_initiale = RuVoie.objects.filter(pk=voie_pk).first()
        form = AlignementForm(initial={'id_voie': voie_pk} if voie_pk else {})
        return render(request, self.template_name,
                      self._ctx(request, form, voie_initiale))

    def post(self, request):
        form = AlignementForm(request.POST)
        if form.is_valid():
            alignement = form.save()
            return redirect('backoffice:alignement_edit', pk=alignement.pk)
        voie_initiale = None
        voie_pk = request.POST.get('id_voie', '')
        if voie_pk:
            voie_initiale = RuVoie.objects.filter(pk=voie_pk).first()
        return render(request, self.template_name,
                      self._ctx(request, form, voie_initiale))


class AlignementEditView(View):
    template_name = 'backoffice/gestion/alignement_edit.html'

    def _ctx(self, request, alignement, form, onglet):
        ctx = {
            'active_page':  'gestion:alignements',
            'breadcrumbs':  [
                {'label': 'Gestion'},
                {'label': 'Alignements', 'url': reverse('backoffice:gestion_alignements')},
                {'label': str(alignement)},
            ],
            'menu_alerts':  get_menu_alerts(request),
            'alignement':   alignement,
            'form':         form,
            'onglet_actif': onglet,
        }
        ctx.update(_alignement_parcelle_autocomplete_prefill(alignement))
        return ctx

    def _get_onglet(self, request):
        onglet = request.GET.get('onglet', 'alignement')
        return onglet if onglet in ('alignement', 'regles') else 'alignement'

    def get(self, request, pk):
        alignement = get_object_or_404(
            RuAlignement.objects.select_related('id_voie', 'id_parcelle'),
            pk=pk,
        )
        onglet = self._get_onglet(request)
        form   = AlignementForm(instance=alignement)
        return render(request, self.template_name,
                      self._ctx(request, alignement, form, onglet))

    def post(self, request, pk):
        alignement = get_object_or_404(
            RuAlignement.objects.select_related('id_voie', 'id_parcelle'),
            pk=pk,
        )
        onglet = self._get_onglet(request)
        form   = AlignementForm(request.POST, instance=alignement)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('backoffice:alignement_edit', args=[pk])}?onglet={onglet}"
            )
        return render(request, self.template_name,
                      self._ctx(request, alignement, form, onglet))


class AlignementSupprimerView(View):
    def post(self, request, pk):
        alignement = get_object_or_404(RuAlignement, pk=pk)
        id_a       = alignement.id_alignement
        alignement.delete()
        messages.success(request, f'Alignement {id_a} supprimé.')
        return redirect('backoffice:gestion_alignements')
