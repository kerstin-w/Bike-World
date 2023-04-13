from django import template


register = template.Library()


@register.filter(name='multiply_price_by_quantity')
def multiply_price_by_quantity(price, quantity):
    '''
    Template Filter that multiplies price and quantity
    '''
    return price * quantity
