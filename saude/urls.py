from django.urls import path

from . import frontend, social

app_name = "saude"

urlpatterns = [
    path("entrar/", frontend.entrar, name="entrar"),
    path("cadastrar/", frontend.cadastrar, name="cadastrar"),
    path("sair/", frontend.sair, name="sair"),

    path("", frontend.dashboard, name="dashboard"),

    path("catalogo/", social.catalogo, name="catalogo"),
    path(
        "catalogo/produto/<int:pk>/",
        social.produto_social,
        name="produto_social",
    ),
    path(
        "catalogo/produto/<int:pk>/comentar/",
        social.comentar_produto,
        name="comentar_produto",
    ),
    path(
        "comentarios/<int:pk>/curtir/",
        social.curtir_comentario,
        name="curtir_comentario",
    ),

    path("meu-armario/", social.armario, name="armario"),
    path(
        "meu-armario/adicionar/",
        social.adicionar_armario,
        name="adicionar_armario",
    ),
    path(
        "meu-armario/<int:pk>/atualizar/",
        social.atualizar_armario,
        name="atualizar_armario",
    ),
    path(
        "meu-armario/<int:pk>/remover/",
        social.remover_armario,
        name="remover_armario",
    ),

    path("meu-perfil/", social.perfil, name="perfil"),
    path(
        "especialistas/",
        social.especialistas,
        name="especialistas",
    ),
    path(
        "especialistas/<int:pk>/",
        social.perfil_especialista,
        name="perfil_especialista",
    ),

    path("sugestoes/", social.sugestoes, name="sugestoes"),
    path(
        "sugestoes/nova/",
        social.sugestao_nova,
        name="sugestao_nova",
    ),
    path(
        "sugestoes/<int:pk>/editar/",
        social.sugestao_editar,
        name="sugestao_editar",
    ),

    path("dados/<slug:slug>/", frontend.lista, name="lista"),
    path(
        "dados/<slug:slug>/novo/",
        frontend.criar,
        name="criar",
    ),
    path(
        "dados/<slug:slug>/<int:pk>/",
        frontend.detalhe,
        name="detalhe",
    ),
    path(
        "dados/<slug:slug>/<int:pk>/editar/",
        frontend.editar,
        name="editar",
    ),
    path(
        "dados/<slug:slug>/<int:pk>/excluir/",
        frontend.excluir,
        name="excluir",
    ),
    path(
        "notificacoes/<int:pk>/ler/",
        frontend.marcar_notificacao,
        name="marcar_notificacao",
    ),
]