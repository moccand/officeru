"""
backoffice/views/gestion_voies.py
───────────────────────────────────
Vues CRUD pour les Voies + endpoint autocomplete.
"""
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView

from core.models import RuVoie

from ..forms import RuVoieForm
from .base import RuContextMixin, get_menu_alerts


class VoiesAutocompleteView(View):
    """
    Endpoint JSON pour l'autocomplétion du champ Voie.
    GET /api/voies-autocomplete/?q=rue+de
    """
    def get(self, request):
        q = request.GET.get('q', '').strip()
        if len(q) < 2:
            return JsonResponse({'results': []})

        voies = (
            RuVoie.objects
            .filter(
                Q(libelle_long__icontains=q)     |
                Q(libelle_court__icontains=q)    |
                Q(code_voie_rivoli__icontains=q) |
                Q(code_voie_ville__icontains=q)
            )
            .values('id_voie', 'libelle_long', 'code_voie_ville', 'code_voie_rivoli')
            [:15]
        )
        results = [
            {
                'id':    v['id_voie'],
                'label': v['libelle_long'] or str(v['id_voie']),
                'codes': f"{v['code_voie_ville']} — {v['code_voie_rivoli']}",
            }
            for v in voies
        ]
        return JsonResponse({'results': results})


class GestionVoiesView(ListView):
    template_name       = 'backoffice/gestion/voies.html'
    context_object_name = 'voies'
    paginate_by         = 25

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', '25')
        return int(per_page) if per_page in ('25', '50', '100') else 25

    def get_queryset(self):
        qs = RuVoie.objects.annotate(
            nb_alignements=Count('alignements')
        ).order_by('libelle_long')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(libelle_long__icontains=q)     |
                Q(libelle_court__icontains=q)    |
                Q(code_voie_rivoli__icontains=q) |
                Q(code_voie_ville__icontains=q)
            )

        voie_privee = self.request.GET.get('voie_privee', '')
        if voie_privee == 'oui':
            qs = qs.filter(voie_privee=1)
        elif voie_privee == 'non':
            qs = qs.filter(voie_privee=0)

        sort = self.request.GET.get('sort', 'libelle_long')
        dire = self.request.GET.get('dir', 'asc')
        cols = {
            'libelle_long', 'code_voie_ville', 'code_voie_rivoli',
            'voie_privee', 'date_creation', 'date_modification', 'nb_alignements',
        }
        if sort in cols:
            qs = qs.order_by(f'-{sort}' if dire == 'desc' else sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = 'gestion:voies'
        ctx['breadcrumbs'] = [{'label': 'Gestion'}, {'label': 'Voies'}]
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        return ctx


class GestionVoieEditView(View):
    template_name = 'backoffice/gestion/voie_edit.html'

    def get_context(self, request, voie, form):
        return {
            'voie':        voie,
            'form':        form,
            'active_page': 'gestion:voies',
            'breadcrumbs': [
                {'label': 'Gestion'},
                {'label': 'Référentiel des Voies', 'url': '/gestion/voies/'},
                {'label': voie.libelle_long or str(voie.pk)},
            ],
            'menu_alerts': get_menu_alerts(request),
        }

    def get(self, request, pk):
        voie = get_object_or_404(RuVoie, pk=pk)
        return render(request, self.template_name,
                      self.get_context(request, voie, RuVoieForm(instance=voie)))

    def post(self, request, pk):
        voie = get_object_or_404(RuVoie, pk=pk)
        form = RuVoieForm(request.POST, instance=voie)
        if form.is_valid():
            form.save()
            messages.success(request, f'La voie "{voie}" a été modifiée avec succès.')
            return redirect('backoffice:gestion_voies')
        return render(request, self.template_name,
                      self.get_context(request, voie, form))


class GestionVoieAjouterView(View):
    template_name = 'backoffice/gestion/voie_ajouter.html'

    def get_context(self, request, form):
        return {
            'voie':        None,
            'form':        form,
            'active_page': 'gestion:voies',
            'breadcrumbs': [
                {'label': 'Gestion'},
                {'label': 'Référentiel des Voies', 'url': '/gestion/voies/'},
                {'label': 'Nouvelle voie'},
            ],
            'menu_alerts': get_menu_alerts(request),
        }

    def get(self, request):
        return render(request, self.template_name,
                      self.get_context(request, RuVoieForm()))

    def post(self, request):
        form = RuVoieForm(request.POST)
        if form.is_valid():
            voie = form.save()
            messages.success(request, f'La voie "{voie}" a été créée avec succès.')
            return redirect('backoffice:gestion_voies')
        return render(request, self.template_name, self.get_context(request, form))


class GestionVoieDupliquerView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/voie_dupliquer.html'
    active_page   = 'gestion:voies'
    breadcrumbs   = [
        {'label': 'Gestion'},
        {'label': 'Référentiel des Voies', 'url': '/gestion/voies/'},
        {'label': 'Duplication'},
    ]


class GestionVoieSupprimerView(View):
    def post(self, request, pk):
        voie           = get_object_or_404(RuVoie, pk=pk)
        nb_alignements = voie.alignements.count()
        if nb_alignements > 0:
            messages.error(
                request,
                f'Impossible de supprimer la voie "{voie}" : '
                f'elle possède {nb_alignements} alignement'
                f'{"s" if nb_alignements > 1 else ""} associé'
                f'{"s" if nb_alignements > 1 else ""}.'
            )
            return redirect('backoffice:gestion_voies')
        voie.delete()
        messages.success(request, f'La voie "{voie}" a été supprimée avec succès.')
        return redirect('backoffice:gestion_voies')
