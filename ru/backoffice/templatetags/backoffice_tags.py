"""
backoffice/templatetags/backoffice_tags.py
──────────────────────────────────────────
Tags custom pour l'application backoffice RU.
Chargement dans les templates : {% load backoffice_tags %}
"""
from django import template

register = template.Library()


@register.simple_tag
def menu_alert(alerts: dict, page_id: str) -> str:
    """
    Affiche une puce d'alerte dans le menu sidebar.

    Usage :
        {% menu_alert menu_alerts "gestion:mutations" %}

    alerts : dict passé par la view
        {"gestion:mutations": True}   → point rouge animé
        {"gestion:mutations": 3}      → badge numérique "3"
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
