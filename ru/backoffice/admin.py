from django.contrib import admin

from .models import GroupProfile, RuExport


@admin.register(GroupProfile)
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ('group', 'description')
    search_fields = ('group__name', 'description')


@admin.register(RuExport)
class RuExportAdmin(admin.ModelAdmin):
    @admin.display(description='agent')
    def agent_username(self, obj):
        return obj.agent.username if obj.agent else ''

    list_display = (
        'datetime_demande_export',
        'agent_username',
        'statut',
        'datetime_fin_export',
        'nom_du_fichier',
        'poids_du_fichier',
    )
    list_filter = ('statut',)
    search_fields = (
        'agent__username',
        'commentaire',
        'nom_du_fichier',
        'poids_du_fichier',
    )
    ordering = ('-datetime_demande_export',)
