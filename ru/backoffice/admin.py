from django.contrib import admin

from .models import GroupProfile, RuExport


@admin.register(GroupProfile)
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ('group', 'description')
    search_fields = ('group__name', 'description')


@admin.register(RuExport)
class RuExportAdmin(admin.ModelAdmin):
    list_display = (
        'datetime_demande_export',
        'login_agent',
        'statut',
        'datetime_fin_export',
        'nom_du_fichier',
        'poids_du_fichier',
    )
    list_filter = ('statut',)
    search_fields = (
        'login_agent',
        'commentaire',
        'nom_du_fichier',
        'poids_du_fichier',
    )
    ordering = ('-datetime_demande_export',)
