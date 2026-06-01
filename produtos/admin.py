from django.contrib import admin
from .models import Categoria, Ingrediente, Produto, ProdutoIngrediente, Referencia, Substancia, SugestaoTroca, TipoDesregulador


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1
    fields = ("nome", "marca", "codigo_barras", "fabricante", "nota_flora")
    readonly_fields = ("nota_flora",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)
    inlines = [ProdutoInline]


class SubstanciaInline(admin.TabularInline):
    model = Substancia
    extra = 1


@admin.register(TipoDesregulador)
class TipoDesreguladorAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)
    inlines = [SubstanciaInline]


class ReferenciaInline(admin.TabularInline):
    model = Referencia
    extra = 1


@admin.register(Substancia)
class SubstanciaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cas_number", "nivel_risco", "tipo_desregulador")
    list_filter = ("nivel_risco", "tipo_desregulador")
    search_fields = ("nome", "cas_number")
    inlines = [ReferenciaInline]


class ProdutoIngredienteInline(admin.TabularInline):
    model = ProdutoIngrediente
    extra = 1
    autocomplete_fields = ["ingrediente"]


class SugestaoTrocaInline(admin.TabularInline):
    model = SugestaoTroca
    fk_name = "produto_risco"
    extra = 1
    autocomplete_fields = ["produto_seguro", "especialista"]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "marca", "categoria", "fabricante", "nota_flora")
    list_filter = ("categoria", "marca")
    search_fields = ("nome", "marca", "codigo_barras")
    readonly_fields = ("nota_flora",)
    inlines = [ProdutoIngredienteInline, SugestaoTrocaInline]


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "funcao_quimica", "substancia")
    search_fields = ("nome", "funcao_quimica", "substancia__nome")


@admin.register(SugestaoTroca)
class SugestaoTrocaAdmin(admin.ModelAdmin):
    list_display = ("produto_risco", "produto_seguro", "confianca", "especialista")
    autocomplete_fields = ["produto_risco", "produto_seguro", "especialista"]


@admin.register(Referencia)
class ReferenciaAdmin(admin.ModelAdmin):
    list_display = ("titulo_artigo", "ano_publicacao", "substancia", "instituicao_fonte")
    search_fields = ("titulo_artigo", "autores", "substancia__nome")