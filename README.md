# Prime Car – sistema de aluguel de carros (Trabalho Prático 03)

Aplicação web em **Django** para uma locadora de carros. Todo o CRUD é feito por
páginas HTML (Django Templates), sem depender do Django Admin.

## Como executar

```bash
# 1. (opcional) criar ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. instalar o Django
pip install -r requirements.txt

# 3. criar as tabelas do banco (SQLite)
python manage.py makemigrations locadora
python manage.py migrate

# 4. (opcional) cadastrar dados de exemplo
python manage.py popular

# 5. rodar o servidor
python manage.py runserver
```

Acesse http://127.0.0.1:8000/

O Django Admin (`/admin/`) existe só para apoio durante o desenvolvimento.
Para usá-lo: `python manage.py createsuperuser`.

## Modelos (models.py)

| Modelo    | Campos principais                                                        | Relacionamento                         |
|-----------|--------------------------------------------------------------------------|----------------------------------------|
| `Cliente` | nome, cpf, cnh, telefone, e-mail                                         | —                                      |
| `Carro`   | marca, modelo, ano, cor, placa, câmbio, lugares, valor da diária, situação | —                                      |
| `Aluguel` | datas de retirada/devolução, valor total, situação                       | `ForeignKey` → `Cliente` e `Carro`     |

## CRUD pela interface

| Entidade | Create | Read | Update | Delete |
|----------|--------|------|--------|--------|
| Carros   | `/carros/novo/` | `/carros/` e `/carros/<id>/` | `/carros/<id>/editar/` | `/carros/<id>/excluir/` |
| Clientes | `/clientes/novo/` | `/clientes/` e `/clientes/<id>/` | `/clientes/<id>/editar/` | `/clientes/<id>/excluir/` |
| Aluguéis | `/alugueis/novo/` | `/alugueis/` e `/alugueis/<id>/` | `/alugueis/<id>/editar/` | `/alugueis/<id>/excluir/` |

Extras: busca e filtros nas listas, mensagens de sucesso/erro (`django.contrib.messages`)
e botão **Registrar devolução**.

## Regras de negócio

- Só carros com situação **Disponível** aparecem ao registrar um aluguel.
- Ao registrar um aluguel o carro passa para **Alugado**; ao devolver (ou excluir o aluguel) volta a **Disponível**. Carros em manutenção não mudam sozinhos.
- Valor total = nº de diárias × valor da diária (mínimo de 1 diária). Na devolução, o valor é recalculado com a data real.
- A data de devolução não pode ser anterior à retirada; CPF e placa são validados e únicos.
- Carros e clientes com aluguéis registrados não podem ser excluídos (`on_delete=PROTECT`).

## Estrutura (padrão MTV)

```
Prime_Car/
├── manage.py
├── requirements.txt
├── config/                  # configurações do projeto (settings, urls)
└── locadora/                # app
    ├── models.py            # Model
    ├── forms.py             # validações dos formulários
    ├── views.py             # View
    ├── urls.py
    ├── templates/locadora/  # Template
    ├── static/locadora/style.css
    └── management/commands/popular.py
```
