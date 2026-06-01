from django.urls import path
from . import views

app_name = "produtos"

urlpatterns = [
    path("categorias/", views.listar_categorias, name="listar_categorias"),
    path("", views.listar_produtos, name="listar_produtos"),
    path("<int:pk>/", views.detalhe_produto, name="detalhe_produto"),
    path("substancias/", views.listar_substancias, name="listar_substancias"),
    path("eixos-hormonais/", views.listar_eixos, name="listar_eixos"),
    path("sugestoes-troca/", views.listar_sugestoes, name="listar_sugestoes"),
]