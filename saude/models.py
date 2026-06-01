from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from produtos.models import Produto, Substancia
from usuarios.models import Usuario


class ArmarioItem(models.Model):
    FREQUENCIA_CHOICES = [
        (3.0, "Diário"),
        (1.0, "Semanal"),
        (0.5, "Esporádico"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="armario")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="usuarios_no_armario")
    frequencia_uso = models.FloatField(choices=FREQUENCIA_CHOICES, default=1.0)

    class Meta:
        unique_together = ("usuario", "produto")

    def __str__(self):
        return f"{self.produto} - {self.usuario}"


class Sintoma(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class CicloMenstrual(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ciclos")
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    duracao = models.PositiveIntegerField(default=5)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data_inicio"]

    def save(self, *args, **kwargs):
        if self.data_inicio and self.data_fim:
            self.duracao = (self.data_fim - self.data_inicio).days + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.data_inicio}"


class RegistroSintoma(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="diario_sintomas")
    sintoma = models.ForeignKey(Sintoma, on_delete=models.CASCADE, related_name="registros")
    data_ocorrencia = models.DateField()
    intensidade = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    fase_ciclo = models.CharField(max_length=50, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data_ocorrencia"]

    def save(self, *args, **kwargs):
        if not self.fase_ciclo:
            from .services import calcular_fase_menstrual
            self.fase_ciclo = calcular_fase_menstrual(self.usuario, self.data_ocorrencia)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.sintoma} - {self.data_ocorrencia}"


class Exposicao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="historico_exposicoes")
    carga_estrogenica = models.FloatField(default=0.0)
    carga_androgenica = models.FloatField(default=0.0)
    carga_tireoidiana = models.FloatField(default=0.0)
    carga_total = models.FloatField(default=0.0)
    data_calculo = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_calculo"]

    def __str__(self):
        return f"{self.usuario} - {self.carga_total:.2f}"


class ExposicaoDetalhe(models.Model):
    exposicao = models.ForeignKey(Exposicao, on_delete=models.CASCADE, related_name="detalhes")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    substancia = models.ForeignKey(Substancia, on_delete=models.CASCADE)
    valor_contribuicao = models.FloatField()

    def __str__(self):
        return f"{self.produto} - {self.substancia}"


class AlertaRisco(models.Model):
    GRAVIDADE_CHOICES = [
        ("VERDE", "Verde"),
        ("AMARELO", "Amarelo"),
        ("VERMELHO", "Vermelho"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="alertas_risco")
    mensagem_alerta = models.TextField()
    nivel_gravidade = models.CharField(max_length=10, choices=GRAVIDADE_CHOICES)
    data_emissao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_emissao"]

    def __str__(self):
        return f"{self.nivel_gravidade} - {self.usuario}"


class Notificacao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="notificacoes")
    mensagem = models.TextField()
    tipo_notificacao = models.CharField(max_length=100)
    lida = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_envio"]

    def __str__(self):
        return f"{self.tipo_notificacao} - {self.usuario}"