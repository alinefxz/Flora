from django import forms

from produtos.models import (
    ComentarioProduto,
    Produto,
    SugestaoTroca,
)
from usuarios.models import Cidade, Pessoa

from .models import ArmarioItem


DATE_INPUT_FORMATS = ["%Y-%m-%d", "%d/%m/%Y"]


def configurar_campo_cidade(campo):
    campo.queryset = Cidade.objects.select_related("uf").all()
    campo.empty_label = "Selecione ou pesquise sua cidade"

    campo.widget.attrs.update({
        "data-smart-select": "",
        "data-create-kind": "city",
        "data-search-placeholder": "Digite o nome da cidade",
    })


def configurar_campo_data(campo):
    campo.input_formats = DATE_INPUT_FORMATS
    campo.widget = forms.DateInput(
        format="%Y-%m-%d",
        attrs={"type": "date"},
    )


class ComentarioProdutoForm(forms.ModelForm):
    class Meta:
        model = ComentarioProduto
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": (
                    "Compartilhe uma observação técnica "
                    "sobre este produto..."
                ),
            }),
        }


class ArmarioRapidoForm(forms.ModelForm):
    class Meta:
        model = ArmarioItem
        fields = ["produto", "frequencia_uso"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        produto = self.fields["produto"]
        produto.queryset = Produto.objects.select_related(
            "categoria"
        )
        produto.empty_label = "Pesquise um produto"
        produto.widget.attrs.update({
            "data-smart-select": "",
            "data-create-kind": "product",
            "data-search-placeholder": "Nome ou marca do produto",
        })

        self.fields["frequencia_uso"].widget.attrs.update({
            "data-smart-select": "",
        })


class SugestaoEspecialistaForm(forms.ModelForm):
    class Meta:
        model = SugestaoTroca
        fields = [
            "produto_risco",
            "produto_seguro",
            "justificativa_tecnica",
            "origem_sugestao",
            "confianca",
        ]
        widgets = {
            "justificativa_tecnica": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": (
                    "Explique tecnicamente por que "
                    "a troca é indicada."
                ),
            }),
            "confianca": forms.NumberInput(attrs={
                "min": "0",
                "max": "1",
                "step": "0.01",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for nome in ("produto_risco", "produto_seguro"):
            self.fields[nome].widget.attrs.update({
                "data-smart-select": "",
                "data-search-placeholder": (
                    "Pesquise pelo nome ou marca"
                ),
            })

    def clean(self):
        cleaned = super().clean()

        if (
            cleaned.get("produto_risco")
            == cleaned.get("produto_seguro")
        ):
            self.add_error(
                "produto_seguro",
                (
                    "O produto seguro deve ser diferente "
                    "do produto de risco."
                ),
            )

        return cleaned


class BasePerfilForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        configurar_campo_cidade(self.fields["cidade"])

        if "data_nasc" in self.fields:
            configurar_campo_data(self.fields["data_nasc"])

        self.fields["foto_perfil"].widget = forms.FileInput(
            attrs={
                "accept": "image/png,image/jpeg,image/webp",
                "data-image-input": "profile",
            }
        )

        self.fields["foto_perfil"].help_text = (
            "A nova foto substitui a atual. "
            "Se não escolher outra, a foto salva será mantida."
        )


class PerfilUsuarioForm(BasePerfilForm):
    class Meta:
        model = Pessoa
        fields = [
            "nome_completo",
            "apelido",
            "foto_perfil",
            "data_nasc",
            "cidade",
        ]


class PerfilEspecialistaForm(BasePerfilForm):
    class Meta:
        model = Pessoa
        fields = [
            "nome_completo",
            "foto_perfil",
            "cidade",
            "registro_profissional",
            "especialidade",
            "biografia",
        ]
        widgets = {
            "biografia": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": (
                    "Conte sobre sua atuação profissional."
                ),
            }),
        }


class PerfilAdminForm(BasePerfilForm):
    class Meta:
        model = Pessoa
        fields = [
            "nome_completo",
            "foto_perfil",
            "cidade",
            "nivel_acesso",
        ]