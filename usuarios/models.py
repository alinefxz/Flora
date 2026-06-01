from django.contrib.auth.models import AbstractUser
from django.db import models


class UF(models.Model):
    nome_estado = models.CharField(max_length=80)
    sigla = models.CharField(max_length=2, unique=True)

    class Meta:
        ordering = ["sigla"]
        verbose_name = "UF"
        verbose_name_plural = "UFs"

    def __str__(self):
        return self.sigla


class Cidade(models.Model):
    nome_cidade = models.CharField(max_length=120)
    uf = models.ForeignKey(UF, on_delete=models.CASCADE, related_name="cidades")

    class Meta:
        ordering = ["uf__sigla", "nome_cidade"]
        unique_together = ("nome_cidade", "uf")
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'

    def __str__(self):
        return f"{self.nome_cidade} - {self.uf.sigla}"


class Pessoa(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ("USUARIA", "Usuária"),
        ("ESPECIALISTA", "Especialista"),
        ("ADMIN", "Administrador"),
    ]

    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    data_nasc = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES, default="USUARIA")
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nome_completo", "cpf"]

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

    @property
    def cpf_mascarado(self):
        if len(self.cpf) < 6:
            return "***"
        return f"{self.cpf[:3]}.***.***-{self.cpf[-2:]}"

    def save(self, *args, **kwargs):
        self.is_active = self.ativo
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_completo or self.email


class Usuario(Pessoa):
    apelido = models.CharField(max_length=50, blank=True)
    foto_perfil = models.ImageField(upload_to="perfis/", null=True, blank=True)

    class Meta:
        verbose_name = "Usuária"
        verbose_name_plural = "Usuárias"

    def save(self, *args, **kwargs):
        self.tipo_usuario = "USUARIA"
        super().save(*args, **kwargs)


class Especialista(Pessoa):
    registro_profissional = models.CharField(max_length=60)
    biografia = models.TextField(blank=True)
    especialidade = models.CharField(max_length=120)

    class Meta:
        verbose_name = "Especialista"
        verbose_name_plural = "Especialistas"

    def save(self, *args, **kwargs):
        self.tipo_usuario = "ESPECIALISTA"
        super().save(*args, **kwargs)


class Admin(Pessoa):
    nivel_acesso = models.CharField(max_length=120)

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def save(self, *args, **kwargs):
        self.tipo_usuario = "ADMIN"
        self.is_staff = True
        super().save(*args, **kwargs)


class PerfilHormonal(models.Model):
    FLUXO_CHOICES = [
        ("LEVE", "Leve"),
        ("MODERADO", "Moderado"),
        ("INTENSO", "Intenso"),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_hormonal")
    uso_contraceptivo = models.BooleanField(default=False)
    condicao_hormonal = models.CharField(max_length=255, blank=True)
    ciclo_regular = models.BooleanField(default=True)
    duracao_ciclo = models.PositiveIntegerField(default=28)
    fluxo_menstrual = models.CharField(max_length=20, choices=FLUXO_CHOICES, default="MODERADO")
    observacoes = models.TextField(blank=True)
    peso_sensibilidade = models.FloatField(default=1.0)

    def __str__(self):
        return f"Perfil hormonal de {self.usuario.nome_completo}"
    
    class Meta:
        verbose_name = 'Perfil Hormonal'
        verbose_name_plural = 'Perfis Hormonais'