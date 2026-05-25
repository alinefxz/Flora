from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UF, Cidade, Pessoa, Usuario, Especialista, Admin, PerfilHormonal
from saude.models import ArmarioItem, RegistroSintoma, AlertaRisco

# viii) UF e Cidades inline
class CidadeInline(admin.TabularInline):
    model = Cidade
    extra = 1

@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome_estado')
    search_fields = ('sigla', 'nome_estado')
    inlines = [CidadeInline]

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome_cidade', 'uf')
    list_filter = ('uf',)
    search_fields = ('nome_cidade',)

# --- INLINES DA FICHA DA USUÁRIA ---

# i) Usuárias e Perfil Hormonal inline
class PerfilHormonalInline(admin.StackedInline): # Stacked fica mais organizado para formulários longos
    model = PerfilHormonal
    can_delete = False
    verbose_name = "Perfil Hormonal Clínico"

# iv) Usuária e Armário Virtual inline
class ArmarioItemInline(admin.TabularInline):
    model = ArmarioItem
    extra = 1
    autocomplete_fields = ['produto'] # Melhora a busca se houver muitos produtos

# v) Usuária e Registro de Sintomas inline
class RegistroSintomaInline(admin.TabularInline):
    model = RegistroSintoma
    extra = 0
    ordering = ('-data_ocorrencia',) # Histórico cronológico (mais recente primeiro)

# x) Usuária e Alertas de Risco inline
class AlertaRiscoInline(admin.TabularInline):
    model = AlertaRisco
    extra = 0
    readonly_fields = ('data_emissao',)

# --- GERENCIAMENTO SEGURO DE USUÁRIOS (Herdando do Django UserAdmin) ---

@admin.register(Pessoa)
class PessoaAdmin(UserAdmin):
    list_display = ('email', 'username', 'nome_completo', 'tipo_usuario', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'nome_completo', 'cpf')
    ordering = ('email',)
    
    # Organiza os campos no formulário de edição do Django
    fieldsets = UserAdmin.fieldsets + (
        ('Campos Específicos do FLORA', {'fields': ('nome_completo', 'cpf', 'data_nasc', 'tipo_usuario', 'cidade', 'ativo')}),
    )

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome_completo', 'apelido', 'cidade', 'ativo')
    search_fields = ('email', 'nome_completo', 'cpf', 'apelido')
    list_filter = ('ativo', 'cidade__uf')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações de Usuária FLORA', {'fields': ('nome_completo', 'cpf', 'data_nasc', 'tipo_usuario', 'cidade', 'ativo', 'apelido', 'foto_perfil')}),
    )
    # Acopla todas as visões diretamente na ficha da Usuária
    inlines = [PerfilHormonalInline, ArmarioItemInline, RegistroSintomaInline, AlertaRiscoInline]

@admin.register(Especialista)
class EspecialistaAdmin(UserAdmin):
    list_display = ('email', 'nome_completo', 'especialidade', 'registro_profissional', 'is_active')
    search_fields = ('email', 'nome_completo', 'registro_profissional', 'especialidade')
    list_filter = ('especialidade', 'is_active')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Credenciais do Especialista', {'fields': ('nome_completo', 'cpf', 'data_nasc', 'tipo_usuario', 'cidade', 'ativo', 'registro_profissional', 'especialidade', 'biografia')}),
    )

@admin.register(Admin)
class AdminAdmin(UserAdmin):
    list_display = ('email', 'nome_completo', 'nivel_acesso', 'is_superuser')
    search_fields = ('email', 'nome_completo')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Controles de Administrador', {'fields': ('nome_completo', 'cpf', 'data_nasc', 'tipo_usuario', 'cidade', 'ativo', 'nivel_acesso')}),
    )

@admin.register(PerfilHormonal)
class PerfilHormonalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'uso_contraceptivo', 'ciclo_regular', 'duracao_ciclo', 'fluxo_menstrual')