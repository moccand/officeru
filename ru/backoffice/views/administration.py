"""
backoffice/views/administration.py
────────────────────────────────────
Vues de la section Administration :
  - Utilisateurs, Groupes, Privilèges (liste + CRUD)
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group, Permission
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView

from ..forms import (
    GroupeForm,
    UtilisateurCreationForm,
    UtilisateurEditionForm,
)
from .base import GROUPES_SYSTEME, RuContextMixin, _admin_context, get_menu_alerts

User = get_user_model()


# ── Listes ────────────────────────────────────────────────────
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
        qs = Group.objects.annotate(nb_utilisateurs=Count('user')).order_by('name')
        q  = self.request.GET.get('q', '').strip()
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


# ── CRUD Utilisateur ──────────────────────────────────────────
class UtilisateurAjouterView(View):
    template_name = 'backoffice/administration/utilisateur_ajouter.html'

    def _ctx(self, request, form):
        return {
            **_admin_context(request, 'utilisateurs'),
            'form':                 form,
            'objet':                None,
            'titre':                'Nouvel utilisateur',
            'sous_titre':           "Création d'un nouveau compte utilisateur",
            'tous_les_groupes':     Group.objects.all(),
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


# ── CRUD Groupe ───────────────────────────────────────────────
class GroupeAjouterView(View):
    template_name = 'backoffice/administration/groupe_ajouter.html'

    def _ctx(self, request, form):
        return {
            **_admin_context(request, 'groupes'),
            'form':           form,
            'objet':          None,
            'titre':          'Nouveau groupe',
            'sous_titre':     "Création d'un nouveau groupe",
            'groupe_systeme': False,
        }

    def get(self, request):
        return render(request, self.template_name, self._ctx(request, GroupeForm()))

    def post(self, request):
        form = GroupeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Groupe créé avec succès.')
            return redirect('backoffice:administration_groupes')
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
            form.data       = form.data.copy()
            form.data['name'] = groupe.name
        if form.is_valid():
            form.save()
            messages.success(request, f'Groupe "{groupe.name}" modifié avec succès.')
            return redirect('backoffice:administration_groupes')
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
