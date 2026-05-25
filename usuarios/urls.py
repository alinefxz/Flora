from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # # path('login/', views.PessoaLoginView.as_view(), name='login'), 
    # # path('logout/', views.PessoaLogoutView.as_view(), name='logout'),
    # # path('cadastro/usuaria/', views.CadastroUsuariaView.as_view(), name='cadastro_usuaria'),
    # # path('cadastro/especialista/', views.CadastroEspecialistaView.as_view(), name='cadastro_especialista'),
    # # path('perfil/', views.PerfilUsuariaView.as_view(), name='perfil_usuaria'),
    # # path('perfil/editar-clinico/', views.EditarPerfilHormonalView.as_view(), name='editar_perfil_hormonal'),
    # # path('senha/alterar/', views.AlteracaoSenhaView.as_view(), name='alterar_senha'),
    # # path('senha/recuperar/', views.RecuperacaoSenhaView.as_view(), name='recuperar_senha'),
    # # path('estados/', views.UFListView.as_view(), name='listar_ufs'),
    # # path('estados/<int:uf_id>/cidades/', views.CidadePorUFListView.as_view(), name='cidades_por_uf'),
]