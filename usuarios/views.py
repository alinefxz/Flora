from django.http import JsonResponse
from .models import Cidade, UF, Usuario


def listar_ufs(request):
    dados = [{"id": uf.id, "sigla": uf.sigla, "nome_estado": uf.nome_estado} for uf in UF.objects.all()]
    return JsonResponse({"ufs": dados})


def cidades_por_uf(request, uf_id):
    cidades = Cidade.objects.filter(uf_id=uf_id)
    dados = [{"id": cidade.id, "nome_cidade": cidade.nome_cidade} for cidade in cidades]
    return JsonResponse({"cidades": dados})


def listar_usuarias(request):
    usuarias = Usuario.objects.select_related("cidade", "cidade__uf")
    dados = [
        {
            "id": u.id,
            "nome_completo": u.nome_completo,
            "apelido": u.apelido,
            "email": u.email,
            "cpf": u.cpf_mascarado,
            "cidade": str(u.cidade) if u.cidade else None,
        }
        for u in usuarias
    ]
    return JsonResponse({"usuarias": dados})