"""
backoffice/urls.py
──────────────────
URLs de l'application backoffice.
À inclure dans ru/urls.py :

    from django.urls import path, include

    urlpatterns = [
        path('', include('backoffice.urls')),
        ...
    ]
"""
from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [

    # ── Page d'accueil ──────────────────────────────────────────────
    path('', views.HomeView.as_view(), name='home'),

    # ── Thème ────────────────────────────────────────────────────────
    path('set-theme/', views.set_theme, name='set_theme'),


    # ── Consultation ─────────────────────────────────────────────────
    path('consultation/carte/',
         views.ConsultationCarteView.as_view(),
         name='consultation_carte'),

    path('consultation/parcelles/',
         views.ConsultationParcellesView.as_view(),
         name='consultation_parcelles'),

    # ── Gestion ──────────────────────────────────────────────────────
    path('gestion/mutations/',
         views.GestionMutationsView.as_view(),
         name='gestion_mutations'),

    path('api/parcelles-autocomplete/',
        views.ParcellesAutocompleteView.as_view(),
        name='parcelles_autocomplete'),
    path('api/regles-parcelle-autocomplete/',
        views.ReglesParcelleAutocompleteView.as_view(),
        name='regles_parcelle_autocomplete'),
    path('api/regles-alignement-autocomplete/',
        views.ReglesAlignementAutocompleteView.as_view(),
        name='regles_alignement_autocomplete'),

    path('gestion/parcelles/',
         views.GestionParcellesView.as_view(),
         name='gestion_parcelles'),
    path('gestion/parcelles/ajouter/',
         views.ParcelleAjouterView.as_view(),
         name='parcelle_ajouter'),
    path('gestion/parcelles/<int:pk>/editer/',
         views.ParcelleEditView.as_view(),
         name='parcelle_edit'),
    path('gestion/parcelles/<int:pk>/supprimer/',
         views.ParcelleSupprimerView.as_view(),
         name='parcelle_supprimer'),

    # Alignements — /ajouter/ AVANT /<int:pk>/
    path('gestion/alignements/',
         views.GestionAlignementsView.as_view(),
         name='gestion_alignements'),
    path('gestion/alignements/ajouter/',
         views.AlignementAjouterView.as_view(),
         name='alignement_ajouter'),
    path('gestion/alignements/<int:pk>/editer/',
         views.AlignementEditView.as_view(),
         name='alignement_edit'),
    path('gestion/alignements/<int:pk>/supprimer/',
         views.AlignementSupprimerView.as_view(),
         name='alignement_supprimer'),

    # Autocomplete voies — endpoint JSON pour le champ voie
    path('api/voies-autocomplete/',
         views.VoiesAutocompleteView.as_view(),
         name='voies_autocomplete'),

    # Voies :
    path('gestion/voies/',
         views.GestionVoiesView.as_view(),
         name='gestion_voies'),
    path('gestion/voies/<int:pk>/editer/',
         views.GestionVoieEditView.as_view(),
         name='gestion_voie_edit'),
    path('gestion/voies/ajouter/',
         views.GestionVoieAjouterView.as_view(),
         name='gestion_voie_ajouter'),
    path('gestion/voies/<int:pk>/dupliquer/',
         views.GestionVoieDupliquerView.as_view(),
         name='gestion_voie_dupliquer'),
    path('gestion/voies/<int:pk>/supprimer/',
         views.GestionVoieSupprimerView.as_view(),
         name='gestion_voie_supprimer'),

    path('gestion/regles/',
         views.GestionReglesView.as_view(),
         name='gestion_regles'),
    path('gestion/regles/ajouter/',
         views.RegleAjouterView.as_view(),
         name='regle_ajouter'),
    path('gestion/regles/<int:pk>/editer/',
         views.RegleEditView.as_view(),
         name='regle_edit'),
    path('gestion/regles/<int:pk>/supprimer/',
         views.RegleSupprimerView.as_view(),
         name='regle_supprimer'),

    path('gestion/gestion-avancee/',
         views.GestionAvanceeView.as_view(),
         name='gestion_avancee'),

    path('gestion/analyse-referentiels/',
         views.GestionAnalyseReferentielsView.as_view(),
         name='gestion_analyse_referentiels'),

    # ── Export ───────────────────────────────────────────────────────
    path('export/exports-internet/',
         views.ExportExportsInternetView.as_view(),
         name='export_exports_internet'),

    # ── Administration ───────────────────────────────────────────────

# Administration utilisateurs
path('administration/utilisateurs/',
     views.AdministrationUtilisateursView.as_view(),
     name='administration_utilisateurs'),
path('administration/groupes/',
     views.AdministrationGroupesView.as_view(),
     name='administration_groupes'),
path('administration/privileges/',
     views.AdministrationPrivilegesView.as_view(),
     name='administration_privileges'),
path('administration/utilisateurs/ajouter/',
     views.UtilisateurAjouterView.as_view(),
     name='utilisateur_ajouter'),
path('administration/utilisateurs/<int:pk>/editer/',
     views.UtilisateurEditView.as_view(),
     name='utilisateur_edit'),
path('administration/utilisateurs/<int:pk>/supprimer/',
     views.UtilisateurSupprimerView.as_view(),
     name='utilisateur_supprimer'),
path('administration/groupes/ajouter/',
     views.GroupeAjouterView.as_view(),
     name='groupe_ajouter'),
path('administration/groupes/<int:pk>/editer/',
     views.GroupeEditView.as_view(),
     name='groupe_edit'),
path('administration/groupes/<int:pk>/supprimer/',
     views.GroupeSupprimerView.as_view(),
     name='groupe_supprimer'),

#Configuration
    path('administration/configuration/',
         views.AdministrationConfigurationView.as_view(),
         name='administration_configuration'),

    # ── API ──────────────────────────────────────────────────────────
    path('api/swagger/',
         views.ApiSwaggerView.as_view(),
         name='api_swagger'),
    path('api/configuration/',
         views.ApiConfigurationView.as_view(),
         name='api_configuration'),

]
