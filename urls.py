from django.urls import path

from . import views

app_name = "locadora"

urlpatterns = [
    path("", views.home, name="home"),
    # carros
    path("carros/", views.carro_lista, name="carro_lista"),
    path("carros/novo/", views.carro_novo, name="carro_novo"),
    path("carros/<int:pk>/", views.carro_detalhe, name="carro_detalhe"),
    path("carros/<int:pk>/editar/", views.carro_editar, name="carro_editar"),
    path("carros/<int:pk>/excluir/", views.carro_excluir, name="carro_excluir"),
    # clientes
    path("clientes/", views.cliente_lista, name="cliente_lista"),
    path("clientes/novo/", views.cliente_novo, name="cliente_novo"),
    path("clientes/<int:pk>/", views.cliente_detalhe, name="cliente_detalhe"),
    path("clientes/<int:pk>/editar/", views.cliente_editar, name="cliente_editar"),
    path("clientes/<int:pk>/excluir/", views.cliente_excluir, name="cliente_excluir"),
    # aluguéis
    path("alugueis/", views.aluguel_lista, name="aluguel_lista"),
    path("alugueis/novo/", views.aluguel_novo, name="aluguel_novo"),
    path("alugueis/<int:pk>/", views.aluguel_detalhe, name="aluguel_detalhe"),
    path("alugueis/<int:pk>/editar/", views.aluguel_editar, name="aluguel_editar"),
    path("alugueis/<int:pk>/devolver/", views.aluguel_devolver, name="aluguel_devolver"),
    path("alugueis/<int:pk>/excluir/", views.aluguel_excluir, name="aluguel_excluir"),
]
