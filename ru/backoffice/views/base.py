"""
backoffice/views/base.py
────────────────────────
Infrastructure partagée : constantes, mixin, helpers contexte,
vue thème et page d'accueil.
"""
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

User = get_user_model()

# ── Constantes ───────────────────────────────────────────────
GROUPES_SYSTEME = {'ADMINISTRATEUR_TECH', 'ADMINISTRATEUR_FONC', 'EDITEUR', 'VALIDATEUR', 'API_USER'}
ALLOWED_THEMES  = {'light', 'dark', 'colorblind'}


# ── Alertes menu ─────────────────────────────────────────────
def get_menu_alerts(request) -> dict:
    """
    Retourne les alertes à afficher dans le menu sidebar.
    À enrichir avec de vraies requêtes BDD.
    """
    return {
        # "gestion:mutations": True,
    }


# ── Mixin contexte commun ────────────────────────────────────
class RuContextMixin:
    """
    Injecte active_page, breadcrumbs et menu_alerts dans le contexte
    de toutes les views du backoffice.
    """
    active_page = ''
    breadcrumbs = []

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = self.active_page
        ctx['breadcrumbs'] = self.breadcrumbs
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        return ctx


# ── Helpers breadcrumbs ───────────────────────────────────────
def _alignement_breadcrumbs(extra=None):
    crumbs = [
        {'label': 'Gestion'},
        {'label': 'Alignements', 'url': '/gestion/alignements/'},
    ]
    if extra:
        crumbs.append(extra)
    return crumbs


def _regle_breadcrumbs(extra=None):
    crumbs = [
        {'label': 'Gestion'},
        {'label': 'Règles', 'url': reverse('backoffice:gestion_regles')},
    ]
    if extra:
        crumbs.append(extra)
    return crumbs


def _parcelle_breadcrumbs(extra=None):
    crumbs = [
        {'label': 'Gestion'},
        {'label': 'Parcelles', 'url': reverse('backoffice:gestion_parcelles')},
    ]
    if extra:
        crumbs.append(extra)
    return crumbs


def _admin_context(request, onglet):
    return {
        'active_page':     'administration:utilisateurs',
        'breadcrumbs':     [{'label': 'Administration'}, {'label': 'Utilisateurs'}],
        'menu_alerts':     get_menu_alerts(request),
        'onglet_actif':    onglet,
        'nb_utilisateurs': User.objects.count(),
        'nb_groupes':      Group.objects.count(),
    }


# ── Thème ─────────────────────────────────────────────────────
def set_theme(request):
    """POST /set-theme/ — persiste le thème en session."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data  = json.loads(request.body)
        theme = data.get('theme', 'light')
        if theme in ALLOWED_THEMES:
            request.session['ru_theme'] = theme
        return JsonResponse({'ok': True, 'theme': theme})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'invalid body'}, status=400)


# ── Accueil ───────────────────────────────────────────────────
class HomeView(TemplateView):
    """Redirige vers la page par défaut selon le statut d'authentification."""
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('backoffice:consultation_carte')
        return redirect('backoffice:consultation_carte')
