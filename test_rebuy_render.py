#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament
from django.template import Template, Context

# Get tournament 43
tournament = Tournament.objects.get(id=43)

# Test the JavaScript rendering with replace
test_template = Template("""parseFloat("{{ valor|default:0 }}".replace(',', '.')) || 0""")
context = Context({'valor': tournament.rebuy_valor})
result = test_template.render(context)
print(f"Tournament Rebuy Valor (raw): {tournament.rebuy_valor}")
print(f"With locale pt-br, rendered as: {{ tournament.rebuy_valor|default:0 }} -> {result}")
print(f"JavaScript evaluation would give: {eval(result)}")
