from django.urls import path
from . import views

app_name = "saude"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("usuarios/<int:usuario_id>/armario/", views.listar_armario, name="listar_armario"),
    path("usuarios/<int:usuario_id>/exposicoes/", views.historico_exposicao, name="historico_exposicao"),
    path("usuarios/<int:usuario_id>/alertas/", views.listar_alertas, name="listar_alertas"),
    path("usuarios/<int:usuario_id>/relatorio.csv", views.exportar_relatorio_csv, name="exportar_relatorio_csv"),
    path("auditoria/geral/", views.auditoria_sistema, name="auditoria_sistema"),
]