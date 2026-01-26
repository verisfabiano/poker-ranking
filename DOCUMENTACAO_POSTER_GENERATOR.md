# Gerador de Posters de Torneios

## Uso

A funcionalidade está disponível em `/torneio/{id}/poster/`

### Parâmetros de Query

- **template** (opcional): `feed`, `story`, `horizontal` (padrão: `feed`)
- **theme** (opcional): `gold`, `dark`, `neon` (padrão: `gold`)
- **format** (opcional): `png`, `jpg` (padrão: `png`)

### Exemplos de URLs

```
# Template padrão (feed com tema gold)
/torneio/9/poster/

# Template story (vertical, ideal para Instagram Stories)
/torneio/9/poster/?template=story

# Template horizontal (landscape)
/torneio/9/poster/?template=horizontal

# Tema neon
/torneio/9/poster/?theme=neon

# Combinações
/torneio/9/poster/?template=story&theme=dark
/torneio/9/poster/?template=horizontal&theme=neon&format=jpg
```

## Templates Disponíveis

### 1. **FEED** (Padrão - 1080x1440)
- Ideal para postar no Instagram Feed
- Layout vertical otimizado
- Exibe: Data/Hora, GTD, Opções de compra, Blind structure, Contato

### 2. **STORY** (1080x1920)
- Ideal para Instagram Stories
- Mais vertical e alongado
- Inclui: QR code (se disponível) para inscrição

### 3. **HORIZONTAL** (1920x1080)
- Ideal para apresentações, wallpapers
- Layout em duas colunas
- Exibe informações de forma expansiva

## Temas Disponíveis

### 1. **GOLD** (Padrão)
- Paleta: Dourado/Branco/Preto
- Elegante e premium

### 2. **DARK**
- Paleta: Azul/Branco/Preto
- Moderno e sofisticado

### 3. **NEON**
- Paleta: Ciano/Magenta/Preto
- Vibrante e chamativo

## Recursos Implementados

✅ Múltiplos templates (Feed, Story, Horizontal)
✅ Múltiplos temas (Gold, Dark, Neon)
✅ Suporte a PNG e JPG
✅ QR Code automático (quando lib qrcode está disponível)
✅ Layout responsivo para diferentes tamanhos
✅ Gradientes e efeitos visuais
✅ Informações estruturadas do torneio
✅ Contato e informações do clube

## Instalação de Dependências Opcionais

Para suporte a QR Code:
```bash
pip install qrcode[pil]
```

## Integração no Painel

Para adicionar botões de download no painel de torneios:

```html
<!-- Botões de download -->
<a href="{% url 'tournament_poster' tournament.id %}?template=feed&theme=gold" 
   class="btn btn-sm btn-primary" target="_blank">
   📱 Feed
</a>

<a href="{% url 'tournament_poster' tournament.id %}?template=story&theme=gold" 
   class="btn btn-sm btn-info" target="_blank">
   📲 Story
</a>

<a href="{% url 'tournament_poster' tournament.id %}?template=horizontal&theme=dark" 
   class="btn btn-sm btn-secondary" target="_blank">
   🖼️ Horizontal
</a>
```

## Customizações Futuras

- [ ] Adicionar logo/marca do clube
- [ ] Suporte a background customizados
- [ ] Mais temas (gradientes, padrões)
- [ ] Exportar múltiplos formatos simultaneamente
- [ ] Adicionar watermark automático
- [ ] Integração com redes sociais para compartilhamento direto
- [ ] Cache de imagens geradas
