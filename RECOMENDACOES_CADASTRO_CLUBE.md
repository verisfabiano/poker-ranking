# 📋 Recomendações para Formulário de Cadastro de Clube (Tenant)

## 🎯 Situação Atual

### Campos Existentes (Formulário Simples)
**Dados do Clube:**
- Nome do Clube ✅
- Descrição (opcional) ✅

**Dados do Administrador:**
- Email ✅
- Senha ✅
- Confirmar Senha ✅

**Modelo Tenant (Database):**
```python
nome                 # CharField
slug                 # SlugField
descricao           # TextField
criado_em           # DateTimeField
ativo               # BooleanField
max_jogadores       # IntegerField (opcional)
max_torneios        # IntegerField (opcional)
```

---

## ✨ Campos Recomendados para Adicionar

### 📌 SEÇÃO 1: INFORMAÇÕES DO CLUBE (Dados Principais)

#### 1.1 **Nome do Clube** ✅ (JÁ EXISTE)
- Tipo: Text
- Obrigatório: Sim
- Validação: 3-255 caracteres
- Exemplo: "Poker Club São Paulo"

#### 1.2 **CNPJ/Registro** (NOVO)
- Tipo: Text (formatado)
- Obrigatório: Recomendado
- Validação: CNPJ válido ou ID de registro
- Máscara: `XX.XXX.XXX/XXXX-XX`
- Armazena: `club_cnpj` (CharField 18)
- Uso: Identificação fiscal/legal

#### 1.3 **Telefone Principal** (NOVO)
- Tipo: Tel
- Obrigatório: Recomendado
- Validação: Formato válido
- Máscara: `(XX) XXXXX-XXXX` ou `(XX) XXXX-XXXX`
- Armazena: `club_phone` (CharField 20)
- Uso: Contato geral

#### 1.4 **Email de Contato** (NOVO)
- Tipo: Email
- Obrigatório: Recomendado
- Validação: Email válido
- Armazena: `club_email` (EmailField)
- Nota: Diferente do email do admin
- Uso: Comunicação geral do clube

#### 1.5 **Website/Link** (NOVO)
- Tipo: URL
- Obrigatório: Opcional
- Validação: URL válida
- Armazena: `club_website` (URLField, blank=True)
- Exemplo: "https://www.pokerclubsp.com"

#### 1.6 **Descrição** ✅ (JÁ EXISTE)
- Tipo: TextArea
- Obrigatório: Não
- Máximo: 500 caracteres

---

### 🏠 SEÇÃO 2: ENDEREÇO

#### 2.1 **CEP** (NOVO - COM VALIDAÇÃO)
- Tipo: Text (formatado)
- Obrigatório: Sim (recomendado)
- Validação: CEP válido (8 dígitos)
- Máscara: `XXXXX-XXX`
- Armazena: `address_cep` (CharField 9)
- Trigger: Auto-preencher próximos campos via API (viaCEP)
- Exemplo: "01310-100"

#### 2.2 **Endereço/Rua** (NOVO)
- Tipo: Text
- Obrigatório: Sim (se preenchido CEP)
- Validação: 5-255 caracteres
- Armazena: `address_street` (CharField 255)
- Preenchimento: Auto (via CEP)
- Exemplo: "Av. Paulista"

#### 2.3 **Número** (NOVO)
- Tipo: Text/Number
- Obrigatório: Sim (se preenchido CEP)
- Validação: 1-20 caracteres
- Armazena: `address_number` (CharField 20)
- Exemplo: "1000"

#### 2.4 **Complemento** (NOVO)
- Tipo: Text
- Obrigatório: Não
- Validação: Máximo 100 caracteres
- Armazena: `address_complement` (CharField 100, blank=True)
- Exemplo: "Apto 1500"

#### 2.5 **Bairro** (NOVO)
- Tipo: Text
- Obrigatório: Sim (se preenchido CEP)
- Validação: 3-100 caracteres
- Armazena: `address_neighborhood` (CharField 100)
- Preenchimento: Auto (via CEP)
- Exemplo: "Bela Vista"

#### 2.6 **Cidade** (NOVO)
- Tipo: Text
- Obrigatório: Sim (se preenchido CEP)
- Validação: 3-100 caracteres
- Armazena: `address_city` (CharField 100)
- Preenchimento: Auto (via CEP)
- Exemplo: "São Paulo"

#### 2.7 **Estado/UF** (NOVO)
- Tipo: Select (dropdown)
- Obrigatório: Sim (se preenchido CEP)
- Opções: Lista de 27 UFs (SP, RJ, MG, BA, ...)
- Armazena: `address_state` (CharField 2, choices)
- Preenchimento: Auto (via CEP)
- Exemplo: "SP"

---

### 👤 SEÇÃO 3: INFORMAÇÕES DO ADMINISTRADOR (DADOS PESSOAIS)

#### 3.1 **Nome Completo do Contato** (NOVO)
- Tipo: Text
- Obrigatório: Sim
- Validação: 5-255 caracteres
- Armazena: `admin_full_name` (CharField 255)
- Nota: Diferente do username
- Exemplo: "João da Silva Santos"

#### 3.2 **Email do Admin** ✅ (JÁ EXISTE)
- Tipo: Email
- Obrigatório: Sim
- Validação: Email válido e único
- Nota: Criará login do Django User

#### 3.3 **Telefone do Contato** (NOVO)
- Tipo: Tel
- Obrigatório: Recomendado
- Validação: Formato válido
- Armazena: `admin_phone` (CharField 20)
- Exemplo: "(11) 98765-4321"

#### 3.4 **Cargo/Função** (NOVO)
- Tipo: Text/Select
- Obrigatório: Recomendado
- Opções: "Proprietário", "Gerente", "Admin", "Outro"
- Armazena: `admin_role` (CharField 50)
- Exemplo: "Proprietário"

#### 3.5 **CPF** (NOVO - OPCIONAL MAS RECOMENDADO)
- Tipo: Text (formatado)
- Obrigatório: Opcional
- Validação: CPF válido (11 dígitos)
- Máscara: `XXX.XXX.XXX-XX`
- Armazena: `admin_cpf` (CharField 14, blank=True)
- Nota: Pode ser armazenado de forma criptografada

#### 3.6 **Senha** ✅ (JÁ EXISTE)
- Tipo: Password
- Obrigatório: Sim
- Validação: Mínimo 8 caracteres, complexidade recomendada
- Força da Senha: Indicador visual recomendado

#### 3.7 **Confirmar Senha** ✅ (JÁ EXISTE)
- Tipo: Password
- Obrigatório: Sim
- Validação: Deve corresponder à senha

---

### ⚙️ SEÇÃO 4: CONFIGURAÇÕES DO CLUBE (OPCIONAL)

#### 4.1 **Tipo de Clube** (NOVO)
- Tipo: Select
- Obrigatório: Opcional
- Opções: "Presencial", "Online", "Ambos", "Torneios"
- Armazena: `club_type` (CharField 50, blank=True)

#### 4.2 **Horário de Funcionamento** (NOVO)
- Tipo: Time Range
- Obrigatório: Opcional
- Formato: "HH:MM - HH:MM"
- Armazena: `opening_hours` (TextField, blank=True)
- Exemplo: "20:00 - 06:00"

#### 4.3 **Capacidade Máxima de Jogadores** (NOVO)
- Tipo: Number
- Obrigatório: Opcional
- Validação: Mínimo 2, máximo 1000
- Armazena: `max_players` (IntegerField, blank=True)
- Já existe no modelo como `max_jogadores`

#### 4.4 **Limite de Torneios por Semana** (NOVO)
- Tipo: Number
- Obrigatório: Opcional
- Validação: Mínimo 1
- Armazena: `max_tournaments` (IntegerField, blank=True)
- Já existe no modelo como `max_torneios`

---

## 📊 ESTRUTURA PROPOSTA DO MODELO TENANT (MELHORADO)

```python
class Tenant(models.Model):
    """
    Representa um Clube/Organização no sistema.
    """
    # INFORMAÇÕES BÁSICAS
    nome = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    
    # INFORMAÇÕES DE CONTATO DO CLUBE
    club_email = models.EmailField(blank=True)
    club_phone = models.CharField(max_length=20, blank=True)
    club_cnpj = models.CharField(max_length=18, blank=True, unique=True, null=True)
    club_website = models.URLField(blank=True)
    club_type = models.CharField(
        max_length=50,
        choices=[
            ('presencial', 'Presencial'),
            ('online', 'Online'),
            ('ambos', 'Ambos'),
            ('torneios', 'Torneios'),
        ],
        blank=True
    )
    
    # ENDEREÇO
    address_cep = models.CharField(max_length=9, blank=True)
    address_street = models.CharField(max_length=255, blank=True)
    address_number = models.CharField(max_length=20, blank=True)
    address_complement = models.CharField(max_length=100, blank=True)
    address_neighborhood = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    
    # INFORMAÇÕES DE FUNCIONAMENTO
    opening_hours = models.TextField(blank=True)
    
    # LIMITES
    max_jogadores = models.IntegerField(null=True, blank=True)
    max_torneios = models.IntegerField(null=True, blank=True)
    
    # METADADOS
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
```

---

## 📋 CAMPOS PARA O ADMIN (USER DO DJANGO)

Atualmente, os dados do admin são armazenados no modelo `User` do Django:
- `username` ✅ (gerado automaticamente)
- `email` ✅ (campo obrigatório)
- `password` ✅ (hasheado)

**Campos Adicionais Recomendados (criar perfil separado):**

Opção 1: Estender User com `UserProfile`:
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    role = models.CharField(max_length=50, choices=[...], blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
```

Opção 2: Usar `django-allauth` ou similar para gerenciar perfis

---

## 🔍 VALIDAÇÕES RECOMENDADAS

### CEP com ViaCEP API
```javascript
// Auto-preencher endereço quando CEP é validado
fetch(`https://viacep.com.br/ws/${cep}/json/`)
  .then(r => r.json())
  .then(data => {
    document.getElementById('street').value = data.logradouro;
    document.getElementById('neighborhood').value = data.bairro;
    document.getElementById('city').value = data.localidade;
    document.getElementById('state').value = data.uf;
  })
```

### CNPJ
- Validar formato: `XX.XXX.XXX/XXXX-XX`
- Verificar se já existe no banco
- Validação de dígitos verificadores (opcional)

### CPF
- Validar formato: `XXX.XXX.XXX-XX`
- Validação de dígitos verificadores (opcional)
- Pode ser criptografado no banco

### Telefone
- Validar formato: `(XX) XXXXX-XXXX` ou `(XX) XXXX-XXXX`
- Aceitar variações

### Email
- Validar formato
- Verificar unicidade
- Usar regex ou `django.core.validators.EmailValidator`

---

## 📱 UX/DESIGN RECOMENDADO

### Organização em Abas/Seções
```
┌─────────────────────────────────────────┐
│  CRIAR NOVO CLUBE                       │
├─────────────────────────────────────────┤
│                                         │
│  ✓ Informações do Clube                │
│  ○ Endereço                            │
│  ○ Administrador                       │
│  ○ Configurações (opcional)            │
│                                         │
└─────────────────────────────────────────┘
```

### Campos Obrigatórios vs Opcionais
- **Obrigatórios:** Nome, Email, Senha, Contato
- **Recomendados:** CEP, Telefone, CNPJ
- **Opcionais:** Website, Tipo de Clube, Horários

### Feedback Visual
- Indicador de força da senha
- Validação em tempo real (CEP, CNPJ, CPF)
- Ícones de sucesso/erro
- Mensagens claras

---

## 🎨 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Modelo (Backend)
- [ ] Adicionar campos ao modelo `Tenant`
- [ ] Criar migration
- [ ] Adicionar validadores customizados
- [ ] Registrar no Django Admin

### Fase 2: Formulário (Backend)
- [ ] Criar `TenantRegistrationForm` (Django Forms)
- [ ] Adicionar validações
- [ ] Criar `UserProfile` model (se necessário)
- [ ] Atualizar view `signup_club`

### Fase 3: Template (Frontend)
- [ ] Atualizar `signup_club.html`
- [ ] Adicionar seções/tabs
- [ ] Adicionar máscaras de input (JavaScript)
- [ ] Adicionar validação em tempo real
- [ ] Integrar ViaCEP API

### Fase 4: JavaScript
- [ ] Máscaras de input (CNPJ, CEP, CPF, Telefone)
- [ ] Validação em tempo real
- [ ] Auto-preencher endereço (ViaCEP)
- [ ] Indicador de força da senha

### Fase 5: Testes
- [ ] Testes unitários dos validadores
- [ ] Testes de integração (view)
- [ ] Testes de aceitação (formulário completo)
- [ ] Testes de UX (mobile responsivo)

---

## 📖 RECURSOS E BIBLIOTECAS

### Python/Django
- `django-phonenumber-field` - Validação de telefone
- `django-localflavor` - Validadores para Brasil (CNPJ, CPF)
- `validate-docbr` - Validação de CNPJ/CPF
- `django-crispy-forms` - Renderização de formulários

### JavaScript
- `imask.js` - Máscaras de input avançadas
- `jquery-mask-plugin` - Máscaras jQuery
- `axios` - Requisições HTTP (ViaCEP)

### APIs Externas
- **ViaCEP:** https://viacep.com.br/ (Gratuito, sem auth)
- **Google Maps API:** Validar endereço (Pago)
- **SMS:** Twilio, AWS SNS para verificação de telefone

---

## 🚀 PRÓXIMOS PASSOS

1. **Discutir prioridades** - Quais campos são críticos?
2. **Definir scope** - Qual fase implementar primeiro?
3. **Design mock-up** - Como ficaria o formulário?
4. **Criar especificação técnica** - Detalhes de implementação
5. **Implementar** - Começar pela Fase 1 (Modelo)

---

## 💡 OBSERVAÇÕES IMPORTANTES

1. **LGPD:** Armazenar CPF é sensível - considerar criptografia
2. **Validação em 2 camadas:** Frontend (UX) + Backend (Segurança)
3. **Migrações:** Planejar bem as migrações para não quebrar sistema
4. **Testes:** Testar com dados reais antes de ir para produção
5. **Documentação:** Documentar novos validadores e campos
6. **Backward compatibility:** Garantir que campos antigos funcionem

