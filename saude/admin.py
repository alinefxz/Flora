from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AlertaRisco,
    ArmarioItem,
    CicloMenstrual,
    Exposicao,
    ExposicaoDetalhe,
    Notificacao,
    RegistroSintoma,
    Sintoma,
)


class CustomAdminBase(admin.ModelAdmin):
    """Classe base com CSS customizado"""

    class Media:
        css = {"all": ("css/admin_custom_fonts_CORRIGIDO.css",)}


class ExposicaoDetalheInline(admin.TabularInline):
    model = ExposicaoDetalhe
    extra = 1
    autocomplete_fields = ["produto", "substancia"]
    fields = ("produto", "substancia", "valor_contribuicao")
    readonly_fields = ("valor_contribuicao",)


@admin.register(ArmarioItem)
class ArmarioItemAdmin(CustomAdminBase):
    list_display = ("usuario", "produto", "frequencia_uso")
    list_filter = ("frequencia_uso",)
    search_fields = ("usuario__nome_completo", "produto__nome")
    autocomplete_fields = ["usuario", "produto"]


@admin.register(Sintoma)
class SintomaAdmin(CustomAdminBase):
    list_display = ("nome", "descricao")
    search_fields = ("nome", "descricao")


@admin.register(RegistroSintoma)
class RegistroSintomaAdmin(CustomAdminBase):
    list_display = (
        "usuario",
        "sintoma",
        "data_ocorrencia",
        "intensidade_badge",
        "fase_ciclo",
    )
    list_filter = ("intensidade", "fase_ciclo", "data_ocorrencia")
    search_fields = ("usuario__nome_completo", "sintoma__nome")
    autocomplete_fields = ["usuario", "sintoma"]
    date_hierarchy = "data_ocorrencia"

    def intensidade_badge(self, obj):
        cores = {
            1: "#28a745",
            2: "#28a745",
            3: "#ffc107",
            4: "#dc3545",
            5: "#dc3545",
        }
        cor = cores.get(obj.intensidade, "#6c757d")
        intensidade_label = ["", "Leve", "Leve", "Moderada", "Severa", "Severa"][obj.intensidade]
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            cor,
            intensidade_label,
        )

    intensidade_badge.short_description = "Intensidade"


@admin.register(CicloMenstrual)
class CicloMenstrualAdmin(CustomAdminBase):
    list_display = ("usuario", "data_inicio", "data_fim", "duracao")
    list_filter = ("data_inicio", "data_fim")
    search_fields = ("usuario__nome_completo",)
    autocomplete_fields = ["usuario"]
    readonly_fields = ("duracao",)
    date_hierarchy = "data_inicio"


@admin.register(Exposicao)
class ExposicaoAdmin(CustomAdminBase):
    list_display = (
        "usuario",
        "carga_total_badge",
        "carga_estrogenica",
        "carga_androgenica",
        "carga_tireoidiana",
        "data_calculo",
    )
    list_filter = ("data_calculo",)
    search_fields = ("usuario__nome_completo",)
    autocomplete_fields = ["usuario"]
    readonly_fields = ("data_calculo",)
    inlines = [ExposicaoDetalheInline]
    date_hierarchy = "data_calculo"

    def carga_total_badge(self, obj):
        if obj.carga_total > 7:
            cor = "#dc3545"
            status = "ALTO"
        elif obj.carga_total > 5:
            cor = "#ffc107"
            status = "MODERADO"
        else:
            cor = "#28a745"
            status = "BAIXO"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold;">{:.2f} ({})</span>',
            cor,
            obj.carga_total,
            status,
        )

    carga_total_badge.short_description = "Carga Total"


@admin.register(AlertaRisco)
class AlertaRiscoAdmin(CustomAdminBase):
    list_display = (
        "usuario",
        "nivel_gravidade_badge",
        "data_emissao",
        "mensagem_alerta",
    )
    list_filter = ("nivel_gravidade", "data_emissao")
    search_fields = ("usuario__nome_completo", "mensagem_alerta")
    readonly_fields = ("data_emissao",)
    date_hierarchy = "data_emissao"

    def nivel_gravidade_badge(self, obj):
        cores = {
            "VERDE": "#28a745",
            "AMARELO": "#ffc107",
            "VERMELHO": "#dc3545",
        }
        cor = cores.get(obj.nivel_gravidade, "#6c757d")
        label = obj.get_nivel_gravidade_display()

        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold;">{}</span>',
            cor,
            label,
        )

    nivel_gravidade_badge.short_description = "Gravidade"


@admin.register(Notificacao)
class NotificacaoAdmin(CustomAdminBase):
    list_display = ("usuario", "tipo_notificacao", "lida_badge", "data_envio")
    list_filter = ("lida", "tipo_notificacao", "data_envio")
    search_fields = ("usuario__nome_completo", "mensagem")
    readonly_fields = ("data_envio",)
    actions = ["marcar_como_lida", "marcar_como_nao_lida"]
    date_hierarchy = "data_envio"

    def lida_badge(self, obj):
        if obj.lida:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold;">✓ Lida</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold;">✗ Não Lida</span>'
            )

    lida_badge.short_description = "Status"

    def marcar_como_lida(self, request, queryset):
        updated = queryset.update(lida=True)
        self.message_user(
            request, f"{updated} notificação(ões) marcada(s) como lida(s)."
        )

    marcar_como_lida.short_description = "✓ Marcar como lida"

    def marcar_como_nao_lida(self, request, queryset):
        updated = queryset.update(lida=False)
        self.message_user(
            request, f"{updated} notificação(ões) marcada(s) como não lida(s)."
        )

    marcar_como_nao_lida.short_description = "✗ Marcar como não lida"


# Customização do Site Admin
admin.site.site_header = "Flora - Administração"
admin.site.site_title = "Flora Admin"
admin.site.index_title = "Bem-vindo ao Painel de Administração Flora"
