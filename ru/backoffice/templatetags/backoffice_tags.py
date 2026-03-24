"""
backoffice/templatetags/backoffice_tags.py
──────────────────────────────────────────
Tags custom pour l'application backoffice RU.
Chargement dans les templates : {% load backoffice_tags %}
"""
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def ru_application_release() -> str:
    """Valeur de settings.APPLICATION_RELEASE (ex. v2.0), affichée en sidebar."""
    return getattr(settings, 'APPLICATION_RELEASE', '')


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Reconstruit la query string en remplaçant les clés indiquées,
    sans jamais dupliquer un paramètre.

    Usage dans un template :
        href="?{% url_replace page=1 %}"
        href="?{% url_replace sort='libelle' dir='asc' page=1 %}"

    Les clés non mentionnées sont conservées telles quelles.
    """
    request = context.get('request')
    if not request:
        return ''
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()


@register.simple_tag
def menu_alert(alerts: dict, page_id: str) -> str:
    """
    Affiche une puce d'alerte dans le menu sidebar.

    Usage :
        {% menu_alert menu_alerts "gestion:misesajour" %}

    alerts : dict passé par la view
        {"gestion:misesajour": True}   → point rouge animé
        {"gestion:misesajour": 3}      → badge numérique "3"
    """
    if not alerts or page_id not in alerts:
        return ''

    value = alerts[page_id]

    if value is True or value == 1:
        return (
            '<span class="ml-auto size-2 rounded-full bg-error shrink-0" '
            'style="animation:pulse 2s cubic-bezier(0.4,0,0.6,1) infinite;"></span>'
        )
    elif isinstance(value, int) and value > 1:
        label = str(value) if value <= 99 else '99+'
        return (
            f'<span class="ml-auto badge badge-error badge-xs '
            f'text-error-content font-semibold">{label}</span>'
        )
    return ''
