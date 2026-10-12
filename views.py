from django.contrib import messages
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AluguelForm, CarroForm, ClienteForm
from .models import Aluguel, Carro, Cliente


# ---------------------------------------------------------------- auxiliares
def atualizar_status_carro(carro):
    """Mantém a situação do carro coerente com seus aluguéis em andamento."""
    if carro.status == Carro.Status.MANUTENCAO:
        return
    em_uso = carro.alugueis.filter(status=Aluguel.Status.ATIVO).exists()
    novo = Carro.Status.ALUGADO if em_uso else Carro.Status.DISPONIVEL
    if carro.status != novo:
        carro.status = novo
        carro.save(update_fields=["status"])


# --------------------------------------------------------------------- início
def home(request):
    contexto = {
        "livres": Carro.objects.filter(status=Carro.Status.DISPONIVEL),
        "qtd_alugados": Carro.objects.filter(status=Carro.Status.ALUGADO).count(),
        "qtd_manutencao": Carro.objects.filter(status=Carro.Status.MANUTENCAO).count(),
        "em_andamento": Aluguel.objects.filter(status=Aluguel.Status.ATIVO)
        .select_related("cliente", "carro")
        .order_by("data_devolucao_prevista"),
    }
    return render(request, "locadora/home.html", contexto)


# ----------------------------------------------------------------- carros
def carro_lista(request):
    busca = request.GET.get("q", "").strip()
    situacao = request.GET.get("status", "")
    carros = Carro.objects.all()
    if busca:
        carros = carros.filter(
            Q(marca__icontains=busca) | Q(modelo__icontains=busca) | Q(placa__icontains=busca)
        )
    if situacao:
        carros = carros.filter(status=situacao)
    contexto = {
        "carros": carros,
        "busca": busca,
        "situacao": situacao,
        "opcoes_status": Carro.Status.choices,
    }
    return render(request, "locadora/carro_lista.html", contexto)


def carro_detalhe(request, pk):
    carro = get_object_or_404(Carro, pk=pk)
    historico = carro.alugueis.select_related("cliente")
    return render(request, "locadora/carro_detalhe.html", {"carro": carro, "historico": historico})


def carro_novo(request):
    form = CarroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        carro = form.save()
        messages.success(request, f"{carro.marca} {carro.modelo} foi cadastrado.")
        return redirect("locadora:carro_detalhe", pk=carro.pk)
    contexto = {
        "titulo": "Cadastrar carro",
        "form": form,
        "botao": "Cadastrar carro",
        "voltar": "locadora:carro_lista",
    }
    return render(request, "locadora/form.html", contexto)


def carro_editar(request, pk):
    carro = get_object_or_404(Carro, pk=pk)
    form = CarroForm(request.POST or None, instance=carro)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "As alterações no carro foram salvas.")
        return redirect("locadora:carro_detalhe", pk=carro.pk)
    contexto = {
        "titulo": f"Editar {carro.marca} {carro.modelo}",
        "form": form,
        "botao": "Salvar alterações",
        "voltar": "locadora:carro_lista",
    }
    return render(request, "locadora/form.html", contexto)


def carro_excluir(request, pk):
    carro = get_object_or_404(Carro, pk=pk)
    if request.method == "POST":
        try:
            carro.delete()
        except ProtectedError:
            messages.error(
                request,
                "Este carro tem aluguéis registrados e não pode ser excluído. "
                "Para tirá-lo de circulação, mude a situação para \"Em manutenção\".",
            )
            return redirect("locadora:carro_detalhe", pk=pk)
        messages.success(request, "O carro foi excluído.")
        return redirect("locadora:carro_lista")
    contexto = {
        "titulo": "Excluir carro",
        "objeto": f"{carro.marca} {carro.modelo} ({carro.placa})",
        "botao": "Excluir carro",
        "voltar": "locadora:carro_detalhe",
        "voltar_pk": carro.pk,
    }
    return render(request, "locadora/confirmar_exclusao.html", contexto)


# --------------------------------------------------------------- clientes
def cliente_lista(request):
    busca = request.GET.get("q", "").strip()
    clientes = Cliente.objects.all()
    if busca:
        clientes = clientes.filter(Q(nome__icontains=busca) | Q(cpf__icontains=busca))
    return render(request, "locadora/cliente_lista.html", {"clientes": clientes, "busca": busca})


def cliente_detalhe(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    historico = cliente.alugueis.select_related("carro")
    return render(request, "locadora/cliente_detalhe.html", {"cliente": cliente, "historico": historico})


def cliente_novo(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cliente = form.save()
        messages.success(request, f"{cliente.nome} foi cadastrado.")
        return redirect("locadora:cliente_detalhe", pk=cliente.pk)
    contexto = {
        "titulo": "Cadastrar cliente",
        "form": form,
        "botao": "Cadastrar cliente",
        "voltar": "locadora:cliente_lista",
    }
    return render(request, "locadora/form.html", contexto)


def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Os dados do cliente foram atualizados.")
        return redirect("locadora:cliente_detalhe", pk=cliente.pk)
    contexto = {
        "titulo": f"Editar {cliente.nome}",
        "form": form,
        "botao": "Salvar alterações",
        "voltar": "locadora:cliente_lista",
    }
    return render(request, "locadora/form.html", contexto)


def cliente_excluir(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        try:
            cliente.delete()
        except ProtectedError:
            messages.error(request, "Este cliente tem aluguéis registrados e não pode ser excluído.")
            return redirect("locadora:cliente_detalhe", pk=pk)
        messages.success(request, "O cliente foi excluído.")
        return redirect("locadora:cliente_lista")
    contexto = {
        "titulo": "Excluir cliente",
        "objeto": cliente.nome,
        "botao": "Excluir cliente",
        "voltar": "locadora:cliente_detalhe",
        "voltar_pk": cliente.pk,
    }
    return render(request, "locadora/confirmar_exclusao.html", contexto)


# --------------------------------------------------------------- aluguéis
def aluguel_lista(request):
    situacao = request.GET.get("status", "")
    alugueis = Aluguel.objects.select_related("cliente", "carro")
    if situacao:
        alugueis = alugueis.filter(status=situacao)
    contexto = {
        "alugueis": alugueis,
        "situacao": situacao,
        "opcoes_status": Aluguel.Status.choices,
    }
    return render(request, "locadora/aluguel_lista.html", contexto)


def aluguel_detalhe(request, pk):
    aluguel = get_object_or_404(Aluguel.objects.select_related("cliente", "carro"), pk=pk)
    return render(request, "locadora/aluguel_detalhe.html", {"aluguel": aluguel})


def aluguel_novo(request):
    if request.method == "POST":
        form = AluguelForm(request.POST)
        if form.is_valid():
            aluguel = form.save()
            atualizar_status_carro(aluguel.carro)
            messages.success(request, f"Aluguel #{aluguel.pk} registrado. O carro agora está alugado.")
            return redirect("locadora:aluguel_detalhe", pk=aluguel.pk)
    else:
        # Vindo do botão "Alugar" da lista de carros, já vem com o carro escolhido.
        form = AluguelForm(initial={"carro": request.GET.get("carro")})
    contexto = {
        "titulo": "Registrar aluguel",
        "form": form,
        "botao": "Registrar aluguel",
        "voltar": "locadora:aluguel_lista",
    }
    return render(request, "locadora/form.html", contexto)


def aluguel_editar(request, pk):
    aluguel = get_object_or_404(Aluguel, pk=pk)
    if aluguel.status == Aluguel.Status.FINALIZADO:
        messages.error(request, "Aluguéis finalizados não podem ser editados.")
        return redirect("locadora:aluguel_detalhe", pk=pk)

    carro_antigo = aluguel.carro
    form = AluguelForm(request.POST or None, instance=aluguel)
    if request.method == "POST" and form.is_valid():
        aluguel = form.save()
        atualizar_status_carro(carro_antigo)  # libera o carro anterior, se mudou
        atualizar_status_carro(aluguel.carro)
        messages.success(request, "O aluguel foi atualizado.")
        return redirect("locadora:aluguel_detalhe", pk=aluguel.pk)
    contexto = {
        "titulo": f"Editar aluguel #{aluguel.pk}",
        "form": form,
        "botao": "Salvar alterações",
        "voltar": "locadora:aluguel_lista",
    }
    return render(request, "locadora/form.html", contexto)


@require_POST
def aluguel_devolver(request, pk):
    aluguel = get_object_or_404(Aluguel, pk=pk, status=Aluguel.Status.ATIVO)
    aluguel.data_devolucao_real = timezone.localdate()
    aluguel.status = Aluguel.Status.FINALIZADO
    aluguel.save()  # recalcula o valor total com a data real
    atualizar_status_carro(aluguel.carro)
    messages.success(
        request,
        f"Devolução registrada. Valor final: R$ {aluguel.valor_total} ({aluguel.dias} diária(s)).",
    )
    return redirect("locadora:aluguel_detalhe", pk=pk)


def aluguel_excluir(request, pk):
    aluguel = get_object_or_404(Aluguel, pk=pk)
    if request.method == "POST":
        carro = aluguel.carro
        aluguel.delete()
        atualizar_status_carro(carro)
        messages.success(request, "O aluguel foi excluído.")
        return redirect("locadora:aluguel_lista")
    contexto = {
        "titulo": "Excluir aluguel",
        "objeto": f"Aluguel #{aluguel.pk} de {aluguel.cliente} ({aluguel.carro.modelo})",
        "botao": "Excluir aluguel",
        "voltar": "locadora:aluguel_detalhe",
        "voltar_pk": aluguel.pk,
    }
    return render(request, "locadora/confirmar_exclusao.html", contexto)
