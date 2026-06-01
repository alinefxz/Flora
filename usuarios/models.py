from django.contrib.auth.models import AbstractUser
from django.db import models


class UF(models.Model):
    nome_estado = models.CharField("Nome do estado", max_length=80)
    sigla = models.CharField("Sigla", max_length=2, unique=True)

    class Meta:
        ordering = ["sigla"]
        verbose_name = "UF"
        verbose_name_plural = "UFs"

    def __str__(self):
        return self.sigla


class Cidade(models.Model):
    nome_cidade = models.CharField("Nome da cidade", max_length=120)
    uf = models.ForeignKey(UF, verbose_name="UF", on_delete=models.CASCADE, related_name="cidades")

    class Meta:
        ordering = ["uf__sigla", "nome_cidade"]
        unique_together = ("nome_cidade", "uf")
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def __str__(self):
        return f"{self.nome_cidade} - {self.uf.sigla}"


class Pessoa(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ("USUARIA", "Usuária"),
        ("ESPECIALISTA", "Especialista"),
        ("ADMIN", "Administrador"),
    ]

    email = models.EmailField("E-mail", unique=True)
    nome_completo = models.CharField("Nome completo", max_length=255)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    data_nasc = models.DateField("Data de nascimento", null=True, blank=True)
    ativo = models.BooleanField("Ativo", default=True)
    tipo_usuario = models.CharField("Tipo de usuário", max_length=15, choices=TIPO_USUARIO_CHOICES, default="USUARIA")
    cidade = models.ForeignKey(Cidade, verbose_name="Cidade", on_delete=models.SET_NULL, null=True, blank=True)

    apelido = models.CharField("Apelido", max_length=50, blank=True)
    foto_perfil = models.ImageField("Foto de perfil", upload_to="perfis/", null=True, blank=True)

    registro_profissional = models.CharField("Registro profissional", max_length=60, blank=True)
    biografia = models.TextField("Biografia", blank=True)
    especialidade = models.CharField("Especialidade", max_length=120, blank=True)

    nivel_acesso = models.CharField("Nível de acesso", max_length=120, blank=True)

    data_criacao = models.DateTimeField("Data de criação", auto_now_add=True)
    ultimo_login = models.DateTimeField("Último login", null=True, blank=True)

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
        if self.tipo_usuario == "ADMIN":
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_completo or self.email


class Usuario(Pessoa):
    class Meta:
        proxy = True
        verbose_name = "Usuária"
        verbose_name_plural = "Usuárias"


class Especialista(Pessoa):
    class Meta:
        proxy = True
        verbose_name = "Especialista"
        verbose_name_plural = "Especialistas"


class Admin(Pessoa):
    class Meta:
        proxy = True
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"


class PerfilHormonal(models.Model):
    FLUXO_CHOICES = [
        ("LEVE", "Leve"),
        ("MODERADO", "Moderado"),
        ("INTENSO", "Intenso"),
    ]

    usuario = models.OneToOneField(Usuario, verbose_name="Usuária", on_delete=models.CASCADE, related_name="perfil_hormonal")
    uso_contraceptivo = models.BooleanField("Usa contraceptivo?", default=False)
    condicao_hormonal = models.CharField("Condição hormonal", max_length=255, blank=True)
    ciclo_regular = models.BooleanField("Ciclo regular?", default=True)
    duracao_ciclo = models.PositiveIntegerField("Duração média do ciclo", default=28)
    fluxo_menstrual = models.CharField("Fluxo menstrual", max_length=20, choices=FLUXO_CHOICES, default="MODERADO")
    observacoes = models.TextField("Observações", blank=True)
    peso_sensibilidade = models.FloatField("Peso de sensibilidade", default=1.0)

    class Meta:
        verbose_name = "Perfil Hormonal"
        verbose_name_plural = "Perfis Hormonais"

    def __str__(self):
        return f"Perfil hormonal de {self.usuario.nome_completo}"