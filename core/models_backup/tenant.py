from django.db import models
from django.contrib.auth.models import User

class Tenant(models.Model):
    """
    Representa uma organização/grupo independente no sistema.
    """
    nome = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    # Limites opcionais
    max_jogadores = models.IntegerField(null=True, blank=True)
    max_torneios = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class TenantUser(models.Model):
    """
    Relaciona usuários a tenants e define papéis.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('moderator', 'Moderador'),
        ('player', 'Jogador'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_users')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')
    adicionado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'tenant']
        ordering = ['-adicionado_em']
    
    def __str__(self):
        return f"{self.user.username} - {self.tenant.nome} ({self.role})"
