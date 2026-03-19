"""
backoffice/views.py
───────────────────
Toutes les vues de l'application backoffice RU.

Chaque view injecte dans le contexte :
  active_page  — identifiant "groupe:page" utilisé par la sidebar
  breadcrumbs  — liste de dict [{label, url?}] pour la navbar
  menu_alerts  — dict d'alertes de menu (via get_menu_alerts())
"""
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

ALLOWED_THEMES = {'light', 'dark', 'colorblind'}


def get_menu_alerts(request) -> dict:
    """
    Retourne les alertes à afficher dans le menu sidebar.
    À enrichir avec de vraies requêtes BDD.

    Exemple :
        {"gestion:mutations": 3}  → badge "3" sur Mutations
        {"gestion:mutations": True} → point rouge animé
    """
    # TODO : remplacer par de vraies requêtes, ex:
    # from .models import Mutation
    # nb = Mutation.objects.filter(statut='en_attente').count()
    return {
        # "gestion:mutations": True,  # décommenter pour activer
    }


class RuContextMixin:
    """
    Mixin à ajouter à toutes les views du backoffice.
    Injecte active_page, breadcrumbs et menu_alerts dans le contexte.
    """
    active_page = ''   # surcharger dans chaque view
    breadcrumbs = []   # surcharger dans chaque view

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = self.active_page
        ctx['breadcrumbs'] = self.breadcrumbs
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        return ctx


# ═══════════════════════════════════════════════════════════
# THÈME
# ═══════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════
class HomeView(TemplateView):
    """Redirige vers la page par défaut selon le statut d'authentification."""
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('backoffice:gestion_parcelles')
        return redirect('backoffice:consultation_carte')


# ═══════════════════════════════════════════════════════════
# CONSULTATION
# ═══════════════════════════════════════════════════════════


class ConsultationCarteView(RuContextMixin, TemplateView):
    """
    Page carte cadastrale — accessible visiteur et connecté.
    """
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
        ctx['communes']             = ['75101','75108','75112','75116']
        ctx['sections']             = ['AB','AC','BA','BB','CA']
        return ctx


class ConsultationTronconsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/consultation/troncons.html'
    active_page   = 'consultation:troncons'
    breadcrumbs   = [{'label': 'Consultation'}, {'label': 'Tronçons'}]


# ═══════════════════════════════════════════════════════════
# GESTION
# ═══════════════════════════════════════════════════════════

class GestionMutationsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/mutations.html'
    active_page   = 'gestion:mutations'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Mutations'}]


class GestionParcellesView(RuContextMixin, TemplateView):
    """
    Page principale de gestion des parcelles (= dashboard.html).
    """
    template_name = 'backoffice/gestion/parcelles.html'
    active_page   = 'gestion:parcelles'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Parcelles'}]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # TODO : remplacer par de vraies requêtes + pagination Django
        ctx['nb_parcelles']         = 86590
        ctx['nb_en_modif']          = 123
        ctx['derniere_publication'] = None   # ex: date.today()
        ctx['parcelles']            = []     # ex: Parcelle.objects.all()
        ctx['page_obj']             = None
        ctx['communes']             = ['75101','75108','75112','75116']
        ctx['sections']             = ['AB','AC','BA','BB','CA']
        return ctx


class GestionParcelleDetailView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/parcelle_detail.html'
    active_page   = 'gestion:parcelles'
    breadcrumbs   = [
        {'label': 'Gestion'},
        {'label': 'Parcelles', 'url': '/gestion/parcelles/'},
        {'label': 'Détail'},
    ]


class GestionTronconsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/troncons.html'
    active_page   = 'gestion:troncons'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Tronçons'}]


class GestionVoiesView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/voies.html'
    active_page   = 'gestion:voies'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Référentiel des Voies'}]


class GestionReglesView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/regles.html'
    active_page   = 'gestion:regles'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Règles'}]


class GestionListesValeursView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/listes_valeurs.html'
    active_page   = 'gestion:listes_valeurs'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Listes de Valeurs des Règles'}]


class GestionAnalyseReferentielsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/analyse_referentiels.html'
    active_page   = 'gestion:analyse_referentiels'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Analyse des Référentiels'}]


class GestionDetailsView(RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/details.html'
    active_page   = 'gestion:details'
    breadcrumbs   = [{'label': 'Gestion'}, {'label': 'Détails'}]


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

class ExportExportsInternetView(RuContextMixin, TemplateView):
    template_name = 'backoffice/export/exports_internet.html'
    active_page   = 'export:exports_internet'
    breadcrumbs   = [{'label': 'Export'}, {'label': 'Exports Internet'}]


# ═══════════════════════════════════════════════════════════
# ADMINISTRATION
# ═══════════════════════════════════════════════════════════

class AdministrationUtilisateursView(RuContextMixin, TemplateView):
    template_name = 'backoffice/administration/utilisateurs.html'
    active_page   = 'administration:utilisateurs'
    breadcrumbs   = [{'label': 'Administration'}, {'label': 'Utilisateurs'}]


class AdministrationConfigurationView(RuContextMixin, TemplateView):
    template_name = 'backoffice/administration/configuration.html'
    active_page   = 'administration:configuration'
    breadcrumbs   = [{'label': 'Administration'}, {'label': 'Configuration'}]


# ═══════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════

class ApiSwaggerView(RuContextMixin, TemplateView):
    template_name = 'backoffice/api/swagger.html'
    active_page   = 'api:swagger'
    breadcrumbs   = [{'label': 'API'}, {'label': 'Swagger'}]


class ApiConfigurationView(RuContextMixin, TemplateView):
    template_name = 'backoffice/api/configuration.html'
    active_page   = 'api:configuration'
    breadcrumbs   = [{'label': 'API'}, {'label': "Configuration de l'API"}]
