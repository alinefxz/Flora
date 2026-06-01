from django.contrib import admin
from .models import AlertaRisco, ArmarioItem, CicloMenstrual, Exposicao, ExposicaoDetalhe, Notificacao, RegistroSintoma, Sintoma


class ExposicaoDetalheInline(admin.TabularInline):
    model = ExposicaoDetalhe
    extra = 0
    readonly_fields = ("produto", "substancia", "valor_contribuicao")


@admin.register(ArmarioItem)
class ArmarioItemAdmin(admin.ModelAdmin):
    list_display = ("usuario", "produto", "frequencia_uso")
    list_filter = ("frequencia_uso",)
    search_fields = ("usuario__nome_completo", "produto__nome")
    autocomplete_fields = ["usuario", "produto"]


@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(RegistroSintoma)
class RegistroSintomaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "sintoma", "data_ocorrencia", "intensidade", "fase_ciclo")
    list_filter = ("intensidade", "fase_ciclo", "data_ocorrencia")
    search_fields = ("usuario__nome_completo", "sintoma__nome")
    autocomplete_fields = ["usuario", "sintoma"]


@admin.register(CicloMenstrual)
class CicloMenstrualAdmin(admin.ModelAdmin):
    list_display = ("usuario", "data_inicio", "data_fim", "duracao")
    list_filter = ("data_inicio",)
    search_fields = ("usuario__nome_completo",)
    autocomplete_fields = ["usuario"]


@admin.register(Exposicao)
class ExposicaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "carga_total", "carga_estrogenica", "carga_androgenica", "carga_tireoidiana", "data_calculo")
    list_filter = ("data_calculo",)
    search_fields = ("usuario__nome_completo",)
    inlines = [ExposicaoDetalheInline]


@admin.register(AlertaRisco)
class AlertaRiscoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nivel_gravidade", "data_emissao", "mensagem_alerta")
    list_filter = ("nivel_gravidade", "data_emissao")
    search_fields = ("usuario__nome_completo", "mensagem_alerta")


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo_notificacao", "lida", "data_envio")
    list_filter = ("lida", "tipo_notificacao", "data_envio")
    search_fields = ("usuario__nome_completo", "mensagem")