from django import template

register = template.Library()

@register.filter
def get_range(start, end):
    """
    Возвращает диапазон чисел от start до end включительно.
    Пример использования: {% for i in start|get_range:end %}
    """
    try:
        start = int(start)
        end = int(end)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return []