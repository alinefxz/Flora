from django.urls import path

from . import views


app_name = "usuarios"

urlpatterns = [
    path(
        "",
        views.listar_usuarias,
        name="listar_usuarias",
    ),
    path(
        "ufs/",
        views.listar_ufs,
        name="listar_ufs",
    ),
    path(
        "ufs/<int:uf_id>/cidades/",
        views.cidades_por_uf,
        name="cidades_por_uf",
    ),
    path(
        "cidades/cadastrar/",
        views.cadastrar_cidade,
        name="cadastrar_cidade",
    ),
]