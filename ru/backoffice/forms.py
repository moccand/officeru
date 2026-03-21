from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm

from core.models import RuVoie, RuAlignement
from backoffice.models import GroupProfile

User = get_user_model()

COMMUNES_PARIS = [(i, f'750{str(i-75100).zfill(2)}')
                  for i in range(75101, 75121)]


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



class AlignementForm(forms.ModelForm):

    commune = forms.ChoiceField(
        choices=[('', '— Sélectionner —')] + [(str(c[0]), c[1]) for c in COMMUNES_PARIS],
        required=False,
    )

    parite = forms.ChoiceField(
        choices=[
            ('', '— Sélectionner —'),
            ('False', 'Impair'),
            ('True',  'Pair'),
        ],
        required=False,
    )


    class Meta:
        model  = RuAlignement
        fields = [
            'id_voie', 'id_parcelle',
            'numero_debut', 'adresse_debut',
            'suffixe_un_debut', 'suffixe_2_debut', 'suffixe_3_debut',
            'numero_fin', 'adresse_fin',
            'suffixe_un_fin', 'suffixe_2_fin', 'suffixe_3_fin',
            'parite', 'commune', 'date',
        ]