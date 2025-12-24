"""
Validadores customizados para o sistema Poker Ranking
"""

import re
from django.core.exceptions import ValidationError


class ValidadorCNPJ:
    """Valida CNPJ brasileiro"""
    
    @staticmethod
    def limpar(cnpj):
        """Remove formatação do CNPJ"""
        return re.sub(r'\D', '', cnpj)
    
    @staticmethod
    def formatar(cnpj):
        """Formata CNPJ para XX.XXX.XXX/XXXX-XX"""
        limpo = ValidadorCNPJ.limpar(cnpj)
        if len(limpo) != 14:
            return cnpj
        return f"{limpo[0:2]}.{limpo[2:5]}.{limpo[5:8]}/{limpo[8:12]}-{limpo[12:14]}"
    
    @staticmethod
    def validar(cnpj):
        """
        Valida CNPJ usando algoritmo de dígitos verificadores
        Aceita formatos: 00000000000000 ou 00.000.000/0000-00
        """
        if not cnpj:
            return True  # Campo pode ser vazio
        
        limpo = ValidadorCNPJ.limpar(cnpj)
        
        # Verificar comprimento
        if len(limpo) != 14:
            raise ValidationError(
                'CNPJ deve conter 14 dígitos (ignorando formatação)'
            )
        
        # Verificar se não é sequência repetida
        if limpo == limpo[0] * 14:
            raise ValidationError('CNPJ inválido')
        
        # Validar primeiro dígito verificador
        soma = 0
        multiplicador = 5
        for i in range(12):
            if multiplicador == 10:
                multiplicador = 2
            soma += int(limpo[i]) * multiplicador
            multiplicador += 1
        
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1
        
        if int(limpo[12]) != digito1:
            raise ValidationError('CNPJ inválido (dígito verificador)')
        
        # Validar segundo dígito verificador
        soma = 0
        multiplicador = 6
        for i in range(13):
            if multiplicador == 10:
                multiplicador = 2
            soma += int(limpo[i]) * multiplicador
            multiplicador += 1
        
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2
        
        if int(limpo[13]) != digito2:
            raise ValidationError('CNPJ inválido (dígito verificador)')
        
        return True


class ValidadorCPF:
    """Valida CPF brasileiro"""
    
    @staticmethod
    def limpar(cpf):
        """Remove formatação do CPF"""
        return re.sub(r'\D', '', cpf)
    
    @staticmethod
    def formatar(cpf):
        """Formata CPF para XXX.XXX.XXX-XX"""
        limpo = ValidadorCPF.limpar(cpf)
        if len(limpo) != 11:
            return cpf
        return f"{limpo[0:3]}.{limpo[3:6]}.{limpo[6:9]}-{limpo[9:11]}"
    
    @staticmethod
    def validar(cpf):
        """
        Valida CPF usando algoritmo de dígitos verificadores
        Aceita formatos: 00000000000 ou 000.000.000-00
        """
        if not cpf:
            return True  # Campo pode ser vazio
        
        limpo = ValidadorCPF.limpar(cpf)
        
        # Verificar comprimento
        if len(limpo) != 11:
            raise ValidationError(
                'CPF deve conter 11 dígitos (ignorando formatação)'
            )
        
        # Verificar se não é sequência repetida
        if limpo == limpo[0] * 11:
            raise ValidationError('CPF inválido')
        
        # Validar primeiro dígito verificador
        soma = sum(int(limpo[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1
        
        if int(limpo[9]) != digito1:
            raise ValidationError('CPF inválido (dígito verificador)')
        
        # Validar segundo dígito verificador
        soma = sum(int(limpo[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2
        
        if int(limpo[10]) != digito2:
            raise ValidationError('CPF inválido (dígito verificador)')
        
        return True


class ValidadorCEP:
    """Valida CEP brasileiro"""
    
    @staticmethod
    def limpar(cep):
        """Remove formatação do CEP"""
        return re.sub(r'\D', '', cep)
    
    @staticmethod
    def formatar(cep):
        """Formata CEP para XXXXX-XXX"""
        limpo = ValidadorCEP.limpar(cep)
        if len(limpo) != 8:
            return cep
        return f"{limpo[0:5]}-{limpo[5:8]}"
    
    @staticmethod
    def validar(cep):
        """
        Valida CEP
        Aceita formatos: 00000000 ou 00000-000
        """
        if not cep:
            return True  # Campo pode ser vazio
        
        limpo = ValidadorCEP.limpar(cep)
        
        # Verificar comprimento
        if len(limpo) != 8:
            raise ValidationError(
                'CEP deve conter 8 dígitos (ignorando formatação)'
            )
        
        # Verificar se não é sequência repetida
        if limpo == limpo[0] * 8:
            raise ValidationError('CEP inválido')
        
        return True


class ValidadorTelefone:
    """Valida telefone brasileiro"""
    
    @staticmethod
    def limpar(telefone):
        """Remove formatação do telefone"""
        return re.sub(r'\D', '', telefone)
    
    @staticmethod
    def formatar(telefone):
        """Formata telefone para (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
        limpo = ValidadorTelefone.limpar(telefone)
        
        if len(limpo) == 10:
            # (XX) XXXX-XXXX
            return f"({limpo[0:2]}) {limpo[2:6]}-{limpo[6:10]}"
        elif len(limpo) == 11:
            # (XX) XXXXX-XXXX
            return f"({limpo[0:2]}) {limpo[2:7]}-{limpo[7:11]}"
        else:
            return telefone
    
    @staticmethod
    def validar(telefone):
        """
        Valida telefone brasileiro
        Aceita: (XX) XXXX-XXXX (10 dígitos) ou (XX) XXXXX-XXXX (11 dígitos)
        """
        if not telefone:
            return True  # Campo pode ser vazio
        
        limpo = ValidadorTelefone.limpar(telefone)
        
        # Verificar se tem 10 ou 11 dígitos
        if len(limpo) not in [10, 11]:
            raise ValidationError(
                'Telefone deve ter 10 ou 11 dígitos (ignorando formatação)'
            )
        
        # DDD válido (11-99, exceto alguns como 00-10)
        ddd = int(limpo[0:2])
        if ddd < 11:
            raise ValidationError('DDD inválido')
        
        return True


class ValidadorEndereço:
    """Validações para campos de endereço"""
    
    UFS_VALIDOS = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    @staticmethod
    def validar_uf(uf):
        """Valida UF (Estado)"""
        if not uf:
            return True
        
        uf_upper = uf.strip().upper()
        
        if uf_upper not in ValidadorEndereço.UFS_VALIDOS:
            raise ValidationError(
                f'UF inválido. Deve ser um dos: {", ".join(ValidadorEndereço.UFS_VALIDOS)}'
            )
        
        return True


# Funções de validação para formulários Django
def validar_cnpj(value):
    """Validador de CNPJ para Django Forms"""
    if value:
        ValidadorCNPJ.validar(value)


def validar_cpf(value):
    """Validador de CPF para Django Forms"""
    if value:
        ValidadorCPF.validar(value)


def validar_cep(value):
    """Validador de CEP para Django Forms"""
    if value:
        ValidadorCEP.validar(value)


def validar_telefone(value):
    """Validador de Telefone para Django Forms"""
    if value:
        ValidadorTelefone.validar(value)


def validar_uf(value):
    """Validador de UF para Django Forms"""
    if value:
        ValidadorEndereço.validar_uf(value)
