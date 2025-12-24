from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Tenant, TenantUser


@receiver(post_save, sender=User)
def criar_tenant_user_padrao(sender, instance, created, **kwargs):
    """
    Quando um novo usuário é criado, atribui o tenant padrão.
    """
    if created:
        try:
            tenant_padrao = Tenant.objects.get(slug='tenant-padrao')
            TenantUser.objects.get_or_create(
                user=instance,
                tenant=tenant_padrao,
                defaults={'role': 'player'}
            )
        except Tenant.DoesNotExist:
            pass


@receiver(post_save, sender=TenantUser)
def atualizar_is_staff_do_usuario(sender, instance, created, **kwargs):
    """
    Quando um TenantUser é criado ou modificado, atualiza is_staff do usuário
    baseado no role. Se é admin em qualquer tenant, é staff.
    """
    user = instance.user
    
    # Verificar se o usuário é admin em qualquer tenant
    is_admin = TenantUser.objects.filter(user=user, role='admin').exists()
    
    # Atualizar is_staff se mudou
    if user.is_staff != is_admin:
        user.is_staff = is_admin
        user.save(update_fields=['is_staff'])
