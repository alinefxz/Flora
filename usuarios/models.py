from django.db import models
from django.contrib.auth.models import AbstractUser

class UF(models.Model):
    #RF21 - Gerenciar UF
    nome_estado = models.CharField(max_length=50)
    sigla = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name = "Estado (UF)"
        verbose_name_plural = "Estados (UFs)"

    def __str__(self):
        return self.sigla


class Cidade(models.Model):
    #RF20 - Gerenciar Cidade
    nome_cidade = models.CharField(max_length=100)
    uf = models.ForeignKey(UF, on_delete=models.CASCADE, related_name='cidades')

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def __str__(self):
        return f"{self.nome_cidade} - {self.uf.sigla}"


class Pessoa(AbstractUser):
    #RF01 - Gerenciar Pessoa
    TIPO_USUARIO_CHOICES = [
        ('USUARIA', 'Usuária'),
        ('ESPECIALISTA', 'Especialista'),
        ('ADMIN', 'Administrador'),
    ]
    
    # Sobrescrevendo campos nativos para alinhar aos requisitos técnicos
    username = models.CharField(max_length=150, unique=True, help_text="Nome de usuário para login")
    email = models.EmailField(unique=True) 
    
    # Campos específicos do FLORA
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)  # RNF05: Armazenar mascarado ou aplicar hash
    data_nasc = models.DateField(null=True, blank=True)
    tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES, default='USUARIA')
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Atalhos semânticos exigidos pelo RF01
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo', 'cpf']

    class Meta:
        verbose_name = "Cadastro Geral de Pessoa"
        verbose_name_plural = "Base Geral de Pessoas"

    def __str__(self):
        return self.nome_completo


class Usuario(Pessoa):
    #RF02 - Gerenciar Usuárias 
    apelido = models.CharField(max_length=50, blank=True)
    foto_perfil = models.ImageField(upload_to='perfis/', null=True, blank=True)

    class Meta:
        verbose_name = "Usuária"
        verbose_name_plural = "Usuárias"
    
    def __str__(self):
        return self.apelido or self.nome_completo


class Especialista(Pessoa):
    #RF03 - Gerenciar Especialistas 
    registro_profissional = models.CharField(max_length=50, help_text="CRM ou CRQ")
    biografia = models.TextField(blank=True)
    especialidade = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Especialista"
        verbose_name_plural = "Especialistas"


class Admin(Pessoa):
    #RF04 - Gerenciar Administrador
    nivel_acesso = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"


class PerfilHormonal(models.Model):
    #RF05 - Gerenciar Perfil Hormonal
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_hormonal')
    uso_contraceptivo = models.BooleanField(default=False)
    condicao_hormonal = models.CharField(max_length=255, blank=True, help_text="Ex: SOP, Endometriose")
    ciclo_regular = models.BooleanField(default=True)
    duracao_ciclo = models.IntegerField(default=28, help_text="Duração média em dias")
    fluxo_menstrual = models.CharField(max_length=50, choices=[('LEVE', 'Leve'), ('MODERADO', 'Moderado'), ('INTENSO', 'Intenso')])
    observacoes = models.TextField(blank=True)
    peso_sensibilidade = models.FloatField(default=1.0)

    class Meta:
        verbose_name = "Perfil Hormonal Clínico"
        verbose_name_plural = "Perfis Hormonais Clínicos"

    def __str__(self):
        return f"Perfil de {self.usuario.apelido or self.usuario.nome_completo}"