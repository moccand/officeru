"""
backoffice/views/__init__.py
─────────────────────────────
Réexporte toutes les vues depuis les sous-modules.
urls.py continue d'utiliser « from . import views » sans modification.
"""

from .base import (
    GROUPES_SYSTEME,
    ALLOWED_THEMES,
    get_menu_alerts,
    RuContextMixin,
    set_theme,
    HomeView,
    _alignement_breadcrumbs,
    _regle_breadcrumbs,
    _parcelle_breadcrumbs,
    _admin_context,
)

from .consultation import (
    ConsultationCarteView,
    ConsultationParcellesView,
    ConsultationTronconsView,
)

from .gestion_misc import (
    GestionMutationsView,
    GestionAnalyseReferentielsView,
    GestionDetailsView,
)

from .gestion_parcelles import (
    ParcellesAutocompleteView,
    ReglesParcelleAutocompleteView,
    GestionParcellesView,
    ParcelleAjouterView,
    ParcelleEditView,
    ParcelleSupprimerView,
)

from .gestion_alignements import (
    _alignement_parcelle_autocomplete_prefill,
    GestionAlignementsView,
    AlignementAjouterView,
    AlignementEditView,
    AlignementSupprimerView,
)

from .gestion_regles import (
    GestionReglesView,
    RegleAjouterView,
    RegleEditView,
    RegleSupprimerView,
)

from .gestion_voies import (
    VoiesAutocompleteView,
    GestionVoiesView,
    GestionVoieEditView,
    GestionVoieAjouterView,
    GestionVoieDupliquerView,
    GestionVoieSupprimerView,
)

from .export_api import (
    ExportExportsInternetView,
    ApiSwaggerView,
    ApiConfigurationView,
)

from .administration import (
    AdministrationConfigurationView,
    AdministrationUtilisateursView,
    AdministrationGroupesView,
    AdministrationPrivilegesView,
    UtilisateurAjouterView,
    UtilisateurEditView,
    UtilisateurSupprimerView,
    GroupeAjouterView,
    GroupeEditView,
    GroupeSupprimerView,
)

__all__ = [
    # base
    'GROUPES_SYSTEME', 'ALLOWED_THEMES', 'get_menu_alerts',
    'RuContextMixin', 'set_theme', 'HomeView',
    '_alignement_breadcrumbs', '_regle_breadcrumbs', '_parcelle_breadcrumbs',
    '_admin_context',
    # consultation
    'ConsultationCarteView', 'ConsultationParcellesView', 'ConsultationTronconsView',
    # gestion misc
    'GestionMutationsView', 'GestionAnalyseReferentielsView', 'GestionDetailsView',
    # gestion parcelles
    'ParcellesAutocompleteView', 'ReglesParcelleAutocompleteView', 'GestionParcellesView',
    'ParcelleAjouterView', 'ParcelleEditView', 'ParcelleSupprimerView',
    # gestion alignements
    '_alignement_parcelle_autocomplete_prefill',
    'GestionAlignementsView', 'AlignementAjouterView',
    'AlignementEditView', 'AlignementSupprimerView',
    # gestion règles
    'GestionReglesView', 'RegleAjouterView', 'RegleEditView', 'RegleSupprimerView',
    # gestion voies
    'VoiesAutocompleteView', 'GestionVoiesView',
    'GestionVoieEditView', 'GestionVoieAjouterView',
    'GestionVoieDupliquerView', 'GestionVoieSupprimerView',
    # export / api
    'ExportExportsInternetView', 'ApiSwaggerView', 'ApiConfigurationView',
    # administration
    'AdministrationConfigurationView',
    'AdministrationUtilisateursView', 'AdministrationGroupesView',
    'AdministrationPrivilegesView',
    'UtilisateurAjouterView', 'UtilisateurEditView', 'UtilisateurSupprimerView',
    'GroupeAjouterView', 'GroupeEditView', 'GroupeSupprimerView',
]
