#!/usr/bin/env python
"""
Test script to verify tournament rebuy values are correctly rendered in template
"""
import os
import django
from django.template import Template, Context
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, Tenant
from django.test import RequestFactory

# Get tournament 43
tournament = Tournament.objects.get(id=43)

# Create a request with tenant
factory = RequestFactory()
request = factory.get('/')

# Get the tenant from tournament
tenant = tournament.tenant

# Create context
context = {
    'tournament': tournament,
}

# Create the JavaScript template snippet WITH i18n load
template_str = """
{% load i18n %}
window.tournamentData = {
    id: {{ tournament.id }},
    nome: "{{ tournament.nome|escapejs }}",
    rebuy_valor: parseFloat("{{ tournament.rebuy_valor|default:0|unlocalize }}") || 0,
    rebuy_duplo_valor: parseFloat("{{ tournament.rebuy_duplo_valor|default:0|unlocalize }}") || 0,
    addon_valor: parseFloat("{{ tournament.addon_valor|default:0|unlocalize }}") || 0,
    permite_rebuy: {{ tournament.permite_rebuy|lower }},
    permite_rebuy_duplo: {{ tournament.permite_rebuy_duplo|lower }},
    permite_addon: {{ tournament.permite_addon|lower }},
    timechip_chips: {{ tournament.timechip_chips|default:0 }}
};
"""

template = Template(template_str)
rendered = template.render(Context(context))

print("Rendered JavaScript:")
print("=" * 60)
print(rendered)
print("=" * 60)
print("\nExpected values:")
print(f"  rebuy_valor: {tournament.rebuy_valor}")
print(f"  rebuy_duplo_valor: {tournament.rebuy_duplo_valor}")
print(f"  addon_valor: {tournament.addon_valor}")
