from django.test import TestCase
from django.urls import reverse

from produtos.models import Categoria, Produto, SugestaoTroca
from usuarios.models import Pessoa


class SocialExperienceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuaria = Pessoa.objects.create_user(
            username="usuaria",
            email="usuaria@flora.test",
            password="senha-forte-123",
            nome_completo="Ana Flora",
            cpf="111.111.111-11",
            tipo_usuario="USUARIA",
        )
        cls.especialista = Pessoa.objects.create_user(
            username="especialista",
            email="especialista@flora.test",
            password="senha-forte-123",
            nome_completo="Dra. Lia Verde",
            cpf="222.222.222-22",
            tipo_usuario="ESPECIALISTA",
            especialidade="Endocrinologia",
            registro_profissional="CRM/SP 123456",
            biografia="Atuação em saúde hormonal e prevenção.",
        )
        cls.admin = Pessoa.objects.create_user(
            username="admin",
            email="admin@flora.test",
            password="senha-forte-123",
            nome_completo="Admin Flora",
            cpf="333.333.333-33",
            tipo_usuario="ADMIN",
        )
        categoria = Categoria.objects.create(nome="Cuidados pessoais")
        cls.produto_risco = Produto.objects.create(
            nome="Produto A",
            marca="Marca A",
            codigo_barras="11111111111111",
            categoria=categoria,
        )
        cls.produto_seguro = Produto.objects.create(
            nome="Produto B",
            marca="Marca B",
            codigo_barras="22222222222222",
            categoria=categoria,
        )
        cls.sugestao = SugestaoTroca.objects.create(
            produto_risco=cls.produto_risco,
            produto_seguro=cls.produto_seguro,
            justificativa_tecnica="Alternativa com menor carga de risco.",
            especialista=cls.especialista,
        )

    def test_login_exibe_logo_e_chamada_de_cadastro(self):
        response = self.client.get(reverse("saude:entrar"))

        self.assertContains(response, "img/logoNome.png")
        self.assertContains(response, "Quero me cadastrar")
        self.assertContains(response, "auth-mode-login")

    def test_cadastro_exibe_retorno_para_login(self):
        response = self.client.get(reverse("saude:cadastrar"))

        self.assertContains(response, "Já tenho uma conta")
        self.assertContains(response, "auth-mode-register")

    def test_todos_os_perfis_acessam_o_proprio_perfil(self):
        for pessoa in (self.usuaria, self.especialista, self.admin):
            with self.subTest(tipo=pessoa.tipo_usuario):
                self.client.force_login(pessoa)
                response = self.client.get(reverse("saude:perfil"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, pessoa.nome_completo)
                self.assertContains(response, "Salvar alterações")

    def test_sugestao_mostra_dados_principais_da_especialista(self):
        self.client.force_login(self.usuaria)
        response = self.client.get(reverse("saude:sugestoes"))

        self.assertContains(response, self.especialista.nome_completo)
        self.assertContains(response, self.especialista.especialidade)
        self.assertContains(response, self.especialista.registro_profissional)
        self.assertContains(response, self.produto_seguro.nome)

    def test_especialista_e_autora_da_nova_sugestao(self):
        self.client.force_login(self.especialista)
        response = self.client.post(
            reverse("saude:sugestao_nova"),
            {
                "produto_risco": self.produto_seguro.pk,
                "produto_seguro": self.produto_risco.pk,
                "justificativa_tecnica": "Nova justificativa técnica.",
                "origem_sugestao": "Análise profissional",
                "confianca": "0.90",
            },
        )

        self.assertRedirects(response, reverse("saude:sugestoes"))
        nova = SugestaoTroca.objects.exclude(pk=self.sugestao.pk).get()
        self.assertEqual(nova.especialista, self.especialista)

    def test_dashboard_da_especialista_nao_exibe_radar_pessoal(self):
        self.client.force_login(self.especialista)
        response = self.client.get(reverse("saude:dashboard"))

        self.assertContains(response, "Área profissional")
        self.assertNotContains(response, 'id="radarChart"')
