from django.db import models
from usuarios.models import Usuario
from produtos.models import Produto, Substancia

class ArmarioItem(models.Model):
    # RF12 - Gerenciar Armário Virtual (RN02 pesos de uso) 
    FREQUENCIA_CHOICES = [
        (3.0, 'Diário'),
        (1.0, 'Semanal'),
        (0.5, 'Esporádico'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='armario')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    frequencia_uso = models.FloatField(choices=FREQUENCIA_CHOICES, default=1.0)

    class Meta:
        unique_together = ('usuario', 'produto')
        verbose_name = "Item do Armário Virtual"
        verbose_name_plural = "Itens do Armário Virtual"

    def __str__(self):
        return f"{self.produto.nome} no armário de {self.usuario.nome_completo}"


class Sintoma(models.Model):
    # RF13 - Gerenciar Sintomas 
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()

    class Meta:
        verbose_name = "Sintoma"
        verbose_name_plural = "Sintomas"

    def __str__(self):
        return self.nome
    

class RegistroSintoma(models.Model):
    # RF14 - Registrar Diário de Ciclo 
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='diario_sintomas')
    sintoma = models.ForeignKey(Sintoma, on_delete=models.CASCADE)
    data_ocorrencia = models.DateField()
    intensidade = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Escala de dor/incômodo de 1 a 5")
    fase_ciclo = models.CharField(max_length=50)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Registro de Sintoma"
        verbose_name_plural = "Registros de Sintomas"

    def __str__(self):
        return f"{self.usuario.nome_completo} - {self.sintoma.nome} ({self.data_ocorrencia})"
    

class CicloMenstrual(models.Model):
    # RF15 - Registrar Ciclo Menstrual 
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ciclos')
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    duracao = models.IntegerField(help_text="Duração em dias calculada automaticamente")
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ciclo Menstrual"
        verbose_name_plural = "Ciclos Menstruais"

    def __str__(self):
        return f"Ciclo iniciado em {self.data_inicio} - {self.usuario.nome_completo}"
    

class Exposicao(models.Model):
    # RF16 - Registrar Exposição
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historico_exposicoes')
    carga_estrogenica = models.FloatField(default=0.0)
    carga_androgenica = models.FloatField(default=0.0)
    carga_tireoidiana = models.FloatField(default=0.0)
    carga_total = models.FloatField(default=0.0)
    data_calculo = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exposição"
        verbose_name_plural = "Histórico de Exposições"

    def __str__(self):
        return f"Carga {self.carga_total} em {self.data_calculo.strftime('%d/%m/%Y')}"


class ExposicaoDetalhe(models.Model):
    # RF17 - Registrar Detalhamento da Exposição 
    exposicao = models.ForeignKey(Exposicao, on_delete=models.CASCADE, related_name='detalhes')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    substancia = models.ForeignKey(Substancia, on_delete=models.CASCADE)
    valor_contribuicao = models.FloatField(help_text="Contribuição fracionada desta substância no cálculo total")

    class Meta:
        verbose_name = "Detalhe da Exposição"
        verbose_name_plural = "Detalhes das Exposições"

    def __str__(self):
        return f"Detalhe {self.substancia.nome} - {self.exposicao.usuario.nome_completo}"


class AlertaRisco(models.Model):
    # RF24 - Emitir alertas de risco (Baseado nas metas da RN04 e RN05)
    GRAVIDADE_CHOICES = [
        ('VERDE', 'Verde (Abaixo de 50%)'),
        ('AMARELO', 'Amarelo (Entre 50% e 75%)'),
        ('VERMELHO', 'Vermelho (Acima de 75%)'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='alertas_risco')
    mensagem_alerta = models.TextField()
    nivel_gravidade = models.CharField(max_length=10, choices=GRAVIDADE_CHOICES)
    data_emissao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alerta de Risco"
        verbose_name_plural = "Alertas de Risco"

    def __str__(self):
        return f"Alerta {self.nivel_gravidade} - {self.usuario.nome_completo}"


class Notificacao(models.Model):
    # RF25 - Gerenciar Notificações
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    tipo_notificacao = models.CharField(max_length=100)
    lida = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"Notificação para {self.usuario.nome_completo} - Lida: {self.lida}"