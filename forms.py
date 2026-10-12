import re

from django import forms
from django.db.models import Q

from .models import Aluguel, Carro, Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "cpf", "cnh", "telefone", "email"]
        widgets = {
            "cpf": forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
            "telefone": forms.TextInput(attrs={"placeholder": "(98) 99999-9999"}),
        }

    def clean_cpf(self):
        digitos = re.sub(r"\D", "", self.cleaned_data["cpf"])
        if len(digitos) != 11:
            raise forms.ValidationError("O CPF deve ter 11 números.")
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


class CarroForm(forms.ModelForm):
    class Meta:
        model = Carro
        fields = ["marca", "modelo", "ano", "cor", "placa", "cambio", "lugares", "valor_diaria", "status"]
        widgets = {
            "placa": forms.TextInput(attrs={"placeholder": "ABC1D23"}),
            "valor_diaria": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def clean_placa(self):
        placa = re.sub(r"[^A-Za-z0-9]", "", self.cleaned_data["placa"]).upper()
        if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", placa):
            raise forms.ValidationError("Placa inválida. Use o formato ABC1D23 ou ABC1234.")
        return placa


class AluguelForm(forms.ModelForm):
    class Meta:
        model = Aluguel
        fields = ["cliente", "carro", "data_retirada", "data_devolucao_prevista"]
        widgets = {
            "data_retirada": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "data_devolucao_prevista": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só aparecem carros livres (mais o carro atual, ao editar um aluguel).
        filtro = Q(status=Carro.Status.DISPONIVEL)
        if self.instance.pk:
            filtro |= Q(pk=self.instance.carro_id)
        self.fields["carro"].queryset = Carro.objects.filter(filtro)
        self.fields["carro"].empty_label = "Escolha um carro disponível"
        self.fields["cliente"].empty_label = "Escolha um cliente"

    def clean(self):
        dados = super().clean()
        retirada = dados.get("data_retirada")
        devolucao = dados.get("data_devolucao_prevista")
        if retirada and devolucao and devolucao < retirada:
            self.add_error("data_devolucao_prevista", "A devolução não pode ser antes da retirada.")
        return dados
