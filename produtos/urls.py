from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    # Categorias (RF06, UI-ii: Listar/Editar produtos vinculados na mesma tela)
    path('categorias/', views.CategoriaListView.as_view(), name='listar_categorias'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='editar_categoria'),
    
    # Produtos (RF07, UI-iii: Gerenciar ingredientes direto no produto, UI-ix: Indicar substitutos seguros)
    path('', views.ProdutoListView.as_view(), name='listar_produtos'),
    path('novo/', views.ProdutoCreateView.as_view(), name='criar_produto'),
    path('<int:pk>/', views.ProdutoDetailView.as_view(), name='detalhar_produto'),
    path('<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='editar_produto'),
    path('<int:pk>/composicao/', views.GerenciarComposicaoView.as_view(), name='gerenciar_composicao'), # RF09
    
    # Ingredientes e Desreguladores (RF08, RF10, UI-vi: Cadastrar substância + upload de referências/Artigos RF19)
    path('ingredientes/', views.IngredienteListView.as_view(), name='listar_ingredientes'),
    path('substancias/', views.SubstanciaListView.as_view(), name='listar_substancias'),
    path('substancias/nova/', views.SubstanciaCreateView.as_view(), name='criar_substancia'),
    path('substancias/<int:pk>/referencias/', views.GerenciarReferenciasView.as_view(), name='gerenciar_referencias'),
    
    # Eixos Hormonais (RF11, UI-vii: Listar todos os químicos associados ao eixo)
    path('eixos-hormonais/', views.TipoDesreguladorListView.as_view(), name='listar_eixos'),
    path('eixos-hormonais/<int:pk>/', views.TipoDesreguladorDetailView.as_view(), name='detalhar_eixo'),
    
    # Substituições Inteligentes (RF18)
    path('sugestoes-troca/', views.SugestaoTrocaListView.as_view(), name='listar_sugestoes'),
]