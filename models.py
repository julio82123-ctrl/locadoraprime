from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    nome = models.CharField("Nome completo", max_length=100)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    cnh = models.CharField("CNH", max_length=20)
    telefone = models.CharField("Telefone", max_length=20)
    email = models.EmailField("E-mail", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Carro(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        ALUGADO = "alugado", "Alugado"
        MANUTENCAO = "manutencao", "Em manutenção"

    class Cambio(models.TextChoices):
        MANUAL = "manual", "Manual"
        AUTOMATICO = "automatico", "Automático"

    marca = models.CharField("Marca", max_length=40)
    modelo = models.CharField("Modelo", max_length=60)
    ano = models.PositiveSmallIntegerField(
        "Ano",
        validators=[MinValueValidator(1990), MaxValueValidator(date.today().year + 1)],
    )
    cor = models.CharField("Cor", max_length=30)
    placa = models.CharField("Placa", max_length=8, unique=True)
    cambio = models.CharField("Câmbio", max_length=12, choices=Cambio.choices, default=Cambio.MANUAL)
    lugares = models.PositiveSmallIntegerField("Lugares", default=5)
    valor_diaria = models.DecimalField("Valor da diária (R$)", max_digits=8, decimal_places=2)
    status = models.CharField("Situação", max_length=12, choices=Status.choices, default=Status.DISPONIVEL)

    class Meta:
        ordering = ["marca", "modelo"]

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"


class Aluguel(models.Model):
    class Status(models.TextChoices):
        ATIVO = "ativo", "Em andamento"
        FINALIZADO = "finalizado", "Finalizado"

    # Duas chaves estrangeiras: cada aluguel liga um cliente a um carro.
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="alugueis")
    carro = models.ForeignKey(Carro, on_delete=models.PROTECT, related_name="alugueis")
    data_retirada = models.DateField("Retirada", default=timezone.localdate)
    data_devolucao_prevista = models.DateField("Devolução prevista")
    data_devolucao_real = models.DateField("Devolvido em", null=True, blank=True)
    valor_total = models.DecimalField("Valor total (R$)", max_digits=10, decimal_places=2, default=0, editable=False)
    status = models.CharField("Situação", max_length=12, choices=Status.choices, default=Status.ATIVO)

    class Meta:
        ordering = ["-data_retirada", "-id"]
        verbose_name_plural = "aluguéis"

    def __str__(self):
        return f"Aluguel #{self.pk} - {self.cliente} / {self.carro}"

    @property
    def dias(self):
        """Dias cobrados: usa a devolução real se já houve, senão a prevista (mínimo 1 diária)."""
        fim = self.data_devolucao_real or self.data_devolucao_prevista
        return max(1, (fim - self.data_retirada).days)

    @property
    def atrasado(self):
        return self.status == self.Status.ATIVO and timezone.localdate() > self.data_devolucao_prevista

    def calcular_total(self):
        return self.dias * self.carro.valor_diaria

    def save(self, *args, **kwargs):
        self.valor_total = self.calcular_total()
        super().save(*args, **kwargs)
