from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from produtos.models import (
    Categoria,
    ComentarioProduto,
    CurtidaComentario,
    Produto,
    SugestaoTroca,
)
from usuarios.models import Pessoa

from .frontend import (
    ADMIN,
    ESPECIALISTA,
    USUARIA,
    contexto_base,
    perfil_usuario,
)
from .models import ArmarioItem
from .social_forms import (
    ArmarioRapidoForm,
    ComentarioProdutoForm,
    PerfilEspecialistaForm,
    PerfilUsuarioForm,
    SugestaoEspecialistaForm,
)


def somente_usuaria(request):
    if perfil_usuario(request.user) != USUARIA:
        raise PermissionDenied


def somente_especialista(request):
    if perfil_usuario(request.user) not in {ADMIN, ESPECIALISTA}:
        raise PermissionDenied


@login_required(login_url="saude:entrar")
def catalogo(request):
    termo = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    produtos = Produto.objects.select_related("categoria").annotate(
        total_comentarios=Count(
            "comentarios",
            filter=Q(comentarios__ativo=True),
            distinct=True,
        )
    )

    if termo:
        produtos = produtos.filter(
            Q(nome__icontains=termo)
            | Q(marca__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(fabricante__icontains=termo)
        )

    if categoria:
        produtos = produtos.filter(categoria_id=categoria)

    contexto = contexto_base(request)
    contexto.update({
        "produtos": produtos,
        "categorias": Categoria.objects.all(),
        "termo": termo,
        "categoria_atual": categoria,
    })

    return render(request, "catalogo.html", contexto)


@login_required(login_url="saude:entrar")
def produto_social(request, pk):
    produto = get_object_or_404(
        Produto.objects.select_related("categoria"),
        pk=pk,
    )

    comentarios = produto.comentarios.filter(
        ativo=True
    ).select_related("autor").prefetch_related("curtidas")

    curtidos = set(
        CurtidaComentario.objects.filter(
            usuario=request.user,
            comentario__produto=produto,
        ).values_list("comentario_id", flat=True)
    )

    sugestoes = produto.sugestoes_de_substituicao.select_related(
        "produto_seguro",
        "especialista",
    )

    contexto = contexto_base(request)
    contexto.update({
        "produto": produto,
        "comentarios": comentarios,
        "comentarios_curtidos": curtidos,
        "sugestoes": sugestoes,
        "comentario_form": ComentarioProdutoForm(),
        "pode_comentar": perfil_usuario(request.user)
        in {ADMIN, ESPECIALISTA},
        "esta_no_armario": (
            perfil_usuario(request.user) == USUARIA
            and request.user.armario.filter(produto=produto).exists()
        ),
    })

    return render(request, "produto_social.html", contexto)


@require_POST
@login_required(login_url="saude:entrar")
def comentar_produto(request, pk):
    somente_especialista(request)
    produto = get_object_or_404(Produto, pk=pk)
    form = ComentarioProdutoForm(request.POST)

    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.produto = produto
        comentario.autor = request.user
        comentario.save()
        messages.success(request, "Comentário publicado.")

    else:
        messages.error(request, "Não foi possível publicar o comentário.")

    return redirect("saude:produto_social", pk=produto.pk)


@require_POST
@login_required(login_url="saude:entrar")
def curtir_comentario(request, pk):
    comentario = get_object_or_404(
        ComentarioProduto,
        pk=pk,
        ativo=True,
    )

    curtida, criada = CurtidaComentario.objects.get_or_create(
        comentario=comentario,
        usuario=request.user,
    )

    if not criada:
        curtida.delete()

    total = comentario.curtidas.count()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "curtido": criada,
            "total": total,
        })

    return redirect(
        "saude:produto_social",
        pk=comentario.produto_id,
    )


@login_required(login_url="saude:entrar")
def armario(request):
    somente_usuaria(request)

    itens = request.user.armario.select_related(
        "produto",
        "produto__categoria",
    )

    contexto = contexto_base(request)
    contexto.update({
        "itens_armario": itens,
        "armario_form": ArmarioRapidoForm(),
    })

    return render(request, "armario.html", contexto)


@require_POST
@login_required(login_url="saude:entrar")
def adicionar_armario(request):
    somente_usuaria(request)
    form = ArmarioRapidoForm(request.POST)

    if form.is_valid():
        produto = form.cleaned_data["produto"]
        frequencia = form.cleaned_data["frequencia_uso"]

        item, criado = ArmarioItem.objects.update_or_create(
            usuario=request.user,
            produto=produto,
            defaults={"frequencia_uso": frequencia},
        )

        if criado:
            messages.success(request, "Produto colocado no seu armário.")
        else:
            messages.success(request, "Frequência de uso atualizada.")
    else:
        messages.error(request, "Confira os dados do produto.")

    return redirect("saude:armario")


@require_POST
@login_required(login_url="saude:entrar")
def atualizar_armario(request, pk):
    somente_usuaria(request)

    item = get_object_or_404(
        ArmarioItem,
        pk=pk,
        usuario=request.user,
    )

    try:
        frequencia = float(request.POST.get("frequencia_uso"))
    except (TypeError, ValueError):
        messages.error(request, "Frequência inválida.")
        return redirect("saude:armario")

    frequencias = {3.0, 1.0, 0.5}

    if frequencia not in frequencias:
        messages.error(request, "Frequência inválida.")
        return redirect("saude:armario")

    item.frequencia_uso = frequencia
    item.save(update_fields=["frequencia_uso"])

    messages.success(request, "Frequência atualizada.")
    return redirect("saude:armario")


@require_POST
@login_required(login_url="saude:entrar")
def remover_armario(request, pk):
    somente_usuaria(request)

    item = get_object_or_404(
        ArmarioItem,
        pk=pk,
        usuario=request.user,
    )
    item.delete()

    messages.success(request, "Produto retirado do seu armário.")
    return redirect("saude:armario")


@login_required(login_url="saude:entrar")
def perfil(request):
    tipo = perfil_usuario(request.user)

    if tipo == ESPECIALISTA:
        form_class = PerfilEspecialistaForm
    else:
        form_class = PerfilUsuarioForm

    form = form_class(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil atualizado.")
        return redirect("saude:perfil")

    contexto = contexto_base(request)
    contexto.update({
        "perfil": request.user,
        "perfil_form": form,
        "perfil_proprio": True,
        "sugestoes_perfil": SugestaoTroca.objects.filter(
            especialista=request.user
        ).select_related(
            "produto_risco",
            "produto_seguro",
        ) if tipo == ESPECIALISTA else None,
        "comentarios_perfil": request.user.comentarios_produtos.filter(
            ativo=True
        ).select_related("produto") if tipo == ESPECIALISTA else None,
    })

    return render(request, "perfil.html", contexto)


@login_required(login_url="saude:entrar")
def perfil_especialista(request, pk):
    especialista = get_object_or_404(
        Pessoa,
        pk=pk,
        tipo_usuario=ESPECIALISTA,
        ativo=True,
    )

    contexto = contexto_base(request)
    contexto.update({
        "perfil": especialista,
        "perfil_proprio": especialista.pk == request.user.pk,
        "sugestoes_perfil": SugestaoTroca.objects.filter(
            especialista=especialista
        ).select_related("produto_risco", "produto_seguro"),
        "comentarios_perfil": especialista.comentarios_produtos.filter(
            ativo=True
        ).select_related("produto"),
    })

    return render(request, "perfil.html", contexto)


@login_required(login_url="saude:entrar")
def especialistas(request):
    termo = request.GET.get("q", "").strip()

    pessoas = Pessoa.objects.filter(
        tipo_usuario=ESPECIALISTA,
        ativo=True,
    )

    if termo:
        pessoas = pessoas.filter(
            Q(nome_completo__icontains=termo)
            | Q(especialidade__icontains=termo)
            | Q(registro_profissional__icontains=termo)
        )

    contexto = contexto_base(request)
    contexto.update({
        "especialistas": pessoas,
        "termo": termo,
    })

    return render(request, "especialistas.html", contexto)


@login_required(login_url="saude:entrar")
def sugestoes(request):
    objetos = SugestaoTroca.objects.select_related(
        "produto_risco",
        "produto_seguro",
        "especialista",
    ).order_by("-pk")

    contexto = contexto_base(request)
    contexto.update({
        "sugestoes": objetos,
        "pode_sugerir": perfil_usuario(request.user)
        in {ADMIN, ESPECIALISTA},
    })

    return render(request, "sugestoes.html", contexto)


@login_required(login_url="saude:entrar")
def sugestao_nova(request):
    somente_especialista(request)

    form = SugestaoEspecialistaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        sugestao = form.save(commit=False)

        if perfil_usuario(request.user) == ESPECIALISTA:
            sugestao.especialista = request.user

        sugestao.save()
        messages.success(request, "Sugestão publicada.")
        return redirect("saude:sugestoes")

    contexto = contexto_base(request)
    contexto.update({
        "form": form,
        "titulo_form": "Nova sugestão de troca",
    })

    return render(request, "formulario_social.html", contexto)


@login_required(login_url="saude:entrar")
def sugestao_editar(request, pk):
    somente_especialista(request)

    sugestao = get_object_or_404(SugestaoTroca, pk=pk)

    if (
        perfil_usuario(request.user) == ESPECIALISTA
        and sugestao.especialista_id != request.user.pk
    ):
        raise PermissionDenied

    form = SugestaoEspecialistaForm(
        request.POST or None,
        instance=sugestao,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sugestão atualizada.")
        return redirect("saude:sugestoes")

    contexto = contexto_base(request)
    contexto.update({
        "form": form,
        "titulo_form": "Editar sugestão",
    })

    return render(request, "formulario_social.html", contexto)