"""
backoffice/views/export_api.py
────────────────────────────────
Vues Export et API (Swagger).
"""
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from ..models import RuExport
from .base import RuContextMixin

_ONGLETS_API_SWAGGER = frozenset({'swagger', 'configuration'})


class ExportExportsInternetView(RuContextMixin, TemplateView):
    template_name = 'backoffice/export/exports_internet.html'
    active_page = 'export:exports_internet'
    breadcrumbs = [{'label': 'Export'}, {'label': 'Exports Internet'}]

    def _get_exports_queryset(self):
        qs = RuExport.objects.select_related('agent').order_by('-datetime_demande_export')
        q = (self.request.GET.get('q') or '').strip()
        if q:
            # Filtre sur tous les champs texte (y compris statut).
            qs = qs.filter(
                Q(agent__username__icontains=q)
                | Q(commentaire__icontains=q)
                | Q(nom_du_fichier__icontains=q)
                | Q(poids_du_fichier__icontains=q)
                | Q(statut__icontains=q)
            )
        return qs

    def get(self, request, *args, **kwargs):
        # Téléchargement : ?download=<pk>
        download_pk = request.GET.get('download')
        if download_pk:
            export = get_object_or_404(RuExport, pk=download_pk)
            if not export.nom_du_fichier:
                raise Http404('Fichier indisponible')

            exports_dir = Path(getattr(settings, 'RU_EXPORTS_DIR', Path(settings.BASE_DIR) / 'exports'))
            safe_name = Path(export.nom_du_fichier).name  # évite les traversées de répertoires
            export_path = (exports_dir / safe_name).resolve()
            try:
                exports_dir_resolved = exports_dir.resolve()
            except Exception:
                exports_dir_resolved = exports_dir

            if exports_dir_resolved not in export_path.parents and export_path != exports_dir_resolved:
                raise Http404('Chemin invalide')

            if not export_path.exists():
                raise Http404('Fichier introuvable')

            return FileResponse(open(export_path, 'rb'), as_attachment=True, filename=safe_name)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['exports'] = self._get_exports_queryset()

        export_en_cours_exists = RuExport.objects.filter(statut=RuExport.Statut.EN_COURS).exists()
        ctx['export_en_cours_exists'] = export_en_cours_exists
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'create_export':
            export_en_cours_exists = RuExport.objects.filter(statut=RuExport.Statut.EN_COURS).exists()
            if export_en_cours_exists:
                messages.error(
                    request,
                    'Il y a déjà un export en cours, attendre qu il se termine et recommencer.'
                )
                return redirect(request.path + ('?q=' + (request.GET.get('q') or '') if request.GET.get('q') else ''))

            commentaire_raw = request.POST.get('commentaire') or ''
            commentaire = commentaire_raw.strip() or None

            RuExport.objects.create(
                agent=request.user if request.user.is_authenticated else None,
                commentaire=commentaire,
                statut=RuExport.Statut.EN_COURS,
            )
            messages.success(request, 'Export créé.')
            return redirect(request.path)

        if action == 'delete_export_file':
            export_pk = request.POST.get('export_pk')
            export = get_object_or_404(RuExport, pk=export_pk)
            export.nom_du_fichier = None
            export.poids_du_fichier = None
            export.save(update_fields=['nom_du_fichier', 'poids_du_fichier'])
            messages.success(request, 'Fichier supprimé.')
            return redirect(request.path)

        if action == 'delete_export_line':
            export_pk = request.POST.get('export_pk')
            export = get_object_or_404(RuExport, pk=export_pk)
            export.delete()
            messages.success(request, "L export a été supprimé.")
            return redirect(request.path)

        messages.error(request, 'Action inconnue.')
        return redirect(request.path)


class ApiSwaggerView(RuContextMixin, TemplateView):
    template_name = 'backoffice/api/swagger.html'
    active_page   = 'api:swagger'
    breadcrumbs   = [{'label': 'API'}, {'label': 'Swagger et configuration'}]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        onglet = self.request.GET.get('onglet', 'swagger')
        ctx['onglet_actif'] = onglet if onglet in _ONGLETS_API_SWAGGER else 'swagger'
        return ctx
