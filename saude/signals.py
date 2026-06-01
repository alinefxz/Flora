from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from produtos.models import ProdutoIngrediente
from .models import ArmarioItem
from .services import calcular_exposicao_usuario


@receiver([post_save, post_delete], sender=ArmarioItem)
def recalcular_exposicao_ao_alterar_armario(sender, instance, **kwargs):
    calcular_exposicao_usuario(instance.usuario)


@receiver([post_save, post_delete], sender=ProdutoIngrediente)
def recalcular_produto_e_usuarios(sender, instance, **kwargs):
    produto = instance.produto
    produto.recalcular_nota_flora()

    usuarios = produto.usuarios_no_armario.select_related("usuario")
    for item in usuarios:
        calcular_exposicao_usuario(item.usuario)