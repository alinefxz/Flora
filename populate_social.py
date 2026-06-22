from django.utils import timezone
from usuarios.models import Especialista, Usuario, Cidade, UF
from produtos.models import Produto, Categoria, SugestaoTroca, ComentarioProduto, CurtidaComentario

# 1. Obter ou Criar Localização para os Perfis
uf, _ = UF.objects.get_or_create(sigla="SP", defaults={"nome_estado": "São Paulo"})
cidade, _ = Cidade.objects.get_or_create(nome_cidade="São Paulo", uf=uf)

# 2. Criar Usuários (Se baseando na herança de Pessoa)
# Nota: preenchemos os campos específicos de especialista conforme seu modelo Pessoa
especialista_dra, _ = Especialista.objects.get_or_create(
    email="fernanda.endocri@flora.com.br",
    defaults={
        "username": "dra_fernanda",
        "nome_completo": "Dra. Fernanda Silva",
        "cpf": "123.456.789-00",
        "tipo_usuario": "ESPECIALISTA",
        "cidade": city,
        "especialidade": "Endocrinologista Hormonal",
        "registro_profissional": "CRM/SP 123456",
        "biografia": "Médica focada em saúde endócrina e impactos de desreguladores no ciclo menstrual.",
        "ativo": True
    }
)

usuario_comum, _ = Usuario.objects.get_or_create(
    email="mariana.silva@email.com",
    defaults={
        "username": "mari_silva",
        "nome_completo": "Mariana Silva",
        "cpf": "987.654.321-11",
        "tipo_usuario": "USUARIA",
        "cidade": city,
        "ativo": True
    }
)

# 3. Obter ou Criar Produtos para a Troca
categoria_cosmeticos, _ = Categoria.objects.get_or_create(nome="Cosméticos", defaults={"descricao": "Produtos de cuidados pessoais"})

produto_risco, _ = Produto.objects.get_or_create(
    codigo_barras="7891234567890",
    defaults={
        "nome": "Creme Hidratante Convencional X",
        "marca": "Marca Antiga",
        "categoria": categoria_cosmeticos,
        "descricao": "Creme hidratante corporal com fragrância intensa.",
        "fabricante": "Cosméticos Antigos S.A.",
        "nota_flora": 1.5  # Nota baixa devido a potenciais desreguladores
    }
)

produto_seguro, _ = Produto.objects.get_or_create(
    codigo_barras="7899876543210",
    defaults={
        "nome": "Loção Hidratante Flora Clean",
        "marca": "Pureza Natural",
        "categoria": categoria_cosmeticos,
        "descricao": "Loção corporal livre de parabenos, ftalatos e fragrâncias sintéticas.",
        "fabricante": "Laboratório Flora Orgânica",
        "nota_flora": 4.8  # Nota alta e segura
    }
)

# 4. Criar Sugestão de Troca (Vinculando os dois produtos e o especialista)
sugestao, criado_sugestao = SugestaoTroca.objects.get_or_create(
    produto_risco=produto_risco,
    produto_seguro=produto_seguro,
    defaults={
        "justificativa_tecnica": (
            "O creme convencional contém altos níveis de parabenos (conservantes) associados à mimetização estrogênica. "
            "A alternativa da Pureza Natural utiliza conservantes botânicos seguros, eliminando a carga tireoidiana."
        ),
        "origem_sugestao": "Análise Clínica Flora",
        "confianca": 0.95,
        "especialista": especialista_dra
    }
)

# 5. Criar Comentários Técnicos no Produto
comentario, criado_comentario = ComentarioProduto.objects.get_or_create(
    produto=produto_risco,
    autor=especialista_dra,
    defaults={
        "texto": (
            "Atenção pacientes com histórico de SOP ou Endometriose: evitem este lote e similares devido à presença "
            "de compostos fenólicos que elevam drasticamente o peso de sensibilidade hormonal no prontuário."
        ),
        "ativo": True
    }
)

# 6. Adicionar uma Curtida no Comentário (Mariana achou o comentário útil)
if criado_comentario:
    CurtidaComentario.objects.get_or_create(
        comentario=comentario,
        usuario=usuario_comum
    )

print("Seed social processado com sucesso!")