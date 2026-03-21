from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm
from core.models import RuVoie

from backoffice.models import GroupProfile

User = get_user_model()

class RuVoieForm(forms.ModelForm):
    class Meta:
        model  = RuVoie
        fields = [
            'libelle_long',
            'libelle_court',
            'code_voie_ville',
            'code_voie_rivoli',
            'voie_privee',
            'date',
        ]

class UtilisateurCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'is_superuser', 'groups']


class UtilisateurEditionForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'is_superuser', 'groups']


class GroupeForm(forms.ModelForm):
    """
    Formulaire pour le modèle Group Django.
    On retire les permissions (gérées via GroupRequiredMixin)
    et on ajoute la description via GroupProfile.
    """
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Description',
        help_text='Décrit le rôle de ce groupe dans l\'application.',
    )

    class Meta:
        model  = Group
        fields = ['name']   # permissions retirées volontairement

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-remplir la description depuis GroupProfile si le groupe existe
        if self.instance and self.instance.pk:
            try:
                self.fields['description'].initial = self.instance.profile.description
            except GroupProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        group = super().save(commit=commit)
        if commit:
            # Créer ou mettre à jour le GroupProfile associé
            GroupProfile.objects.update_or_create(
                group=group,
                defaults={'description': self.cleaned_data.get('description', '')}
            )
        return group