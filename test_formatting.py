#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar a formatação de valores decimais para HTML5 type=number
"""

from decimal import Decimal

# Teste de formatação
test_values = [
    Decimal("100.00"),
    Decimal("100.50"),
    Decimal("100,50"),  # Valor com vírgula
    Decimal("0.00"),
    None,
]

print("Testando formatação de valores para HTML5 number input:")
print("=" * 60)

for val in test_values:
    if val:
        formatted = f"{float(val):.2f}"
        print(f"Valor: {val:10} => Formatado: {formatted}")
    else:
        formatted = ""
        print(f"Valor: None       => Formatado: '{formatted}'")

print("\n" + "=" * 60)
print("✓ Todos os testes de formatação completados")
