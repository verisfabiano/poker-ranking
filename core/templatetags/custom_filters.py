from django import template

register = template.Library()

@register.filter
def number_format(value):
    """Formata número com ponto decimal para HTML5 type=number"""
    if value is None or value == '':
        return ''
    
    try:
        # Converter para float e retornar com ponto decimal
        float_value = float(value)
        return f"{float_value:.2f}"
    except (ValueError, TypeError):
        return value
