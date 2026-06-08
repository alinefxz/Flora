from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from produtos.models import (
    Categoria,
    Ingrediente,
    Produto,
    ProdutoIngrediente,
    Referencia,
    Substancia,
    SugestaoTroca,
    TipoDesregulador,
)
from usuarios.models import (
    Admin,
    Cidade,
    Especialista,
    PerfilHormonal,
    Pessoa,
    UF,
    Usuario,
)
from .forms import (
    AdminFloraForm,
    ArmarioItemForm,
    CadastroForm,
    CategoriaForm,
    CidadeForm,
    CicloMenstrualForm,
    EspecialistaForm,
    IngredienteForm,
    LoginForm,
    PessoaForm,
    PerfilHormonalForm,
    ProdutoForm,
    ProdutoIngredienteForm,
    ReferenciaForm,
    RegistroSintomaForm,
    SintomaForm,
    SubstanciaForm,
    SugestaoTrocaForm,
    TipoDesreguladorForm,
    UFForm,
    UsuarioForm,
)
from .models import (
    AlertaRisco,
    ArmarioItem,
    CicloMenstrual,
    Exposicao,
    ExposicaoDetalhe,
    Notificacao,
    RegistroSintoma,
    Sintoma,
)


ADMIN = "ADMIN"
USUARIA = "USUARIA"
ESPECIALISTA = "ESPECIALISTA"


def entidade(
    titulo,
    secao,
    model,
    form,
    colunas,
    busca=(),
    visualizar=(ADMIN,),
    editar=(ADMIN,),
    filtro=None,
    owner_lookup=None,
    owner_field=None,
    specialist_field=None,
):
    return {
        "titulo": titulo,
        "secao": secao,
        "model": model,
        "form": form,
        "colunas": colunas,
        "busca": busca,
        "visualizar": set(visualizar),
        "editar": set(editar),
        "filtro": filtro or {},
        "owner_lookup": owner_lookup,
        "owner_field": owner_field,
        "specialist_field": specialist_field,
    }


ENTIDADES = {
    "pessoas": entidade(
        "Pessoas", "Administração", Pessoa, PessoaForm,
        ["nome_completo", "email", "cpf", "tipo_usuario", "ativo"],
        ["nome_completo", "email", "cpf"],
    ),
    "usuarias": entidade(
        "Usuárias", "Administração", Usuario, UsuarioForm,
        ["nome_completo", "email", "data_nasc", "apelido", "ativo"],
        ["nome_completo", "email", "cpf", "apelido"],
        filtro={"tipo_usuario": "USUARIA"},
    ),
    "especialistas": entidade(
        "Especialistas", "Administração", Especialista,
        EspecialistaForm,
        [
            "nome_completo",
            "email",
            "registro_profissional",
            "especialidade",
            "ativo",
        ],
        [
            "nome_completo",
            "email",
            "registro_profissional",
            "especialidade",
        ],
        filtro={"tipo_usuario": "ESPECIALISTA"},
    ),
    "administradores": entidade(
        "Administradores", "Administração", Admin,
        AdminFloraForm,
        ["nome_completo", "email", "nivel_acesso", "ativo"],
        ["nome_completo", "email", "nivel_acesso"],
        filtro={"tipo_usuario": "ADMIN"},
    ),
    "ufs": entidade(
        "UFs", "Administração", UF, UFForm,
        ["nome_estado", "sigla"],
        ["nome_estado", "sigla"],
    ),
    "cidades": entidade(
        "Cidades", "Administração", Cidade, CidadeForm,
        ["nome_cidade", "uf"],
        ["nome_cidade", "uf__sigla"],
    ),
    "categorias": entidade(
        "Categorias", "Catálogo", Categoria, CategoriaForm,
        ["nome", "descricao"],
        ["nome", "descricao"],
    ),
    "produtos": entidade(
        "Produtos", "Catálogo", Produto, ProdutoForm,
        ["nome", "marca", "categoria", "fabricante", "nota_flora"],
        ["nome", "marca", "codigo_barras", "fabricante"],
        visualizar=(ADMIN, ESPECIALISTA),
    ),
    "ingredientes": entidade(
        "Ingredientes", "Catálogo", Ingrediente,
        IngredienteForm,
        ["nome", "funcao_quimica", "substancia"],
        ["nome", "funcao_quimica", "substancia__nome"],
        visualizar=(ADMIN, ESPECIALISTA),
    ),
    "composicoes": entidade(
        "Composição dos produtos", "Catálogo",
        ProdutoIngrediente, ProdutoIngredienteForm,
        [
            "produto",
            "ingrediente",
            "concentracao_estimada",
            "unidade_concentracao",
        ],
        ["produto__nome", "ingrediente__nome"],
        visualizar=(ADMIN, ESPECIALISTA),
    ),
    "tipos-desreguladores": entidade(
        "Eixos hormonais", "Análise técnica",
        TipoDesregulador, TipoDesreguladorForm,
        ["nome", "descricao"],
        ["nome", "descricao"],
        visualizar=(ADMIN, ESPECIALISTA),
        editar=(ADMIN, ESPECIALISTA),
    ),
    "substancias": entidade(
        "Substâncias", "Análise técnica",
        Substancia, SubstanciaForm,
        ["nome", "cas_number", "nivel_risco", "tipo_desregulador"],
        ["nome", "cas_number", "tipo_desregulador__nome"],
        visualizar=(ADMIN, ESPECIALISTA),
        editar=(ADMIN, ESPECIALISTA),
    ),
    "referencias": entidade(
        "Referências científicas", "Análise técnica",
        Referencia, ReferenciaForm,
        ["titulo_artigo", "autores", "ano_publicacao", "substancia"],
        ["titulo_artigo", "autores", "substancia__nome"],
        visualizar=(ADMIN, ESPECIALISTA),
        editar=(ADMIN, ESPECIALISTA),
    ),
    "sugestoes": entidade(
        "Sugestões de troca", "Análise técnica",
        SugestaoTroca, SugestaoTrocaForm,
        ["produto_risco", "produto_seguro", "confianca", "especialista"],
        [
            "produto_risco__nome",
            "produto_seguro__nome",
            "especialista__nome_completo",
        ],
        visualizar=(ADMIN, ESPECIALISTA, USUARIA),
        editar=(ADMIN, ESPECIALISTA),
        specialist_field="especialista",
    ),
    "perfis-hormonais": entidade(
        "Perfil hormonal", "Minha saúde",
        PerfilHormonal, PerfilHormonalForm,
        [
            "usuario",
            "uso_contraceptivo",
            "condicao_hormonal",
            "ciclo_regular",
            "duracao_ciclo",
            "fluxo_menstrual",
        ],
        ["usuario__nome_completo", "condicao_hormonal"],
        visualizar=(ADMIN, USUARIA),
        editar=(ADMIN, USUARIA),
        owner_lookup="usuario",
        owner_field="usuario",
    ),
    "armario": entidade(
        "Armário virtual", "Minha saúde",
        ArmarioItem, ArmarioItemForm,
        ["produto", "frequencia_uso"],
        ["usuario__nome_completo", "produto__nome"],
        visualizar=(ADMIN, USUARIA),
        editar=(ADMIN, USUARIA),
        owner_lookup="usuario",
        owner_field="usuario",
    ),
    "sintomas": entidade(
        "Sintomas", "Minha saúde",
        Sintoma, SintomaForm,
        ["nome", "descricao"],
        ["nome", "descricao"],
        visualizar=(ADMIN, USUARIA),
    ),
    "registros-sintomas": entidade(
        "Diário de sintomas", "Minha saúde",
        RegistroSintoma, RegistroSintomaForm,
        [
            "sintoma",
            "data_ocorrencia",
            "intensidade",
            "fase_ciclo",
        ],
        ["usuario__nome_completo", "sintoma__nome", "fase_ciclo"],
        visualizar=(ADMIN, USUARIA),
        editar=(ADMIN, USUARIA),
        owner_lookup="usuario",
        owner_field="usuario",
    ),
    "ciclos": entidade(
        "Ciclos menstruais", "Minha saúde",
        CicloMenstrual, CicloMenstrualForm,
        ["data_inicio", "data_fim", "duracao", "observacoes"],
        ["usuario__nome_completo", "observacoes"],
        visualizar=(ADMIN, USUARIA),
        editar=(ADMIN, USUARIA),
        owner_lookup="usuario",
        owner_field="usuario",
    ),
    "exposicoes": entidade(
        "Exposições", "Acompanhamento",
        Exposicao, None,
        [
            "usuario",
            "carga_estrogenica",
            "carga_androgenica",
            "carga_tireoidiana",
            "carga_total",
            "data_calculo",
        ],
        ["usuario__nome_completo"],
        visualizar=(ADMIN, ESPECIALISTA, USUARIA),
        editar=(),
        owner_lookup="usuario",
    ),
    "detalhes-exposicao": entidade(
        "Detalhes da exposição", "Acompanhamento",
        ExposicaoDetalhe, None,
        ["produto", "substancia", "valor_contribuicao"],
        [
            "produto__nome",
            "substancia__nome",
            "exposicao__usuario__nome_completo",
        ],
        visualizar=(ADMIN, ESPECIALISTA, USUARIA),
        editar=(),
        owner_lookup="exposicao__usuario",
    ),
    "alertas": entidade(
        "Alertas de risco", "Acompanhamento",
        AlertaRisco, None,
        ["nivel_gravidade", "mensagem_alerta", "data_emissao"],
        ["usuario__nome_completo", "mensagem_alerta"],
        visualizar=(ADMIN, USUARIA),
        editar=(),
        owner_lookup="usuario",
    ),
    "notificacoes": entidade(
        "Notificações", "Acompanhamento",
        Notificacao, None,
        ["tipo_notificacao", "mensagem", "lida", "data_envio"],
        ["usuario__nome_completo", "tipo_notificacao", "mensagem"],
        visualizar=(ADMIN, USUARIA),
        editar=(),
        owner_lookup="usuario",
    ),
}


def perfil_usuario(user):
    if user.is_superuser or user.tipo_usuario == "ADMIN":
        return ADMIN
    if user.tipo_usuario == "ESPECIALISTA":
        return ESPECIALISTA
    return USUARIA


def get_config(slug):
    try:
        return ENTIDADES[slug]
    except KeyError as exc:
        raise Http404("Página não encontrada.") from exc


def pode_visualizar(config, user):
    return perfil_usuario(user) in config["visualizar"]


def pode_editar(config, user):
    return perfil_usuario(user) in config["editar"]


def verificar_permissao(config, user, escrita=False):
    permitido = (
        pode_editar(config, user)
        if escrita
        else pode_visualizar(config, user)
    )
    if not permitido:
        raise PermissionDenied


def queryset_base(config, request):
    queryset = config["model"].objects.filter(**config["filtro"])
    perfil = perfil_usuario(request.user)

    if perfil == USUARIA and config.get("owner_lookup"):
        queryset = queryset.filter(
            **{config["owner_lookup"]: request.user}
        )

    return queryset


def menu_context(user):
    perfil = perfil_usuario(user)
    secoes = []

    ordem = [
        "Administração",
        "Catálogo",
        "Minha saúde",
        "Análise técnica",
        "Acompanhamento",
    ]

    for secao in ordem:
        itens = []

        for slug, config in ENTIDADES.items():
            if config["secao"] != secao:
                continue
            if perfil not in config["visualizar"]:
                continue

            itens.append({
                "slug": slug,
                "titulo": config["titulo"],
            })

        if itens:
            secoes.append({"titulo": secao, "itens": itens})

    return secoes


def contexto_base(request):
    nao_lidas = 0

    if perfil_usuario(request.user) == USUARIA:
        nao_lidas = request.user.notificacoes.filter(lida=False).count()

    return {
        "menu_secoes": menu_context(request.user),
        "perfil_atual": perfil_usuario(request.user),
        "notificacoes_nao_lidas": nao_lidas,
    }


def colunas_config(config):
    resultado = []

    for nome in config["colunas"]:
        field = config["model"]._meta.get_field(nome)
        resultado.append({
            "nome": nome,
            "rotulo": field.verbose_name,
        })

    return resultado


def campos_detalhe(obj):
    ignorados = {"password"}
    resultado = []

    for field in obj._meta.fields:
        if field.name in ignorados:
            continue

        resultado.append({
            "nome": field.name,
            "rotulo": field.verbose_name,
        })

    return resultado


def preparar_form(form, config, request):
    perfil = perfil_usuario(request.user)

    if perfil == USUARIA and config.get("owner_field"):
        form.fields.pop(config["owner_field"], None)

    if perfil == ESPECIALISTA and config.get("specialist_field"):
        form.fields.pop(config["specialist_field"], None)

    return form


def salvar_form(form, config, request):
    objeto = form.save(commit=False)
    perfil = perfil_usuario(request.user)

    if perfil == USUARIA and config.get("owner_field"):
        setattr(objeto, config["owner_field"], request.user)

    if perfil == ESPECIALISTA and config.get("specialist_field"):
        setattr(objeto, config["specialist_field"], request.user)

    objeto.save()
    form.save_m2m()
    return objeto


def entrar(request):
    if request.user.is_authenticated:
        return redirect("saude:dashboard")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"].lower(),
            password=form.cleaned_data["senha"],
        )

        if user is not None and user.is_active:
            login(request, user)
            return redirect("saude:dashboard")

        messages.error(request, "E-mail ou senha inválidos.")

    return render(request, "entrar.html", {"form": form})


def cadastrar(request):
    if request.user.is_authenticated:
        return redirect("saude:dashboard")

    form = CadastroForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)

        if user.tipo_usuario == "USUARIA":
            PerfilHormonal.objects.get_or_create(usuario=user)

        messages.success(request, "Sua conta foi criada.")
        return redirect("saude:dashboard")

    return render(request, "cadastrar.html", {"form": form})


@login_required(login_url="saude:entrar")
def sair(request):
    logout(request)
    return redirect("saude:entrar")


@login_required(login_url="saude:entrar")
def dashboard(request):
    perfil = perfil_usuario(request.user)
    contexto = contexto_base(request)

    if perfil == USUARIA:
        exposicao = request.user.historico_exposicoes.first()
        metricas = [
            {
                "rotulo": "Produtos no armário",
                "valor": request.user.armario.count(),
                "url": reverse("saude:lista", args=["armario"]),
            },
            {
                "rotulo": "Sintomas registrados",
                "valor": request.user.diario_sintomas.count(),
                "url": reverse(
                    "saude:lista",
                    args=["registros-sintomas"],
                ),
            },
            {
                "rotulo": "Ciclos registrados",
                "valor": request.user.ciclos.count(),
                "url": reverse("saude:lista", args=["ciclos"]),
            },
            {
                "rotulo": "Alertas",
                "valor": request.user.alertas_risco.count(),
                "url": reverse("saude:lista", args=["alertas"]),
            },
        ]
        atividades = request.user.notificacoes.all()[:4]

    elif perfil == ESPECIALISTA:
        exposicao = Exposicao.objects.first()
        metricas = [
            {
                "rotulo": "Substâncias",
                "valor": Substancia.objects.count(),
                "url": reverse("saude:lista", args=["substancias"]),
            },
            {
                "rotulo": "Referências",
                "valor": Referencia.objects.count(),
                "url": reverse("saude:lista", args=["referencias"]),
            },
            {
                "rotulo": "Sugestões",
                "valor": SugestaoTroca.objects.count(),
                "url": reverse("saude:lista", args=["sugestoes"]),
            },
            {
                "rotulo": "Produtos",
                "valor": Produto.objects.count(),
                "url": reverse("saude:lista", args=["produtos"]),
            },
        ]
        atividades = SugestaoTroca.objects.select_related(
            "produto_risco",
            "produto_seguro",
        )[:4]

    else:
        exposicao = Exposicao.objects.first()
        metricas = [
            {
                "rotulo": "Usuárias",
                "valor": Pessoa.objects.filter(
                    tipo_usuario="USUARIA"
                ).count(),
                "url": reverse("saude:lista", args=["usuarias"]),
            },
            {
                "rotulo": "Especialistas",
                "valor": Pessoa.objects.filter(
                    tipo_usuario="ESPECIALISTA"
                ).count(),
                "url": reverse(
                    "saude:lista",
                    args=["especialistas"],
                ),
            },
            {
                "rotulo": "Produtos",
                "valor": Produto.objects.count(),
                "url": reverse("saude:lista", args=["produtos"]),
            },
            {
                "rotulo": "Alertas",
                "valor": AlertaRisco.objects.count(),
                "url": reverse("saude:lista", args=["alertas"]),
            },
        ]
        atividades = AlertaRisco.objects.select_related("usuario")[:4]

    contexto.update({
        "exposicao": exposicao,
        "metricas": metricas,
        "atividades": atividades,
        "radar_valores": [
            float(exposicao.carga_estrogenica or 0) if exposicao else 0,
            float(exposicao.carga_androgenica or 0) if exposicao else 0,
            float(exposicao.carga_tireoidiana or 0) if exposicao else 0,
        ],
    })

    return render(request, "dashboard.html", contexto)


@login_required(login_url="saude:entrar")
def lista(request, slug):
    config = get_config(slug)
    verificar_permissao(config, request.user)

    queryset = queryset_base(config, request)
    termo = request.GET.get("q", "").strip()

    if termo:
        filtro = Q()
        for campo in config["busca"]:
            filtro |= Q(**{f"{campo}__icontains": termo})
        queryset = queryset.filter(filtro)

    contexto = contexto_base(request)
    contexto.update({
        "config": config,
        "slug": slug,
        "objetos": queryset,
        "colunas": colunas_config(config),
        "termo": termo,
        "pode_editar": pode_editar(config, request.user),
    })

    return render(request, "lista.html", contexto)


@login_required(login_url="saude:entrar")
def detalhe(request, slug, pk):
    config = get_config(slug)
    verificar_permissao(config, request.user)

    objeto = get_object_or_404(
        queryset_base(config, request),
        pk=pk,
    )

    contexto = contexto_base(request)
    contexto.update({
        "config": config,
        "slug": slug,
        "objeto": objeto,
        "campos": campos_detalhe(objeto),
        "pode_editar": pode_editar(config, request.user),
    })

    return render(request, "detalhe.html", contexto)


@login_required(login_url="saude:entrar")
def criar(request, slug):
    config = get_config(slug)
    verificar_permissao(config, request.user, escrita=True)

    if config["form"] is None:
        raise PermissionDenied

    if (
        slug == "perfis-hormonais"
        and perfil_usuario(request.user) == USUARIA
    ):
        perfil = PerfilHormonal.objects.filter(
            usuario=request.user
        ).first()

        if perfil:
            return redirect(
                "saude:editar",
                slug=slug,
                pk=perfil.pk,
            )

    form = config["form"](
        request.POST or None,
        request.FILES or None,
    )
    preparar_form(form, config, request)

    if request.method == "POST" and form.is_valid():
        salvar_form(form, config, request)
        messages.success(request, "Registro salvo com sucesso.")
        return redirect("saude:lista", slug=slug)

    contexto = contexto_base(request)
    contexto.update({
        "config": config,
        "slug": slug,
        "form": form,
        "titulo_form": "Novo registro",
    })

    return render(request, "formulario.html", contexto)


@login_required(login_url="saude:entrar")
def editar(request, slug, pk):
    config = get_config(slug)
    verificar_permissao(config, request.user, escrita=True)

    if config["form"] is None:
        raise PermissionDenied

    objeto = get_object_or_404(
        queryset_base(config, request),
        pk=pk,
    )

    form = config["form"](
        request.POST or None,
        request.FILES or None,
        instance=objeto,
    )
    preparar_form(form, config, request)

    if request.method == "POST" and form.is_valid():
        salvar_form(form, config, request)
        messages.success(request, "Alterações salvas.")
        return redirect("saude:lista", slug=slug)

    contexto = contexto_base(request)
    contexto.update({
        "config": config,
        "slug": slug,
        "form": form,
        "titulo_form": "Editar registro",
    })

    return render(request, "formulario.html", contexto)


@login_required(login_url="saude:entrar")
def excluir(request, slug, pk):
    config = get_config(slug)
    verificar_permissao(config, request.user, escrita=True)

    objeto = get_object_or_404(
        queryset_base(config, request),
        pk=pk,
    )

    if request.method == "POST":
        objeto.delete()
        messages.success(request, "Registro excluído.")
        return redirect("saude:lista", slug=slug)

    contexto = contexto_base(request)
    contexto.update({
        "config": config,
        "slug": slug,
        "objeto": objeto,
    })

    return render(request, "confirmar_exclusao.html", contexto)


@require_POST
@login_required(login_url="saude:entrar")
def marcar_notificacao(request, pk):
    perfil = perfil_usuario(request.user)

    if perfil == ADMIN:
        notificacao = get_object_or_404(Notificacao, pk=pk)
    elif perfil == USUARIA:
        notificacao = get_object_or_404(
            Notificacao,
            pk=pk,
            usuario=request.user,
        )
    else:
        raise PermissionDenied

    notificacao.lida = True
    notificacao.save(update_fields=["lida"])
    return redirect("saude:lista", slug="notificacoes")