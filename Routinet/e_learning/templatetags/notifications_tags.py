from django import template
from e_learning.models import Notification

register = template.Library()


@register.simple_tag
def unread_notifications_count(user):
    if getattr(user, 'is_authenticated', False):
        return Notification.objects.filter(utilisateur=user, lu=False).count()
    return 0
