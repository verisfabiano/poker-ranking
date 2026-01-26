"""
Utilitários para geração automática de usernames seguros.
"""
import secrets
from django.contrib.auth.models import User


def generate_unique_username(prefix="player"):
    """
    Gera um username único e aleatório baseado no prefixo.
    
    Args:
        prefix (str): Prefixo para o username (padrão: "player")
    
    Returns:
        str: Username único (ex: player_12345abcd)
    
    Exemplo:
        >>> username = generate_unique_username()
        >>> username
        'player_a7f3c9e2'
    """
    while True:
        # Gerar 8 caracteres aleatórios
        random_str = secrets.token_hex(4)  # 8 caracteres hexadecimais
        username = f"{prefix}_{random_str}"
        
        # Verificar se é único
        if not User.objects.filter(username=username).exists():
            return username


def generate_display_username(email):
    """
    Gera um "display username" legível baseado no email.
    Usado apenas para exibição, não para login.
    
    Args:
        email (str): Email do usuário
    
    Returns:
        str: Display username (ex: "john_s" para "john.smith@example.com")
    
    Exemplo:
        >>> display_username = generate_display_username("john.smith@example.com")
        >>> display_username
        'john_s'
    """
    # Extrair parte antes do @
    local_part = email.split('@')[0]
    
    # Remover pontos e caracteres especiais
    local_part = local_part.replace('.', '_').replace('-', '_')
    
    # Pegar até 20 caracteres
    return local_part[:20].lower()
