import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from produtos.models import Produto, Substancia
from usuarios.models import Usuario
from .models import AlertaRisco, ArmarioItem, CicloMenstrual, Exposicao, Notificacao, RegistroSintoma, Sintoma
from .services import calcular_exposicao_usuario


def resposta_json(dados, status=200):
    return JsonResponse(dados, status=status, json_dumps_params={"ensure_ascii": False})


def dashboard(request):
    usuario_id = request.GET.get("usuario_id")
    usuario = get_object_or_404(Usuario, pk=usuario_id) if usuario_id else Usuario.objects.first()

    if not usuario:
        return resposta_json({
            "status": "Backend FLORA funcionando",
            "mensagem": "Nenhuma usuária cadastrada ainda. Acesse /admin/ para cadastrar os dados iniciais.",
            "rotas": {
                "admin": "/admin/",
                "auditoria": "/auditoria/geral/",
                "produtos": "/produtos/",
                "categorias": "/produtos/categorias/",
                "substancias": "/produtos/substancias/",
                "usuarias": "/usuarios/",
            }
        })

    exposicao = usuario.historico_exposicoes.first()

    if not exposicao:
        exposicao = calcular_exposicao_usuario(usuario)

    return resposta_json({
        "usuario": usuario.nome_completo,
        "radar": {
            "estrogenica": exposicao.carga_estrogenica,
            "androgenica": exposicao.carga_androgenica,
            "tireoidiana": exposicao.carga_tireoidiana,
        },
        "carga_total": exposicao.carga_total,
        "data_calculo": exposicao.data_calculo,
    })


def listar_armario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    itens = usuario.armario.select_related("produto")
    dados = [
        {
            "id": item.id,
            "produto": item.produto.nome,
            "marca": item.produto.marca,
            "frequencia_uso": item.frequencia_uso,
            "nota_flora": item.produto.nota_flora,
        }
        for item in itens
    ]
    return resposta_json({"usuario": usuario.nome_completo, "armario": dados})


def historico_exposicao(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    dados = [
        {
            "data_calculo": e.data_calculo,
            "carga_estrogenica": e.carga_estrogenica,
            "carga_androgenica": e.carga_androgenica,
            "carga_tireoidiana": e.carga_tireoidiana,
            "carga_total": e.carga_total,
        }
        for e in usuario.historico_exposicoes.all()
    ]
    return resposta_json({"usuario": usuario.nome_completo, "exposicoes": dados})


def listar_alertas(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    dados = [
        {
            "nivel": alerta.nivel_gravidade,
            "mensagem": alerta.mensagem_alerta,
            "data": alerta.data_emissao,
        }
        for alerta in usuario.alertas_risco.all()
    ]
    return resposta_json({"alertas": dados})


def auditoria_sistema(request):
    return resposta_json({
        "usuarios": Usuario.objects.count(),
        "produtos": Produto.objects.count(),
        "substancias": Substancia.objects.count(),
        "armario_itens": ArmarioItem.objects.count(),
        "sintomas": Sintoma.objects.count(),
        "registros_sintomas": RegistroSintoma.objects.count(),
        "ciclos": CicloMenstrual.objects.count(),
        "exposicoes": Exposicao.objects.count(),
        "alertas": AlertaRisco.objects.count(),
        "notificacoes": Notificacao.objects.count(),
    })


def exportar_relatorio_csv(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="relatorio_flora_{usuario.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Data", "Estrogênica", "Androgênica", "Tireoidiana", "Total"])

    for exposicao in usuario.historico_exposicoes.all():
        writer.writerow([
            exposicao.data_calculo,
            exposicao.carga_estrogenica,
            exposicao.carga_androgenica,
            exposicao.carga_tireoidiana,
            exposicao.carga_total,
        ])

    return response

@login_required(login_url="saude:entrar")
def editar_perfil(request):
    # O SEGREDO ESTÁ AQUI: Passar a instance=request.user para carregar e salvar os dados corretamente
    if request.method == "POST":
        form = CadastroForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("saude:perfil") # Ou a rota correta do seu painel
    else:
        # Carrega os dados que já existem para a pessoa não ter que digitar tudo de novo
        form = CadastroForm(instance=request.user)

    contexto = {
        "form": form,
        "titulo_form": "Editar Perfil",
    }
    return render(request, "formulario.html", contexto)