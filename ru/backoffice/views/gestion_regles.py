"""
backoffice/views/gestion_regles.py
────────────────────────────────────
Vues CRUD pour les Règles.
"""
from django.contrib import messages
from django.db.models import (
    Case,
    Count,
    ExpressionWrapper,
    F,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from core.models import RuDetail, RuDetailAlignement, RuRegle

from ..forms import RuRegleForm
from .base import _regle_breadcrumbs, get_menu_alerts


class GestionReglesView(ListView):
    template_name       = 'backoffice/gestion/regles.html'
    context_object_name = 'regles'
    paginate_by         = 25

    def get_queryset(self):
        # Sous-requêtes : deux Count() sur des relations différentes provoquent
        # des jointures qui faussaient nb_ru_detail (ex. règle alignement sans RuDetail).
        nb_detail_sq = (
            RuDetail.objects.filter(id_regle_id=OuterRef('pk'))
            .values('id_regle_id')
            .annotate(_c=Count('id_detail'))
            .values('_c')[:1]
        )
        nb_align_sq = (
            RuDetailAlignement.objects.filter(id_regle_id=OuterRef('pk'))
            .values('id_regle_id')
            .annotate(_c=Count('id_detail'))
            .values('_c')[:1]
        )
        qs = (
            RuRegle.objects.annotate(
                nb_ru_detail=Coalesce(
                    Subquery(nb_detail_sq, output_field=IntegerField()),
                    Value(0),
                ),
                nb_ru_detail_alignement=Coalesce(
                    Subquery(nb_align_sq, output_field=IntegerField()),
                    Value(0),
                ),
            )
            .annotate(
                # Affichage : ne montrer les détails parcelle que pour type PARCELLE,
                # et les détails alignement que pour type ALIGNEMENT (évite 1/1 trompeur).
                nb_detail_affiche_parcelle=Case(
                    When(
                        type_regle=RuRegle.TypeRegle.PARCELLE,
                        then=F('nb_ru_detail'),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                nb_detail_affiche_alignement=Case(
                    When(
                        type_regle=RuRegle.TypeRegle.ALIGNEMENT,
                        then=F('nb_ru_detail_alignement'),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
            .annotate(
                nb_details_lies=ExpressionWrapper(
                    F('nb_detail_affiche_parcelle')
                    + F('nb_detail_affiche_alignement'),
                    output_field=IntegerField(),
                ),
            )
            .all()
            .order_by('id_regle')
        )
        q  = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(code__icontains=q)
                | Q(libelle__icontains=q)
                | Q(phrase_chatbot__icontains=q)
            )
        type_regle = self.request.GET.get('type_regle', '').strip()
        type_regles_valides = {c[0] for c in RuRegle.TypeRegle.choices}
        if type_regle in type_regles_valides:
            qs = qs.filter(type_regle=type_regle)
        sort = self.request.GET.get('sort', 'code')
        dire = self.request.GET.get('dir', 'asc')
        cols = {
            'code', 'type_regle', 'libelle', 'doc_urba', 'autorite',
            'date_creation', 'date_modification', 'nb_details_lies',
        }
        if sort in cols:
            primary = f'-{sort}' if dire == 'desc' else sort
            # Tri stable pour la pagination (évite les lignes qui « sautent »).
            qs = qs.order_by(primary, 'id_regle')
        return qs

    def get_paginate_by(self, qs):
        v = self.request.GET.get('per_page', '25')
        return int(v) if v in ('25', '50', '100') else 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = 'gestion:regles'
        ctx['breadcrumbs'] = [{'label': 'Gestion'}, {'label': 'Règles'}]
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        ctx['type_regle_choices'] = RuRegle.TypeRegle.choices
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

    def _ctx(self, request, regle, form, onglet):
        return {
            'active_page':  'gestion:regles',
            'breadcrumbs':  _regle_breadcrumbs({'label': str(regle)}),
            'menu_alerts':  get_menu_alerts(request),
            'regle':        regle,
            'form':         form,
            'onglet_actif': onglet,
        }

    def _get_onglet(self, request):
        onglet = request.GET.get('onglet', 'regle')
        return onglet if onglet in ('regle', 'valeurs') else 'regle'

    def get(self, request, pk):
        regle   = get_object_or_404(RuRegle, pk=pk)
        onglet  = self._get_onglet(request)
        form    = RuRegleForm(instance=regle)
        return render(request, self.template_name,
                      self._ctx(request, regle, form, onglet))

    def post(self, request, pk):
        regle  = get_object_or_404(RuRegle, pk=pk)
        onglet = 'regle'
        form   = RuRegleForm(request.POST, instance=regle)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('backoffice:regle_edit', args=[pk])}?onglet={onglet}"
            )
        return render(request, self.template_name,
                      self._ctx(request, regle, form, onglet))


class RegleSupprimerView(View):
    def post(self, request, pk):
        regle = get_object_or_404(RuRegle, pk=pk)
        label = str(regle)
        regle.delete()
        messages.success(request, f'La règle « {label} » a été supprimée.')
        return redirect('backoffice:gestion_regles')
