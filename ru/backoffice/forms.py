from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm

from core.models import RuVoie, RuAlignement, RuRegle, RuParcelle
from backoffice.models import GroupProfile

User = get_user_model()

COMMUNES_PARIS = [(i, f'750{str(i-75100).zfill(2)}')
                  for i in range(75101, 75121)]


# ═══════════════════════════════════════════════════════════
# MIXIN — champs obligatoires dérivés du modèle
# ═══════════════════════════════════════════════════════════

class RuModelFormMixin:
    """
    Dérive automatiquement `required` depuis les contraintes du modèle.

    Règle : un champ de formulaire est required si et seulement si
    le champ modèle correspondant a blank=False ET null=False.

    Cela évite de coder en dur les champs obligatoires dans chaque
    formulaire : la source de vérité est le modèle.

    Désactive l'attribut HTML5 `required` (validation serveur uniquement).
    """
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self._meta.model
        for field_name, form_field in self.fields.items():
            try:
                model_field = model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # Champ ajouté manuellement sur le formulaire (ChoiceField…) :
                # on lit quand même la contrainte si un champ de même nom existe
                # dans le modèle (ex. ForeignKey avec _id suffix).
                continue
            blank = getattr(model_field, 'blank', True)
            null  = getattr(model_field, 'null',  True)
            form_field.required = (not blank) and (not null)


# ═══════════════════════════════════════════════════════════
# FORMULAIRES
# ═══════════════════════════════════════════════════════════

class RuVoieForm(RuModelFormMixin, forms.ModelForm):
    """
    Modèle RuVoie — champs obligatoires dérivés automatiquement.
    Champs requis (blank=False, null=False) : libelle_long, libelle_court,
    code_voie_rivoli.
    """
    class Meta:
        model  = RuVoie
        fields = [
            'libelle_long',
            'libelle_court',
            'code_voie_ville',
            'code_voie_rivoli',
            'voie_privee',
        ]

    def save(self, commit=True):
        voie = super().save(commit=False)
        if voie.pk is None:
            max_id = RuVoie.objects.aggregate(m=Max('id_voie'))['m']
            voie.id_voie = (max_id or 0) + 1
        if commit:
            voie.save()
        return voie


class AlignementForm(RuModelFormMixin, forms.ModelForm):
    """
    Modèle RuAlignement.
    Champs requis (blank=False, null=False) : id_voie, id_parcelle,
    numero_debut, numero_fin, commune.
    Les champs adresse_* et suffixe_* sont blank=True dans le modèle
    (calculés automatiquement par RuAlignement.save()).
    """
    commune = forms.ChoiceField(
        choices=[('', '— Sélectionner —')] + [(str(c[0]), c[1]) for c in COMMUNES_PARIS],
        required=False,  # sera écrasé par le mixin (null=False, blank=False)
    )

    parite = forms.ChoiceField(
        choices=[
            ('', '— Sélectionner —'),
            ('False', 'Impair'),
            ('True',  'Pair'),
        ],
        required=False,  # sera écrasé par le mixin
    )

    class Meta:
        model  = RuAlignement
        fields = [
            'id_voie', 'id_parcelle',
            'numero_debut', 'adresse_debut',
            'suffixe_un_debut', 'suffixe_2_debut', 'suffixe_3_debut',
            'numero_fin', 'adresse_fin',
            'suffixe_un_fin', 'suffixe_2_fin', 'suffixe_3_fin',
            'parite', 'commune',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer le « 0 » par défaut sur les numéros pour un formulaire vierge
        if self.instance.pk is None and not self.is_bound:
            self.initial['numero_debut'] = None
            self.initial['numero_fin']   = None

    def save(self, commit=True):
        alignement = super().save(commit=False)
        if alignement.pk is None:
            max_id = RuAlignement.objects.aggregate(m=Max('id_alignement'))['m']
            alignement.id_alignement = (max_id or 0) + 1
        if commit:
            alignement.save()
        return alignement


class RuRegleForm(RuModelFormMixin, forms.ModelForm):
    """
    Modèle RuRegle.
    Champ requis (blank=False, null=False) : code.
    Tous les autres champs ont blank=True ou null=True dans le modèle.
    """
    class Meta:
        model = RuRegle
        fields = [
            'code', 'type_regle', 'type_valeur', 'libelle', 'doc_urba', 'autorite', 'url_doc',
            'standard_cnig', 'type_cnig', 'code_cnig', 'sous_code_cnig',
            'cible', 'phrase_chatbot', 'type_cartads',
        ]
        widgets = {
            'libelle': forms.Textarea(attrs={
                'rows': 3, 'class': 'textarea textarea-bordered w-full text-sm',
            }),
            'phrase_chatbot': forms.Textarea(attrs={
                'rows': 4, 'class': 'textarea textarea-bordered w-full text-sm',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer les classes DaisyUI aux champs texte simples
        for name, field in self.fields.items():
            if name in ('libelle', 'phrase_chatbot'):
                continue
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.setdefault('class', 'input input-bordered w-full text-sm')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'select select-bordered w-full text-sm')

    def save(self, commit=True):
        regle = super().save(commit=False)
        if regle.pk is None:
            max_id = RuRegle.objects.aggregate(m=Max('id_regle'))['m']
            regle.id_regle = (max_id or 0) + 1
        if commit:
            regle.save()
        return regle


class RuParcelleForm(RuModelFormMixin, forms.ModelForm):
    """
    Modèle RuParcelle.
    Champs requis (blank=False, null=False) : identifiant, dep, insee_com,
    section, numero.
    Champs optionnels : insee_com_absorbee (blank=True, default='000'),
    m2_dgfip (blank=True, default=0), enclave (null=True).
    Les dates création / modification sont gérées par le modèle.
    """
    class Meta:
        model = RuParcelle
        fields = [
            'identifiant', 'dep', 'insee_com', 'insee_com_absorbee',
            'section', 'numero', 'm2_dgfip', 'enclave', 'statut',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer les classes DaisyUI selon le type de widget
        num_cls = 'input input-bordered w-full text-sm'
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.TextInput):
                w.attrs.setdefault('class', 'input input-bordered w-full text-sm')
            elif isinstance(w, forms.NumberInput):
                w.attrs.setdefault('class', num_cls)
            elif isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'select select-bordered w-full text-sm')

    def clean(self):
        cleaned = super().clean()
        # m2_dgfip est blank=True mais null=False dans le modèle :
        # une valeur vide du formulaire doit être coercée en 0 (valeur neutre).
        if cleaned.get('m2_dgfip') is None:
            cleaned['m2_dgfip'] = 0
        return cleaned

    def save(self, commit=True):
        parcelle = super().save(commit=False)
        if parcelle.pk is None:
            max_id = RuParcelle.objects.aggregate(m=Max('id_parcelle'))['m']
            parcelle.id_parcelle = (max_id or 0) + 1
        if commit:
            parcelle.save()
        return parcelle


class RuDetailParcelleAddForm(forms.Form):
    """
    Petit formulaire d'ajout de RuDetail depuis l'onglet
    « Règles sur la parcelle ».
    """
    use_required_attribute = False

    id_regle = forms.IntegerField(required=True, widget=forms.HiddenInput())
    regle_search = forms.CharField(required=False)
    valeur = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full text-sm',
            'placeholder': 'Valeur libre…',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['regle_search'].widget.attrs.update({
            'class': 'grow bg-transparent text-sm text-base-content placeholder:text-base-content/30 min-w-0',
            'style': 'outline:none;box-shadow:none;border:none;',
            'placeholder': 'Rechercher une règle (code ou libellé)…',
            'autocomplete': 'off',
            'aria-autocomplete': 'list',
            'aria-controls': 'detail-regle-suggestions',
        })

    def clean_id_regle(self):
        regle_id = self.cleaned_data.get('id_regle')
        exists = RuRegle.objects.filter(pk=regle_id, type_regle=RuRegle.TypeRegle.PARCELLE).exists()
        if not exists:
            raise forms.ValidationError("Veuillez sélectionner une règle via l'autocomplétion.")
        return regle_id

    def clean_valeur(self):
        """
        Rendu serveur du comportement côté UI selon `RuRegle.type_valeur`.
        - PAS DE VALEUR => valeur ignorée
        - SAISIE LIBRE => valeur acceptée (optionnelle)
        - LISTE FIXE => valeur obligatoire (sélection non vide)
        """
        regle_id = self.cleaned_data.get('id_regle')
        valeur = self.cleaned_data.get('valeur') or ''

        type_valeur = RuRegle.objects.filter(pk=regle_id).values_list('type_valeur', flat=True).first()
        if type_valeur == RuRegle.TypeValeur.PAS_DE_VALEUR:
            return ''
        if type_valeur == RuRegle.TypeValeur.LISTE_FIXE:
            if not (valeur or '').strip():
                raise forms.ValidationError("Veuillez sélectionner une valeur dans la liste.")
            return valeur.strip()
        # SAISIE_LIBRE (ou valeur inconnue) : on laisse passer
        return (valeur or '').strip()


class RuDetailAlignementAddForm(forms.Form):
    """Ajout de RuDetailAlignement depuis l'onglet « Règles sur l'alignement »."""

    use_required_attribute = False

    id_regle = forms.IntegerField(required=True, widget=forms.HiddenInput())
    regle_search = forms.CharField(required=False)
    valeur = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full text-sm',
            'placeholder': 'Valeur libre…',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['regle_search'].widget.attrs.update({
            'class': 'grow bg-transparent text-sm text-base-content placeholder:text-base-content/30 min-w-0',
            'style': 'outline:none;box-shadow:none;border:none;',
            'placeholder': 'Rechercher une règle (code ou libellé)…',
            'autocomplete': 'off',
            'aria-autocomplete': 'list',
            'aria-controls': 'detail-alignement-regle-suggestions',
        })

    def clean_id_regle(self):
        regle_id = self.cleaned_data.get('id_regle')
        exists = RuRegle.objects.filter(pk=regle_id, type_regle=RuRegle.TypeRegle.ALIGNEMENT).exists()
        if not exists:
            raise forms.ValidationError("Veuillez sélectionner une règle via l'autocomplétion.")
        return regle_id

    def clean_valeur(self):
        regle_id = self.cleaned_data.get('id_regle')
        valeur = self.cleaned_data.get('valeur') or ''

        type_valeur = RuRegle.objects.filter(pk=regle_id).values_list('type_valeur', flat=True).first()
        if type_valeur == RuRegle.TypeValeur.PAS_DE_VALEUR:
            return ''
        if type_valeur == RuRegle.TypeValeur.LISTE_FIXE:
            if not (valeur or '').strip():
                raise forms.ValidationError("Veuillez sélectionner une valeur dans la liste.")
            return valeur.strip()
        return (valeur or '').strip()


# ═══════════════════════════════════════════════════════════
# FORMULAIRES UTILISATEURS / GROUPES (inchangés)
# ═══════════════════════════════════════════════════════════

class UtilisateurCreationForm(UserCreationForm):
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
    use_required_attribute = False

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Description',
        help_text="Décrit le rôle de ce groupe dans l'application.",
    )

    class Meta:
        model  = Group
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                self.fields['description'].initial = self.instance.profile.description
            except GroupProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        group = super().save(commit=commit)
        if commit:
            GroupProfile.objects.update_or_create(
                group=group,
                defaults={'description': self.cleaned_data.get('description', '')}
            )
        return group
