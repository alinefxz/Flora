from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from saude.models import AlertaRisco, ArmarioItem, CicloMenstrual, RegistroSintoma
from .models import Admin, Cidade, Especialista, PerfilHormonal, Pessoa, UF, Usuario


class CidadeInline(admin.TabularInline):
    model = Cidade
    extra = 1


@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome_estado")
    search_fields = ("sigla", "nome_estado")
    inlines = [CidadeInline]


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome_cidade", "uf")
    list_filter = ("uf",)
    search_fields = ("nome_cidade", "uf__sigla", "uf__nome_estado")


class PerfilHormonalInline(admin.StackedInline):
    model = PerfilHormonal
    can_delete = False
    extra = 0


class ArmarioItemInline(admin.TabularInline):
    model = ArmarioItem
    extra = 1
    autocomplete_fields = ["produto"]


class RegistroSintomaInline(admin.TabularInline):
    model = RegistroSintoma
    extra = 0
    ordering = ("-data_ocorrencia",)
    autocomplete_fields = ["sintoma"]


class CicloMenstrualInline(admin.TabularInline):
    model = CicloMenstrual
    extra = 1
    fields = ("data_inicio", "data_fim", "duracao", "observacoes")
    ordering = ("-data_inicio",)


class AlertaRiscoInline(admin.TabularInline):
    model = AlertaRisco
    extra = 0
    readonly_fields = ("mensagem_alerta", "nivel_gravidade", "data_emissao")


class PessoaAdminBase(UserAdmin):
    list_display = (
        "email",
        "nome_completo",
        "tipo_usuario",
        "cidade",
        "data_nasc",
        "ativo",
        "is_staff",
    )
    list_filter = ("tipo_usuario", "ativo", "is_staff", "cidade__uf")
    search_fields = (
        "email",
        "username",
        "nome_completo",
        "cpf",
        "cidade__nome_cidade",
    )
    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Dados Flora",
            {
                "fields": (
                    "nome_completo",
                    "cpf",
                    "data_nasc",
                    "cidade",
                    "foto_perfil",
                    "ativo",
                )
            },
        ),
        ("Perfil Flora", {"fields": ("tipo_usuario",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Dados Flora",
            {
                "fields": (
                    "email",
                    "nome_completo",
                    "cpf",
                    "data_nasc",
                    "tipo_usuario",
                    "cidade",
                    "foto_perfil",
                    "ativo",
                )
            },
        ),
    )


@admin.register(Pessoa)
class PessoaAdmin(PessoaAdminBase):
    pass


@admin.register(Usuario)
class UsuarioAdmin(PessoaAdminBase):
    fieldsets = PessoaAdminBase.fieldsets + (
        ("Perfil de usuária", {"fields": ("apelido",)}),
    )
    inlines = [
        PerfilHormonalInline,
        CicloMenstrualInline,
        ArmarioItemInline,
        RegistroSintomaInline,
        AlertaRiscoInline,
    ]


@admin.register(Especialista)
class EspecialistaAdmin(PessoaAdminBase):
    fieldsets = PessoaAdminBase.fieldsets + (
        (
            "Dados profissionais",
            {
                "fields": (
                    "registro_profissional",
                    "especialidade",
                    "biografia",
                )
            },
        ),
    )


@admin.register(Admin)
class AdminAdmin(PessoaAdminBase):
    fieldsets = PessoaAdminBase.fieldsets + (
        ("Acesso administrativo", {"fields": ("nivel_acesso",)}),
    )


@admin.register(PerfilHormonal)
class PerfilHormonalAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "condicao_hormonal",
        "uso_contraceptivo",
        "ciclo_regular",
        "peso_sensibilidade",
    )
    search_fields = ("usuario__nome_completo", "condicao_hormonal")