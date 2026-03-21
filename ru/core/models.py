from django.db import models

class RuParcelle(models.Model):

    class Statut(models.TextChoices):
        A_VALIDER = 'A_VALIDER', 'À valider'
        ACTIVE    = 'ACTIVE',    'Active'
        ARCHIVEE  = 'ARCHIVEE',  'Archivée'

    id_parcelle = models.IntegerField(primary_key=True)
    identifiant = models.CharField(max_length=50, default='')
    dep = models.IntegerField(default=0)
    insee_com = models.IntegerField(default=0)
    insee_com_absorbee = models.CharField(max_length=50, default='')
    section = models.CharField(max_length=50, default='')
    numero = models.CharField(max_length=50, default='')
    m2_dgfip = models.IntegerField(default=0)
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
    code_voie_rivoli = models.CharField(max_length=10, default='', null=False, blank=False)
    code_voie_ville = models.CharField(max_length=10, default='', null=False, blank=False)
    voie_privee =  models.BooleanField(default=False)
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
    numero_debut = models.IntegerField(default=0)
    adresse_debut = models.CharField(max_length=50, default='')
    suffixe_un_debut = models.CharField(max_length=50, default='')
    suffixe_2_debut = models.CharField(max_length=50, default='')
    suffixe_3_debut = models.CharField(max_length=50, default='')
    numero_fin = models.IntegerField(default=0)
    adresse_fin = models.CharField(max_length=50, default='')
    suffixe_un_fin = models.CharField(max_length=50, default='')
    suffixe_2_fin = models.CharField(max_length=50, default='')
    suffixe_3_fin = models.CharField(max_length=50, default='')
    id_voie = models.ForeignKey(
        RuVoie,
        on_delete=models.PROTECT, # ← Django lève une ProtectedError si on tente de supprimer
        default=0,
        db_column='id_voie',
        related_name='alignements'
    )
    parite = models.BooleanField(default=False)
    id_parcelle = models.ForeignKey(
        RuParcelle,
        on_delete=models.SET_DEFAULT,
        default=0,
        db_column='id_parcelle',
        related_name='alignements'
    )
    commune = models.IntegerField(default=0)
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ru_alignement'

    def __str__(self):
        return f'Alignement {self.id_alignement}'


class RuRegle(models.Model):
    id_regle = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=50, default='')
    libelle = models.TextField(null=True, blank=True)
    doc_urba = models.CharField(max_length=50, default='')
    autorite = models.CharField(max_length=50, default='')
    url_doc = models.CharField(max_length=255, default='')
    standard_cnig = models.CharField(max_length=50, default='')
    type_cnig = models.CharField(max_length=50, default='')
    code_cnig = models.CharField(max_length=50, default='')
    sous_code_cnig = models.CharField(max_length=50, default='')
    cible = models.CharField(max_length=50, default='')
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