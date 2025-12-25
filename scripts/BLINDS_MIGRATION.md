# 🎲 Migração de Estruturas de Blinds para Railway

Este guia mostra como exportar e carregar as estruturas de blinds do seu banco local para o Railway.

## 📋 Passo a Passo

### 1️⃣ Exportar Blinds Localmente

Execute o script que exporta as estruturas:

```bash
python scripts/export_blinds.py
```

**O que acontece:**
- ✅ Lê todas as estruturas de blinds do seu banco local
- ✅ Exporta para arquivos JSON (um por tenant)
- ✅ Salva arquivos como `blinds_<tenant-slug>.json`

### 2️⃣ Fazer Commit e Push

```bash
# Adicionar os arquivos JSON ao git
git add blinds_*.json

# Fazer commit
git commit -m "Add: Estruturas de blinds para migração Railway"

# Push para o repositório
git push
```

### 3️⃣ Carregar no Railway

Acesse o terminal do seu projeto no Railway e execute:

```bash
# Opção 1: Usando o comando customizado (recomendado)
railway run python manage.py load_blinds

# Opção 2: Usando loaddata diretamente
railway run python manage.py loaddata blinds_*.json
```

## 🔄 Fluxo Resumido

```
1. python scripts/export_blinds.py
   └─> Gera blinds_*.json
   
2. git add blinds_*.json && git commit && git push
   └─> Envia para GitHub
   
3. railway run python manage.py load_blinds
   └─> Carrega no banco do Railway
```

## 📝 Exemplos de Saída

### Export local:
```
🎲 Exportando Estruturas de Blinds...
📍 Tenants encontrados: 1

📦 Exportando blinds do tenant: Veris Poker
   ✅ 5 estruturas encontradas
   ✅ 127 níveis encontrados
   💾 Salvo em: blinds_veris_poker.json

✅ Exportação concluída!
```

### Load no Railway:
```
🎲 Procurando arquivos de blinds...
✅ Encontrados 1 arquivos de blinds

📦 Carregando blinds_veris_poker.json...
✅ blinds_veris_poker.json carregado com sucesso!

✅ Estruturas de blinds carregadas!
```

## ⚙️ Detalhes Técnicos

### O que é exportado:
- `BlindStructure` (estruturas de blinds)
- `BlindLevel` (níveis individuais de cada estrutura)

### Formato do arquivo JSON:
```json
[
  {
    "model": "core.blindstructure",
    "pk": 1,
    "fields": {
      "nome": "6-Max Cash",
      "tenant": 1,
      ...
    }
  },
  {
    "model": "core.blindlevel",
    "pk": 1,
    "fields": {
      "blind_structure": 1,
      "nivel": 1,
      "small_blind": "0.5",
      ...
    }
  }
]
```

## 🐛 Troubleshooting

### Erro: "Nenhum tenant encontrado"
```bash
# Certifique-se de que seu banco local tem dados
python manage.py shell
>>> from core.models import Tenant
>>> Tenant.objects.all().count()
```

### Erro ao carregar no Railway: "Duplicate key"
Se receber erro de chave duplicada:
1. Execute `railway run python manage.py flush` (cuidado: apaga dados!)
2. Ou use `python manage.py loaddata --ignore-conflicts blinds_*.json`

### Espaço em arquivo JSON muito grande
Se o arquivo ficar grande, você pode compactá-lo:
```bash
gzip blinds_*.json
```

E carregar assim:
```bash
railway run python manage.py loaddata blinds_*.json.gz
```

## 📚 Referências

- [Django loaddata documentation](https://docs.djangoproject.com/en/5.2/ref/django-admin/#loaddata)
- [Django dumpdata documentation](https://docs.djangoproject.com/en/5.2/ref/django-admin/#dumpdata)
- [Railway documentation](https://docs.railway.app/)
