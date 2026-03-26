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
import base64
import json

from django.db.models.functions import Coalesce

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.http import JsonResponse
from django.core.paginator import Paginator

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
        if onglet == 'valeurs' and regle.type_valeur == RuRegle.TypeValeur.PAS_DE_VALEUR:
            onglet = 'regle'
        form    = RuRegleForm(instance=regle)
        return render(request, self.template_name,
                      self._ctx(request, regle, form, onglet))

    def post(self, request, pk):
        regle  = get_object_or_404(RuRegle, pk=pk)
        onglet = 'regle'
        form   = RuRegleForm(request.POST, instance=regle)
        if form.is_valid():
            regle = form.save()
            messages.success(request, f'La règle « {regle.code} » a bien été enregistrée.')
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


class RegleTypeValeurByIdView(View):
    """
    Endpoint AJAX : récupère le type_valeur d'une règle.
    Utile pour recalibrer l'UI (champ Valeur) après re-render suite à des erreurs.
    """

    def get(self, request):
        regle_id = request.GET.get('id_regle', '').strip()
        if not regle_id.isdigit():
            return JsonResponse({'type_valeur': RuRegle.TypeValeur.PAS_DE_VALEUR})

        regle = get_object_or_404(RuRegle, pk=int(regle_id))
        return JsonResponse({'type_valeur': regle.type_valeur})


class RegleValeursAnalyseView(View):
    """
    Analyse des valeurs (uniquement pour SAISIE_LIBRE).
    Retour JSON des valeurs distinctes groupées par parcelle + valeur.
    """

    def get(self, request, pk):
        regle = get_object_or_404(RuRegle, pk=pk)

        if regle.type_valeur != RuRegle.TypeValeur.SAISIE_LIBRE:
            return JsonResponse({'disabled': True, 'rows': []})

        rows = {}

        # Group-by (règle, valeur) : une seule ligne par valeur.
        qs_detail = (
            RuDetail.objects
            .filter(id_regle_id=regle.pk)
            .values('valeur')
            .annotate(nb=Count('id_detail'))
        )
        for r in qs_detail:
            valeur = r['valeur']
            key = '__NULL__' if valeur is None else f'__VAL__{valeur}'
            rows[key] = {
                'valeur': valeur,
                'valeur_affiche': 'NULL' if valeur is None else ('(VIDE)' if valeur == '' else valeur),
                'nb_details': int(r['nb'] or 0),
            }

        qs_align = (
            RuDetailAlignement.objects
            .filter(id_regle_id=regle.pk)
            .values('valeur')
            .annotate(nb=Count('id_detail'))
        )
        for r in qs_align:
            valeur = r['valeur']
            key = '__NULL__' if valeur is None else f'__VAL__{valeur}'
            if key not in rows:
                rows[key] = {
                    'valeur': valeur,
                    'valeur_affiche': 'NULL' if valeur is None else ('(VIDE)' if valeur == '' else valeur),
                    'nb_details': 0,
                }
            rows[key]['nb_details'] += int(r['nb'] or 0)

        decoded_rows = []
        for data in rows.values():
            payload = {
                'is_null': data['valeur'] is None,
                'value': None if data['valeur'] is None else str(data['valeur']),
            }
            token = base64.urlsafe_b64encode(
                json.dumps(payload, ensure_ascii=True).encode('utf-8')
            ).decode('ascii')
            data['key'] = token
            decoded_rows.append(data)

        sort = request.GET.get('sort', 'valeur').strip()
        dire = request.GET.get('dir', 'asc').strip().lower()
        reverse = (dire == 'desc')

        if sort == 'impact':
            decoded_rows.sort(key=lambda x: int(x.get('nb_details') or 0), reverse=reverse)
        else:
            # valeur : NULL puis texte (ordre alpha)
            decoded_rows.sort(
                key=lambda x: (
                    x.get('valeur') is not None,
                    str(x.get('valeur', '')).lower(),
                ),
                reverse=reverse,
            )

        per_page_raw = request.GET.get('per_page', '25').strip()
        page_raw = request.GET.get('page', '1').strip()
        per_page = int(per_page_raw) if per_page_raw in ('25', '50', '100') else 25
        page_num = int(page_raw) if page_raw.isdigit() else 1

        paginator = Paginator(decoded_rows, per_page)
        page_obj = paginator.get_page(page_num)

        return JsonResponse({
            'disabled': False,
            'rows': list(page_obj.object_list),
            'pagination': {
                'page': page_obj.number,
                'per_page': per_page,
                'num_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            },
            'sort': sort if sort in ('valeur', 'impact') else 'valeur',
            'dir': 'desc' if reverse else 'asc',
        })


class RegleValeursSupprimerView(View):
    """
    Suppression groupée des détails de valeurs (uniquement SAISIE_LIBRE).
    Cette suppression n'impacte ni la règle ni la parcelle.
    """

    def post(self, request, pk):
        regle = get_object_or_404(RuRegle, pk=pk)

        selected_keys = request.POST.getlist('selected_keys')
        if not selected_keys:
            messages.error(request, 'Aucune valeur sélectionnée.')
            return redirect(f'{reverse("backoffice:regle_edit", args=[regle.pk])}?onglet=valeurs&analyze=1')

        # On ne bloque pas strictement la requête côté serveur,
        # mais c'est l'UI qui appelle ce endpoint pour SAISIE_LIBRE.
        to_delete = []
        for token in selected_keys:
            try:
                raw = base64.urlsafe_b64decode(token.encode('ascii')).decode('utf-8')
                payload = json.loads(raw)
                to_delete.append({
                    'is_null': bool(payload.get('is_null')),
                    'value': payload.get('value'),
                })
            except Exception:
                # Compat anciens tokens (valeur brute encodée)
                try:
                    valeur = base64.urlsafe_b64decode(token.encode('ascii')).decode('utf-8')
                    to_delete.append({'is_null': False, 'value': valeur})
                except Exception:
                    continue

        if not to_delete:
            messages.error(request, 'Sélection invalide.')
            return redirect(f'{reverse("backoffice:regle_edit", args=[regle.pk])}?onglet=valeurs&analyze=1')

        # Suppression : RuDetail + RuDetailAlignement.
        # Les détails (SET_DEFAULT sur FK côté parcelle/alignement) garantissent
        # qu'on ne supprime ni la règle ni la parcelle.
        nb_detail_deleted = 0
        nb_align_deleted = 0

        for item in to_delete:
            if item['is_null']:
                nb_detail_deleted += RuDetail.objects.filter(
                    id_regle_id=regle.pk,
                    valeur__isnull=True,
                ).delete()[0]
                nb_align_deleted += RuDetailAlignement.objects.filter(
                    id_regle_id=regle.pk,
                    valeur__isnull=True,
                ).delete()[0]
            else:
                nb_detail_deleted += RuDetail.objects.filter(
                    id_regle_id=regle.pk,
                    valeur=item['value'],
                ).delete()[0]
                nb_align_deleted += RuDetailAlignement.objects.filter(
                    id_regle_id=regle.pk,
                    valeur=item['value'],
                ).delete()[0]

        messages.success(
            request,
            f"Valeurs supprimées : {nb_detail_deleted} détail(s) et {nb_align_deleted} détail(s) d'alignement.",
            extra_tags='quick-dismiss',
        )
        return redirect(f'{reverse("backoffice:regle_edit", args=[regle.pk])}?onglet=valeurs&analyze=1')
