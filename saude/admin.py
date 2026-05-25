from django.contrib import admin
from .models import ArmarioItem, Sintoma, RegistroSintoma, CicloMenstrual, Exposicao, ExposicaoDetalhe, AlertaRisco, Notificacao

class ExposicaoDetalheInline(admin.TabularInline):
    model = ExposicaoDetalhe
    extra = 0

@admin.register(ArmarioItem)
class ArmarioItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'produto', 'frequencia_uso')
    list_filter = ('frequencia_uso', 'usuario')

@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(RegistroSintoma)
class RegistroSintomaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'sintoma', 'data_ocorrencia', 'intensidade', 'fase_ciclo')
    list_filter = ('intensidade', 'fase_ciclo', 'data_ocorrencia', 'usuario')

@admin.register(CicloMenstrual)
class CicloMenstrualAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_inicio', 'data_fim', 'duracao')
    list_filter = ('usuario', 'data_inicio')

@admin.register(Exposicao)
class ExposicaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'carga_total', 'carga_estrogenica', 'carga_androgenica', 'carga_tireoidiana', 'data_calculo')
    list_filter = ('data_calculo', 'usuario')
    inlines = [ExposicaoDetalheInline]

@admin.register(AlertaRisco)
class AlertaRiscoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nivel_gravidade', 'data_emissao', 'mensagem_alerta')
    list_filter = ('nivel_gravidade', 'data_emissao', 'usuario')

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_notificacao', 'lida', 'data_envio')
    list_filter = ('lida', 'tipo_notificacao', 'usuario')