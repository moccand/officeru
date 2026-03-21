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
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AdminPasswordChangeForm

from django.db.models import Q, Count

# import des modèles pour accéder aux données
from core.models import RuVoie

User = get_user_model()

from .forms import (
    RuVoieForm,
    UtilisateurCreationForm,
    UtilisateurEditionForm,
    GroupeForm,
)

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

# Groupes système — non supprimables et nom non modifiable
GROUPES_SYSTEME = {'ADMINISTRATEUR_TECH', 'ADMINISTRATEUR_FONC', 'EDITEUR', 'VALIDATEUR'}

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

    # prépare le dictionnaire de variables transmis au template pour le rendu
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

    # prépare le dictionnaire de variables transmis au template pour le rendu
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


class GestionAlignementsView(ListView):
    template_name = 'backoffice/gestion/alignements.html'
    context_object_name = 'alignements'
    paginate_by = 25

    def get_queryset(self):
        from core.models import RuAlignement
        qs = RuAlignement.objects.all().order_by('id_alignement')

        # Filtre sur la voie — passé en GET depuis le lien dans voies.html
        voie_pk = self.request.GET.get('voie', '')
        if voie_pk:
            qs = qs.filter(id_voie=voie_pk)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = 'gestion:alignements'
        ctx['breadcrumbs'] = [
            {'label': 'Gestion'},
            {'label': 'Alignements'},
        ]
        ctx['menu_alerts'] = get_menu_alerts(self.request)
        # Passer la voie filtrée au contexte pour l'afficher dans le titre
        voie_pk = self.request.GET.get('voie', '')
        if voie_pk:
            from core.models import RuVoie
            ctx['voie_filtree'] = RuVoie.objects.filter(pk=voie_pk).first()
        return ctx

class GestionVoiesView(ListView):
    template_name       = 'backoffice/gestion/voies.html'
    context_object_name = 'voies'
    paginate_by         = 25
    def get_paginate_by(self, queryset):
        """Permet à l'utilisateur de choisir 25, 50 ou 100 lignes par page."""
        per_page = self.request.GET.get('per_page', '25')
        if per_page in ('25', '50', '100'):
            return int(per_page)
        return 25

    def get_queryset(self):
        qs = RuVoie.objects.annotate(
            nb_alignements=Count('alignements')  # 'alignements' = related_name sur RuAlignement
        ).order_by('libelle_long')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(libelle_long__icontains=q) |
                Q(libelle_court__icontains=q) |
                Q(code_voie_rivoli__icontains=q) |
                Q(code_voie_ville__icontains=q)
            )

        voie_privee = self.request.GET.get('voie_privee', '')
        if voie_privee == 'oui':
            qs = qs.filter(voie_privee=1)
        elif voie_privee == 'non':
            qs = qs.filter(voie_privee=0)

        sort = self.request.GET.get('sort', 'libelle_long')
        direction = self.request.GET.get('dir', 'asc')
        colonnes_autorisees = {
            'libelle_long', 'code_voie_ville',
            'code_voie_rivoli', 'voie_privee', 'date',
            'nb_alignements'  # ← ajouter pour permettre le tri
        }
        if sort in colonnes_autorisees:
            qs = qs.order_by(f'-{sort}' if direction == 'desc' else sort)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_page'] = 'gestion:voies'
        ctx['breadcrumbs'] = [{'label': 'Gestion'}, {'label': 'Référentiel des Voies'}]
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
        form = RuVoieForm(instance=voie)
        return render(request, self.template_name, self.get_context(request, voie, form))

    def post(self, request, pk):
        voie = get_object_or_404(RuVoie, pk=pk)
        form = RuVoieForm(request.POST, instance=voie)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'La voie "{voie}" a été modifiée avec succès.'
            )
            return redirect('backoffice:gestion_voies')
        messages.error(
            request,
            'La modification a échoué. Veuillez corriger les erreurs ci-dessous.'
        )
        return render(request, self.template_name, self.get_context(request, voie, form))

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
        form = RuVoieForm()
        return render(request, self.template_name, self.get_context(request, form))

    def post(self, request):
        form = RuVoieForm(request.POST)
        if form.is_valid():
            voie = form.save()
            messages.success(
                request,
                f'La voie "{voie}" a été créée avec succès.'
            )
            return redirect('backoffice:gestion_voies')
        messages.error(
            request,
            'La création a échoué. Veuillez corriger les erreurs ci-dessous.'
        )
        return render(request, self.template_name, self.get_context(request, form))

class GestionVoieDupliquerView( RuContextMixin, TemplateView):
    template_name = 'backoffice/gestion/voie_dupliquer.html'
    active_page   = 'gestion:voies'
    breadcrumbs   = [
        {'label': 'Gestion'},
        {'label': 'Référentiel des Voies', 'url': '/gestion/voies/'},
        {'label': 'Duplication'},
    ]

class GestionVoieSupprimerView(View):
    def post(self, request, pk):
        voie = get_object_or_404(RuVoie, pk=pk)

        # Vérifier si la voie a des alignements
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
        messages.success(
            request,
            f'La voie "{voie}" a été supprimée avec succès.'
        )
        return redirect('backoffice:gestion_voies')


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
# ADMINISTRATION - Configuration
# ═══════════════════════════════════════════════════════════

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



# ═══════════════════════════════════════════════════════════
# ADMINISTRATION - Utlisateurs
# ═══════════════════════════════════════════════════════════

# ── Helpers ──────────────────────────────────────────────────

def _admin_context(request, onglet):
    return {
        'active_page':       'administration:utilisateurs',
        'breadcrumbs':       [{'label': 'Administration'}, {'label': 'Utilisateurs'}],
        'menu_alerts':       get_menu_alerts(request),
        'onglet_actif':      onglet,
        'nb_utilisateurs':   User.objects.count(),
        'nb_groupes':        Group.objects.count(),
    }


# ── Listes ───────────────────────────────────────────────────

class AdministrationUtilisateursView(ListView):
    template_name       = 'backoffice/administration/utilisateurs.html'
    context_object_name = 'object_list'
    paginate_by         = 25

    def get_queryset(self):
        qs = User.objects.all().order_by('username')
        q  = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q)   |
                Q(email__icontains=q)      |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        actif = self.request.GET.get('actif', '')
        if actif in ('0', '1'):
            qs = qs.filter(is_active=actif == '1')
        staff = self.request.GET.get('staff', '')
        if staff in ('0', '1'):
            qs = qs.filter(is_staff=staff == '1')
        sort = self.request.GET.get('sort', 'username')
        dire = self.request.GET.get('dir', 'asc')
        cols = {'username', 'last_name', 'first_name', 'email',
                'is_active', 'is_staff', 'date_joined'}
        if sort in cols:
            qs = qs.order_by(f'-{sort}' if dire == 'desc' else sort)
        return qs

    def get_paginate_by(self, qs):
        v = self.request.GET.get('per_page', '25')
        return int(v) if v in ('25', '50', '100') else 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_admin_context(self.request, 'utilisateurs'))
        ctx['add_url']   = reverse('backoffice:utilisateur_ajouter')
        ctx['add_label'] = 'Ajouter un utilisateur'
        return ctx


class AdministrationGroupesView(ListView):
    template_name       = 'backoffice/administration/utilisateurs.html'
    context_object_name = 'object_list'
    paginate_by         = 25

    def get_queryset(self):
        qs = Group.objects.annotate(
            nb_utilisateurs=Count('user')
        ).order_by('name')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        sort = self.request.GET.get('sort', 'name')
        dire = self.request.GET.get('dir', 'asc')
        if sort in {'name', 'nb_utilisateurs'}:
            qs = qs.order_by(f'-{sort}' if dire == 'desc' else sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_admin_context(self.request, 'groupes'))
        ctx['groupes_systeme'] = GROUPES_SYSTEME
        return ctx


class AdministrationPrivilegesView(TemplateView):
    template_name = 'backoffice/administration/utilisateurs.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_admin_context(self.request, 'privileges'))
        ctx['add_url']   = '#'
        ctx['add_label'] = 'Ajouter un privilège'
        return ctx


# ── CRUD Utilisateur ─────────────────────────────────────────

class UtilisateurAjouterView( View):
    template_name = 'backoffice/administration/utilisateur_ajouter.html'

    def _ctx(self, request, form):
        return {
            **_admin_context(request, 'utilisateurs'),
            'form':               form,
            'objet':              None,
            'titre':              'Nouvel utilisateur',
            'sous_titre':         'Création d\'un nouveau compte utilisateur',
            'tous_les_groupes':   Group.objects.all(),
            'groupes_selectionnes': [],
        }

    def get(self, request):
        return render(request, self.template_name,
                      self._ctx(request, UtilisateurCreationForm()))

    def post(self, request):
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès.')
            return redirect('backoffice:administration_utilisateurs')
        messages.error(request, 'Veuillez corriger les erreurs.')
        return render(request, self.template_name, self._ctx(request, form))


class UtilisateurEditView(View):
    template_name = 'backoffice/administration/utilisateur_edit.html'

    def _ctx(self, request, user, form):
        return {
            **_admin_context(request, 'utilisateurs'),
            'form':                 form,
            'objet':                user,
            'titre':                f'Éditer — {user.username}',
            'sous_titre':           'Modification du compte utilisateur',
            'tous_les_groupes':     Group.objects.all(),
            'groupes_selectionnes': list(user.groups.values_list('pk', flat=True)),
        }

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, self.template_name,
                      self._ctx(request, user, UtilisateurEditionForm(instance=user)))

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UtilisateurEditionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Utilisateur "{user}" modifié avec succès.')
            return redirect('backoffice:administration_utilisateurs')
        messages.error(request, 'Veuillez corriger les erreurs.')
        return render(request, self.template_name, self._ctx(request, user, form))


class UtilisateurSupprimerView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
            return redirect('backoffice:administration_utilisateurs')
        nom = str(user)
        user.delete()
        messages.success(request, f'Utilisateur "{nom}" supprimé.')
        return redirect('backoffice:administration_utilisateurs')


# ── CRUD Groupe ──────────────────────────────────────────────

class GroupeAjouterView(View):
    template_name = 'backoffice/administration/groupe_ajouter.html'

    def _ctx(self, request, form):
        return {
            **_admin_context(request, 'groupes'),
            'form':                     form,
            'objet':                    None,
            'titre':                    'Nouveau groupe',
            'sous_titre':               'Création d\'un nouveau groupe',
        }

    def get(self, request):
        return render(request, self.template_name, self._ctx(request, GroupeForm()))

    def post(self, request):
        form = GroupeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Groupe créé avec succès.')
            return redirect('backoffice:administration_groupes')
        messages.error(request, 'Veuillez corriger les erreurs.')
        return render(request, self.template_name, self._ctx(request, form))


class GroupeEditView(View):
    template_name = 'backoffice/administration/groupe_edit.html'

    def _ctx(self, request, groupe, form):
        return {
            **_admin_context(request, 'groupes'),
            'form':           form,
            'objet':          groupe,
            'titre':          f'Éditer — {groupe.name}',
            'sous_titre':     'Modification du groupe',
            'groupe_systeme': groupe.name in GROUPES_SYSTEME,
        }

    def get(self, request, pk):
        groupe = get_object_or_404(Group, pk=pk)
        return render(request, self.template_name,
                      self._ctx(request, groupe, GroupeForm(instance=groupe)))

    def post(self, request, pk):
        groupe = get_object_or_404(Group, pk=pk)
        form   = GroupeForm(request.POST, instance=groupe)

        if groupe.name in GROUPES_SYSTEME:
            # Forcer le nom original — ignorer ce que le formulaire a reçu
            form.data = form.data.copy()
            form.data['name'] = groupe.name

        if form.is_valid():
            form.save()
            messages.success(request, f'Groupe "{groupe.name}" modifié avec succès.')
            return redirect('backoffice:administration_groupes')
        messages.error(request, 'Veuillez corriger les erreurs.')
        return render(request, self.template_name, self._ctx(request, groupe, form))


class GroupeSupprimerView(View):
    def post(self, request, pk):
        groupe = get_object_or_404(Group, pk=pk)

        if groupe.name in GROUPES_SYSTEME:
            messages.error(
                request,
                f'Le groupe "{groupe.name}" est un groupe système et ne peut pas être supprimé.'
            )
            return redirect('backoffice:administration_groupes')

        nom = groupe.name
        groupe.delete()
        messages.success(request, f'Groupe "{nom}" supprimé.')
        return redirect('backoffice:administration_groupes')