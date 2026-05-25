from django.contrib import admin
from .models import Categoria, TipoDesregulador, Substancia, Produto, Ingrediente, ProdutoIngrediente, SugestaoTroca, Referencia

# Registrando os modelos de Produtos e Química no Painel Administrativo
admin.site.register(Categoria)
admin.site.register(TipoDesregulador)
admin.site.register(Substancia)
admin.site.register(Produto)
admin.site.register(Ingrediente)
admin.site.register(ProdutoIngrediente)
admin.site.register(SugestaoTroca)
admin.site.register(Referencia)