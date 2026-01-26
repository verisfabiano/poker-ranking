#!/usr/bin/env python
import os
import django
from django.template import Template, Context
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament

# Get tournament 43
tournament = Tournament.objects.get(id=43)

# Test the unlocalize filter with a simple template
test_template = Template("""{% load i18n %}{{ valor|unlocalize }}""")
context = Context({'valor': tournament.rebuy_valor})
result = test_template.render(context)
print(f"Tournament Rebuy Valor (raw): {tournament.rebuy_valor}")
print(f"Template render with unlocalize: {result}")
print(f"Type: {type(result)}")

# Also test parseFloat conversion
test_template2 = Template("""{% load i18n %}parseFloat({{ valor|unlocalize }})""")
result2 = test_template2.render(context)
print(f"\nJavaScript snippet: {result2}")
