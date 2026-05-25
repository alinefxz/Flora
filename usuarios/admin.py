from django.contrib import admin
from .models import UF, Cidade, Pessoa, Usuario, Especialista, Admin, PerfilHormonal

# Registrando os modelos de Usuários no Painel Administrativo
admin.site.register(UF)
admin.site.register(Cidade)
admin.site.register(Pessoa)
admin.site.register(Usuario)
admin.site.register(Especialista)
admin.site.register(Admin)
admin.site.register(PerfilHormonal)