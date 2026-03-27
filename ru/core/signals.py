import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RuAlignement, RuDetail, RuDetailAlignement, RuParcelle, RuRegle, RuVoie


logger = logging.getLogger('core')
TRACKED_MODELS = (RuVoie, RuParcelle, RuAlignement, RuRegle, RuDetail, RuDetailAlignement)


@receiver(post_save, dispatch_uid='core_log_model_changes')
def log_core_model_changes(sender, instance, created, raw=False, update_fields=None, **kwargs):
    if raw or sender not in TRACKED_MODELS:
        return

    action = 'CREATE' if created else 'UPDATE'
    model_name = instance._meta.label
    if update_fields:
        fields = ','.join(sorted(update_fields))
        logger.info('%s %s pk=%s fields=%s', action, model_name, instance.pk, fields)
    else:
        logger.info('%s %s pk=%s', action, model_name, instance.pk)
