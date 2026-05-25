from django.contrib import admin
from .models import ArmarioItem, Sintoma, RegistroSintoma, CicloMenstrual, Exposicao, ExposicaoDetalhe, AlertaRisco, Notificacao

# Registrando os modelos de Saúde e Monitoramento no Painel Administrativo
admin.site.register(ArmarioItem)
admin.site.register(Sintoma)
admin.site.register(RegistroSintoma)
admin.site.register(CicloMenstrual)
admin.site.register(Exposicao)
admin.site.register(ExposicaoDetalhe)
admin.site.register(AlertaRisco)
admin.site.register(Notificacao)