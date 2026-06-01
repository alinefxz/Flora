from django.urls import path
from . import frontend

app_name = "saude"

urlpatterns = [
    path("entrar/", frontend.entrar, name="entrar"),
    path("cadastrar/", frontend.cadastrar, name="cadastrar"),
    path("sair/", frontend.sair, name="sair"),

    path("", frontend.dashboard, name="dashboard"),
    path("dados/<slug:slug>/", frontend.lista, name="lista"),
    path("dados/<slug:slug>/novo/", frontend.criar, name="criar"),
    path("dados/<slug:slug>/<int:pk>/", frontend.detalhe, name="detalhe"),
    path("dados/<slug:slug>/<int:pk>/editar/", frontend.editar, name="editar"),
    path("dados/<slug:slug>/<int:pk>/excluir/", frontend.excluir, name="excluir"),
]