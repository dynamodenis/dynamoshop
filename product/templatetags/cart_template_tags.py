from django import template
from product.models import Order

register = template.Library()

@register.filter

def cart_item_count(user):
    if user.is_authenticated:
        order = Order.objects.filter(user = user, ordered = False)
        if order.exists():
            return order[0].items.count()
    return 0