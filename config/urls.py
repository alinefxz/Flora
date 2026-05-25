from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Módulos do Sistema FLORA
    path('', include('saude.urls')),          # Centraliza o Dashboard e Diários na raiz
    path('usuarios/', include('usuarios.urls')), # Fluxos de usuários, perfis e login
    path('produtos/', include('produtos.urls')), # Catálogo de produtos, substâncias e trocas
]

# Configuração para servir arquivos de mídia (Fotos de perfil e de produtos) em Desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_block=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)