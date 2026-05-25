from django.contrib import admin
from .models import Categoria, TipoDesregulador, Substancia, Produto, Ingrediente, ProdutoIngrediente, SugestaoTroca, Referencia

# ii) Categoria e Produtos inline
class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1
    fields = ('nome', 'marca', 'codigo_barras', 'fabricante', 'nota_flora')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    inlines = [ProdutoInline]

# vii) Tipos de Desreguladores e Substâncias inline
class SubstanciaInline(admin.TabularInline):
    model = Substancia
    extra = 1
    fields = ('nome', 'cas_number', 'nivel_risco')

@admin.register(TipoDesregulador)
class TipoDesreguladorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    inlines = [SubstanciaInline]

# vi) Substância e Referências inline
class ReferenciaInline(admin.TabularInline):
    model = Referencia
    extra = 1

@admin.register(Substancia)
class SubstanciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cas_number', 'nivel_risco', 'tipo_desregulador')
    list_filter = ('nivel_risco', 'tipo_desregulador')
    search_fields = ('nome', 'cas_number')
    inlines = [ReferenciaInline]

# iii) Produto e Composição (Ingredientes) inline
class ProdutoIngredienteInline(admin.TabularInline):
    model = ProdutoIngrediente
    extra = 1

# ix) Produtos e Sugestões de Troca inline (Focado no produto com risco)
class SugestaoTrocaInline(admin.TabularInline):
    model = SugestaoTroca
    fk_name = 'produto_risco' # Aponta especificamente que este produto gerará as alternativas seguras
    extra = 1

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'categoria', 'fabricante', 'nota_flora')
    list_filter = ('categoria', 'marca')
    search_fields = ('nome', 'marca', 'codigo_barras')
    inlines = [ProdutoIngredienteInline, SugestaoTrocaInline]

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'funcao_quimica', 'substancia')
    search_fields = ('nome', 'funcao_quimica')

@admin.register(SugestaoTroca)
class SugestaoTrocaAdmin(admin.ModelAdmin):
    list_display = ('produto_risco', 'produto_seguro', 'confianca', 'especialista')

@admin.register(Referencia)
class ReferenciaAdmin(admin.ModelAdmin):
    list_display = ('titulo_artigo', 'ano_publicacao', 'substancia', 'instituicao_fonte')