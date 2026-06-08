from django import forms

from produtos.models import ComentarioProduto, SugestaoTroca
from usuarios.models import Pessoa
from .models import ArmarioItem


class ComentarioProdutoForm(forms.ModelForm):
    class Meta:
        model = ComentarioProduto
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": (
                    "Compartilhe uma observação técnica sobre este produto..."
                ),
            }),
        }


class ArmarioRapidoForm(forms.ModelForm):
    class Meta:
        model = ArmarioItem
        fields = ["produto", "frequencia_uso"]


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
                "placeholder": "Explique tecnicamente por que a troca é indicada.",
            }),
            "confianca": forms.NumberInput(attrs={
                "min": "0",
                "max": "1",
                "step": "0.01",
            }),
        }

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("produto_risco") == cleaned.get("produto_seguro"):
            self.add_error(
                "produto_seguro",
                "O produto seguro deve ser diferente do produto de risco.",
            )

        return cleaned


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = [
            "nome_completo",
            "apelido",
            "foto_perfil",
            "data_nasc",
            "cidade",
        ]
        widgets = {
            "data_nasc": forms.DateInput(attrs={"type": "date"}),
        }


class PerfilEspecialistaForm(forms.ModelForm):
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
                "placeholder": "Conte sobre sua atuação profissional.",
            }),
        }