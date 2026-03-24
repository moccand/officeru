from django.db import models

class RuParcelle(models.Model):

    class Statut(models.TextChoices):
        A_VALIDER = 'A_VALIDER', 'À valider'
        ACTIVE    = 'ACTIVE',    'Active'
        ARCHIVEE  = 'ARCHIVEE',  'Archivée'

    id_parcelle = models.IntegerField(primary_key=True)
    identifiant = models.CharField(max_length=50, blank=False, null=False)
    dep = models.IntegerField(blank=False, null=False)
    insee_com = models.IntegerField(blank=False, null=False)
    insee_com_absorbee = models.CharField(max_length=50, default='000', blank=True)
    section = models.CharField(max_length=50, blank=False, null=False)
    numero = models.CharField(max_length=50, blank=False, null=False)
    m2_dgfip = models.IntegerField(default=0, blank=True)
    enclave = models.SmallIntegerField(null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.A_VALIDER,
    )
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ru_parcelle'
        indexes = [
            models.Index(fields=['identifiant'], name='idx_ru_parcelle_identifiant'),
            models.Index(fields=['insee_com'], name='idx_ru_parcelle_insee_com'),
            models.Index(fields=['section'], name='idx_ru_parcelle_section'),
        ]

    def __str__(self):
        return f'{self.identifiant} ({self.id_parcelle})'


class RuVoie(models.Model):
    id_voie = models.IntegerField(primary_key=True)
    libelle_long = models.TextField(null=False, blank=False)
    libelle_court = models.TextField(null=False, blank=False)
    code_voie_rivoli = models.CharField(max_length=10, null=False, blank=False)
    code_voie_ville = models.CharField(max_length=10, default='', blank=True)
    voie_privee =  models.BooleanField(default=False, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ru_voie'
        indexes = [
            models.Index(fields=['libelle_long'], name='idx_ru_voie_libelle_long'),
        ]

    def __str__(self):
        return self.libelle_long or self.libelle_court or str(self.id_voie)


class RuAlignement(models.Model):
    id_alignement = models.IntegerField(primary_key=True)
    numero_debut = models.IntegerField(default=0, null=False, blank=False)
    adresse_debut = models.CharField(max_length=50, default='', blank=True)
    suffixe_un_debut = models.CharField(max_length=50, default='', blank=True)
    suffixe_2_debut = models.CharField(max_length=50, default='', blank=True)
    suffixe_3_debut = models.CharField(max_length=50, default='', blank=True)
    numero_fin = models.IntegerField(default=0, null=False, blank=False)
    adresse_fin = models.CharField(max_length=50, default='', blank=True)
    suffixe_un_fin = models.CharField(max_length=50, default='', blank=True)
    suffixe_2_fin = models.CharField(max_length=50, default='', blank=True)
    suffixe_3_fin = models.CharField(max_length=50, default='', blank=True)
    id_voie = models.ForeignKey(
        RuVoie,
        on_delete=models.PROTECT, # ← Django lève une ProtectedError si on tente de supprimer
        default=0,
        db_column='id_voie',
        related_name='alignements',
        null=False, blank=False
    )
    parite = models.BooleanField(default=False)
    id_parcelle = models.ForeignKey(
        RuParcelle,
        on_delete=models.SET_DEFAULT,
        default=0,
        db_column='id_parcelle',
        related_name='alignements',
        null=False, blank=False
    )
    commune = models.IntegerField(null=False, blank=False)
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ru_alignement'


    def _construire_adresse(self, numero, suffixe1, suffixe2, suffixe3):
        """Concatène numéro et suffixes en retirant les parties vides."""
        parties = [str(numero)] if numero else []
        for s in (suffixe1, suffixe2, suffixe3):
            if s and s.strip():
                parties.append(s.strip())
        return ' '.join(parties)

    def save(self, *args, **kwargs):
        self.adresse_debut = self._construire_adresse(
            self.numero_debut,
            self.suffixe_un_debut,
            self.suffixe_2_debut,
            self.suffixe_3_debut,
        )
        self.adresse_fin = self._construire_adresse(
            self.numero_fin,
            self.suffixe_un_fin,
            self.suffixe_2_fin,
            self.suffixe_3_fin,
        )
        super().save(*args, **kwargs)


    def __str__(self):
        voie = self.id_voie.libelle_long if self.id_voie_id else ''
        if self.adresse_debut == self.adresse_fin:
            return f'{self.adresse_debut}, {voie}'.strip(', ')
        return f'du {self.adresse_debut} au {self.adresse_fin}, {voie}'.strip(', ')


class RuRegle(models.Model):
    class TypeRegle(models.TextChoices):
        PARCELLE = 'PARCELLE', 'Parcelle'
        ALIGNEMENT = 'ALIGNEMENT', 'Alignement'

    id_regle = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=50, default='')
    type_regle = models.CharField(
        max_length=10,
        choices=TypeRegle.choices,
        null=False,
        blank=False,
        default=TypeRegle.PARCELLE,
    )
    libelle = models.TextField(null=True, blank=True)
    doc_urba = models.CharField(max_length=50, default='', blank=True)
    autorite = models.CharField(max_length=50, default='', blank=True)
    url_doc = models.CharField(max_length=255, default='', blank=True)
    standard_cnig = models.CharField(max_length=50, default='', blank=True)
    type_cnig = models.CharField(max_length=50, default='', blank=True)
    code_cnig = models.CharField(max_length=50, default='', blank=True)
    sous_code_cnig = models.CharField(max_length=50, default='', blank=True)
    cible = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(null=True, blank=True)
    phrase_chatbot = models.TextField(null=True, blank=True)
    type_cartads = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        db_table = 'ru_regle'
        indexes = [
            models.Index(fields=['libelle'], name='idx_ru_regle_libelle'),
            models.Index(fields=['code'], name='idx_ru_regle_code'),
        ]

    def __str__(self):
        return f'{self.code} - {self.libelle or ""}'


class RuDetail(models.Model):
    id_detail = models.IntegerField(primary_key=True)
    id_parcelle = models.ForeignKey(
        RuParcelle,
        on_delete=models.SET_DEFAULT,
        default=0,
        db_column='id_parcelle',
        related_name='details'
    )
    id_regle = models.ForeignKey(
        RuRegle,
        on_delete=models.SET_DEFAULT,
        default=0,
        db_column='id_regle',
        related_name='details'
    )
    valeur = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ru_detail'
        # Pour fusionner RuDetail et RuDetailAlignement sur une seule table :
        # 1. Supprimer cette classe et RuDetailAlignement
        # 2. Créer une unique classe RuDetail avec les deux FK (id_parcelle + id_alignement)
        # 3. Mettre db_table = 'ru_detail' sur cette classe unique
        # 4. Les deux FK peuvent être null=True, blank=True pour rester optionnelles

    def __str__(self):
        return f'Detail {self.id_detail}'


class RuDetailAlignement(models.Model):
    id_detail = models.IntegerField(primary_key=True)
    id_alignement = models.ForeignKey(
        RuAlignement,
        on_delete=models.SET_DEFAULT,
        default=0,
        db_column='id_alignement',
        related_name='details'
    )
    id_regle = models.ForeignKey(
        RuRegle,
        on_delete=models.SET_DEFAULT,
        default=0,
        db_column='id_regle',
        related_name='details_alignement'
    )
    valeur = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ru_detail_alignement'
        # Pour fusionner avec RuDetail sur une seule table :
        # Voir le commentaire dans RuDetail.Meta ci-dessus.
        # Il faudra aussi créer une migration qui :
        # - copie les données de ru_detail_alignement vers ru_detail
        # - ajoute la colonne id_alignement dans ru_detail
        # - supprime la table ru_detail_alignement

    def __str__(self):
        return f'DetailAlignement {self.id_detail}'