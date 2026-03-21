from django.db import models

from django.contrib.auth.models import Group

class GroupProfile(models.Model):
    """
    Extension du modèle Group de Django via une relation OneToOne.
    Permet d'ajouter des champs sans toucher au modèle Group natif.
    Compatible avec toutes les montées de version Django.
    """
    group       = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Groupe',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Description',
        help_text='Décrit le rôle de ce groupe dans l\'application.',
    )

    class Meta:
        verbose_name        = 'Profil de groupe'
        verbose_name_plural = 'Profils de groupes'

    def __str__(self):
        return f'Profil — {self.group.name}'
