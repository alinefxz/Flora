from django.http import JsonResponse
from .models import Categoria, Produto, Substancia, SugestaoTroca, TipoDesregulador


def listar_categorias(request):
    dados = [
        {
            "id": categoria.id,
            "nome": categoria.nome,
            "descricao": categoria.descricao,
            "total_produtos": categoria.produtos.count(),
        }
        for categoria in Categoria.objects.all()
    ]
    return JsonResponse({"categorias": dados})


def listar_produtos(request):
    produtos = Produto.objects.select_related("categoria").all()
    dados = [
        {
            "id": p.id,
            "nome": p.nome,
            "marca": p.marca,
            "codigo_barras": p.codigo_barras,
            "categoria": p.categoria.nome,
            "fabricante": p.fabricante,
            "nota_flora": p.nota_flora,
        }
        for p in produtos
    ]
    return JsonResponse({"produtos": dados})


def detalhe_produto(request, pk):
    produto = Produto.objects.select_related("categoria").prefetch_related("composicao__ingrediente__substancia").get(pk=pk)
    composicao = [
        {
            "ingrediente": item.ingrediente.nome,
            "funcao_quimica": item.ingrediente.funcao_quimica,
            "substancia": item.ingrediente.substancia.nome if item.ingrediente.substancia else None,
            "concentracao": item.concentracao_estimada,
            "unidade": item.unidade_concentracao,
        }
        for item in produto.composicao.all()
    ]

    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome,
        "marca": produto.marca,
        "categoria": produto.categoria.nome,
        "nota_flora": produto.nota_flora,
        "composicao": composicao,
    })


def listar_substancias(request):
    substancias = Substancia.objects.select_related("tipo_desregulador")
    dados = [
        {
            "id": s.id,
            "nome": s.nome,
            "cas_number": s.cas_number,
            "nivel_risco": s.nivel_risco,
            "tipo_desregulador": s.tipo_desregulador.nome,
        }
        for s in substancias
    ]
    return JsonResponse({"substancias": dados})


def listar_eixos(request):
    dados = [
        {
            "id": eixo.id,
            "nome": eixo.nome,
            "descricao": eixo.descricao,
            "substancias": [s.nome for s in eixo.substancias.all()],
        }
        for eixo in TipoDesregulador.objects.prefetch_related("substancias")
    ]
    return JsonResponse({"eixos": dados})


def listar_sugestoes(request):
    sugestoes = SugestaoTroca.objects.select_related("produto_risco", "produto_seguro", "especialista")
    dados = [
        {
            "produto_risco": s.produto_risco.nome,
            "produto_seguro": s.produto_seguro.nome,
            "justificativa": s.justificativa_tecnica,
            "confianca": s.confianca,
            "especialista": s.especialista.nome_completo if s.especialista else None,
        }
        for s in sugestoes
    ]
    return JsonResponse({"sugestoes": dados})