from datetime import date


def calcular_fase_menstrual(usuario, data_referencia: date) -> str:
    ultimo_ciclo = usuario.ciclos.filter(data_inicio__lte=data_referencia).order_by("-data_inicio").first()

    if not ultimo_ciclo:
        return "Indefinida"

    duracao_media = 28
    if hasattr(usuario, "perfil_hormonal"):
        duracao_media = usuario.perfil_hormonal.duracao_ciclo or 28

    dia = ((data_referencia - ultimo_ciclo.data_inicio).days % duracao_media) + 1

    if dia <= 5:
        return "Menstrual"
    if dia <= max(6, duracao_media // 2 - 2):
        return "Folicular"
    if dia <= max(7, duracao_media // 2 + 2):
        return "Ovulatória"
    return "Lútea"


def limite_seguranca(usuario) -> float:
    limite = 100.0
    perfil = getattr(usuario, "perfil_hormonal", None)

    if not perfil:
        return limite

    condicao = (perfil.condicao_hormonal or "").lower()

    if "sop" in condicao or "endometriose" in condicao:
        limite *= 0.75

    if perfil.uso_contraceptivo:
        limite *= 0.9

    return limite / max(perfil.peso_sensibilidade, 0.1)


def calcular_exposicao_usuario(usuario):
    from .models import AlertaRisco, Exposicao, ExposicaoDetalhe, Notificacao

    perfil = getattr(usuario, "perfil_hormonal", None)
    fator = perfil.peso_sensibilidade if perfil else 1.0

    totais = {
        "estrogenica": 0.0,
        "androgenica": 0.0,
        "tireoidiana": 0.0,
    }

    detalhes = []

    armario = usuario.armario.select_related("produto").prefetch_related(
        "produto__composicao__ingrediente__substancia__tipo_desregulador"
    )

    for item in armario:
        for composicao in item.produto.composicao.all():
            substancia = composicao.ingrediente.substancia
            if not substancia:
                continue

            valor = (
                substancia.nivel_risco
                * item.frequencia_uso
                * max(composicao.concentracao_estimada, 0)
                * fator
            )

            eixo = substancia.tipo_desregulador.nome.lower()
            if "estrog" in eixo:
                totais["estrogenica"] += valor
            elif "andro" in eixo:
                totais["androgenica"] += valor
            elif "tireo" in eixo:
                totais["tireoidiana"] += valor

            detalhes.append((item.produto, substancia, valor))

    carga_total = sum(totais.values())

    exposicao = Exposicao.objects.create(
        usuario=usuario,
        carga_estrogenica=round(totais["estrogenica"], 2),
        carga_androgenica=round(totais["androgenica"], 2),
        carga_tireoidiana=round(totais["tireoidiana"], 2),
        carga_total=round(carga_total, 2),
    )

    ExposicaoDetalhe.objects.bulk_create([
        ExposicaoDetalhe(
            exposicao=exposicao,
            produto=produto,
            substancia=substancia,
            valor_contribuicao=round(valor, 2),
        )
        for produto, substancia, valor in detalhes
    ])

    emitir_alerta(usuario, exposicao)
    return exposicao


def emitir_alerta(usuario, exposicao):
    from .models import AlertaRisco, Notificacao

    limite = limite_seguranca(usuario)
    percentual = exposicao.carga_total / limite if limite else 0

    if percentual >= 0.75:
        gravidade = "VERMELHO"
        mensagem = "Carga hormonal elevada. Recomenda-se revisar produtos de maior risco no Armário Virtual."
    elif percentual >= 0.5:
        gravidade = "AMARELO"
        mensagem = "Carga hormonal moderada. Há pontos de atenção na exposição acumulada."
    else:
        gravidade = "VERDE"
        mensagem = "Carga hormonal dentro da faixa de menor risco."

    AlertaRisco.objects.create(
        usuario=usuario,
        nivel_gravidade=gravidade,
        mensagem_alerta=mensagem,
    )

    if gravidade in ["AMARELO", "VERMELHO"]:
        Notificacao.objects.create(
            usuario=usuario,
            tipo_notificacao="ALERTA_RISCO",
            mensagem=mensagem,
        )

    ultimos_alertas = list(usuario.alertas_risco.order_by("-data_emissao")[:3])
    sintomas_graves = usuario.diario_sintomas.filter(intensidade__gt=4).exists()

    if len(ultimos_alertas) == 3 and all(a.nivel_gravidade == "VERMELHO" for a in ultimos_alertas) and sintomas_graves:
        Notificacao.objects.create(
            usuario=usuario,
            tipo_notificacao="RELATORIO_MEDICO",
            mensagem="A carga hormonal permaneceu em nível vermelho por 3 ciclos e há sintomas intensos. Exporte o relatório para acompanhamento com especialista.",
        )