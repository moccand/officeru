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

    path('consultation/troncons/',
         views.ConsultationTronconsView.as_view(),
         name='consultation_troncons'),

    # ── Gestion ──────────────────────────────────────────────────────
    path('gestion/mutations/',
         views.GestionMutationsView.as_view(),
         name='gestion_mutations'),

    path('gestion/parcelles/',
         views.GestionParcellesView.as_view(),
         name='gestion_parcelles'),

    path('gestion/parcelles/<int:pk>/',
         views.GestionParcelleDetailView.as_view(),
         name='gestion_parcelle_detail'),

    path('gestion/troncons/',
         views.GestionTronconsView.as_view(),
         name='gestion_troncons'),

    path('gestion/voies/',
         views.GestionVoiesView.as_view(),
         name='gestion_voies'),

    path('gestion/regles/',
         views.GestionReglesView.as_view(),
         name='gestion_regles'),

    path('gestion/listes-valeurs/',
         views.GestionListesValeursView.as_view(),
         name='gestion_listes_valeurs'),

    path('gestion/analyse-referentiels/',
         views.GestionAnalyseReferentielsView.as_view(),
         name='gestion_analyse_referentiels'),

    path('gestion/details/',
         views.GestionDetailsView.as_view(),
         name='gestion_details'),

    # ── Export ───────────────────────────────────────────────────────
    path('export/exports-internet/',
         views.ExportExportsInternetView.as_view(),
         name='export_exports_internet'),

    # ── Administration ───────────────────────────────────────────────
    path('administration/utilisateurs/',
         views.AdministrationUtilisateursView.as_view(),
         name='administration_utilisateurs'),

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
