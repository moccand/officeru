from django.contrib import admin
from .models import RuParcelle, RuVoie, RuAlignement, RuRegle, RuDetail, RuDetailAlignement

admin.site.register(RuParcelle)
admin.site.register(RuVoie)
admin.site.register(RuAlignement)
admin.site.register(RuRegle)
admin.site.register(RuDetail)
admin.site.register(RuDetailAlignement)
