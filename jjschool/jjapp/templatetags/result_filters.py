from django import template
from jjapp.models import Result  # Import your Result model

register = template.Library()

@register.filter
def filter_by_student(results, student):
    return results.filter(student=student).first()