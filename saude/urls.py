from django.urls import path
from . import views

app_name = 'saude'

urlpatterns = [
    # # Dashboard Principal (RF23: Gráfico Radar do mapa hormonal pessoal)
    # path('', views.DashboardView.as_view(), name='dashboard'),
    
    # # Armário Virtual (RF12, UI-iv: Ajustar frequências de uso)
    # path('armario/', views.ArmarioVirtualView.as_view(), name='armario_virtual'),
    # path('armario/adicionar/', views.AdicionarAoArmarioView.as_view(), name='adicionar_armario'),
    # path('armario/remover/<int:pk>/', views.RemoverDoArmarioView.as_view(), name='remover_armario'),
    
    # # Sintomas e Ciclos Menstruais (RF13, RF14, RF15, RN06: Cálculo de Fase Menstrual automático)
    # path('diario/ciclo/', views.CicloMenstrualListView.as_view(), name='historico_ciclos'),
    # path('diario/ciclo/registrar/', views.CicloMenstrualCreateView.as_view(), name='registrar_ciclo'),
    # path('diario/sintoma/registrar/', views.RegistroSintomaCreateView.as_view(), name='registrar_sintoma'),
    
    # # Histórico de Exposição e Alertas (RF16, RF17, RF24, RF25, RN04/RN05)
    # path('exposicao/historico/', views.ExposicaoListView.as_view(), name='historico_exposicao'),
    # path('alertas/', views.AlertaRiscoListView.as_view(), name='listar_alertas'),
    # path('notificacoes/ler/<int:pk>/', views.MarcarNotificacaoLidaView.as_view(), name='ler_notificacao'),
    
    # # Exportação de Relatórios Clínicos (RF28 - Suporta formatos PDF/CSV)
    # path('exposicao/exportar/<str:formato>/', views.ExportarRelatorioView.as_view(), name='exportar_relatorio'),
    
    # # Auditoria Acadêmica / Administrativa (RNF04: Listagem HTML de auditoria de todos os dados salvos)
    # path('auditoria/geral/', views.AuditoriaDadosView.as_view(), name='auditoria_sistema'),
]