from django import forms
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm

from core.models import RuVoie, RuAlignement, RuRegle, RuParcelle
from backoffice.models import GroupProfile

User = get_user_model()

COMMUNES_PARIS = [(i, f'750{str(i-75100).zfill(2)}')
                  for i in range(75101, 75121)]


class OptionalIntegerFormField(forms.IntegerField):
    """Chaîne vide du navigateur → None (évite l’erreur « Enter a whole number »)."""
    def to_python(self, value):
        if value in (None, ''):
            return None
        return super().to_python(value)


class RuVoieForm(forms.ModelForm):
    """
    id_voie est une clé primaire IntegerField sans auto-incrément (comme id_alignement).
    """
    use_required_attribute = False

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

    def save(self, commit=True):
        voie = super().save(commit=False)
        if voie.pk is None:
            max_id = RuVoie.objects.aggregate(m=Max('id_voie'))['m']
            voie.id_voie = (max_id or 0) + 1
        if commit:
            voie.save()
        return voie


class UtilisateurCreationForm(UserCreationForm):
    """Validation côté serveur uniquement (pas d'attribut HTML required / pas de validation navigateur)."""
    use_required_attribute = False

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'is_superuser', 'groups']


class UtilisateurEditionForm(forms.ModelForm):
    use_required_attribute = False

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
    use_required_attribute = False

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
    """
    Champs réellement obligatoires côté métier / affichage (*) : voie, parcelle,
    numéro début et numéro fin. Adresses et suffixes sont optionnels (le modèle
    recalcule souvent les adresses à l'enregistrement).
    """
    use_required_attribute = False

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Création : le modèle a default=0 sur les numéros → sans ça le formulaire affiche « 0 ».
        if self.instance.pk is None and not self.is_bound:
            self.initial['numero_debut'] = None
            self.initial['numero_fin'] = None
        # Le modèle n'a pas blank=True sur ces CharField → Django les marque « required »
        # alors qu'ils ne doivent pas porter l'astérisque ni bloquer la validation à vide.
        optional_char = (
            'adresse_debut', 'adresse_fin',
            'suffixe_un_debut', 'suffixe_2_debut', 'suffixe_3_debut',
            'suffixe_un_fin', 'suffixe_2_fin', 'suffixe_3_fin',
        )
        for name in optional_char:
            if name in self.fields:
                self.fields[name].required = False

    def save(self, commit=True):
        """
        id_alignement est une clé primaire IntegerField sans auto-incrément Django :
        il faut attribuer le prochain identifiant à la création.
        """
        alignement = super().save(commit=False)
        if alignement.pk is None:
            max_id = RuAlignement.objects.aggregate(m=Max('id_alignement'))['m']
            alignement.id_alignement = (max_id or 0) + 1
        if commit:
            alignement.save()
        return alignement


class RuRegleForm(forms.ModelForm):
    """
    id_regle : clé primaire sans auto-incrément (assignation au save à la création).
    Champ obligatoire métier affiché (*) : code. Les autres attributs sont optionnels en UX.
    """
    use_required_attribute = False

    class Meta:
        model = RuRegle
        fields = [
            'code', 'libelle', 'doc_urba', 'autorite', 'url_doc',
            'standard_cnig', 'type_cnig', 'code_cnig', 'sous_code_cnig',
            'cible', 'date', 'phrase_chatbot', 'type_cartads',
        ]
        widgets = {
            'libelle': forms.Textarea(attrs={'rows': 3, 'class': 'textarea textarea-bordered w-full text-sm'}),
            'phrase_chatbot': forms.Textarea(attrs={'rows': 4, 'class': 'textarea textarea-bordered w-full text-sm'}),
            'date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'input input-bordered w-full text-sm'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].required = True
        for name in self.Meta.fields:
            if name != 'code' and name in self.fields:
                self.fields[name].required = False

        self.fields['date'].input_formats = ['%Y-%m-%d']

        for _name, field in self.fields.items():
            if _name in ('libelle', 'phrase_chatbot', 'date'):
                continue
            w = field.widget
            if isinstance(w, forms.TextInput):
                w.attrs.setdefault('class', 'input input-bordered w-full text-sm')

    def save(self, commit=True):
        regle = super().save(commit=False)
        if regle.pk is None:
            max_id = RuRegle.objects.aggregate(m=Max('id_regle'))['m']
            regle.id_regle = (max_id or 0) + 1
        if commit:
            regle.save()
        return regle


class RuParcelleForm(forms.ModelForm):
    """
    id_parcelle : clé primaire sans auto-incrément (assignation au save à la création).
    Champ obligatoire métier affiché (*) : identifiant.
    """
    use_required_attribute = False

    class Meta:
        model = RuParcelle
        fields = [
            'identifiant', 'dep', 'insee_com', 'insee_com_absorbee',
            'section', 'numero', 'm2_dgfip', 'enclave', 'statut', 'date',
        ]
        widgets = {
            'date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'input input-bordered w-full text-sm'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identifiant'].required = True
        for name in self.Meta.fields:
            if name != 'identifiant' and name in self.fields:
                self.fields[name].required = False
        self.fields['date'].input_formats = ['%Y-%m-%d']

        num_cls = 'input input-bordered w-full text-sm'
        for name in ('dep', 'insee_com', 'm2_dgfip', 'enclave'):
            old = self.fields.get(name)
            if not old:
                continue
            self.fields[name] = OptionalIntegerFormField(
                label=old.label,
                required=False,
                widget=forms.NumberInput(attrs={'class': num_cls}),
                help_text=old.help_text,
            )

        for _name, field in self.fields.items():
            if _name in ('dep', 'insee_com', 'm2_dgfip', 'enclave', 'date'):
                continue
            w = field.widget
            if isinstance(w, forms.TextInput):
                w.attrs.setdefault('class', 'input input-bordered w-full text-sm')
            elif isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'select select-bordered w-full text-sm')

    def clean(self):
        cleaned = super().clean()
        for key in ('dep', 'insee_com', 'm2_dgfip'):
            if cleaned.get(key) is None:
                cleaned[key] = 0
        return cleaned

    def save(self, commit=True):
        parcelle = super().save(commit=False)
        if parcelle.pk is None:
            max_id = RuParcelle.objects.aggregate(m=Max('id_parcelle'))['m']
            parcelle.id_parcelle = (max_id or 0) + 1
        if commit:
            parcelle.save()
        return parcelle