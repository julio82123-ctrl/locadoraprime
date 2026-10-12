from django.contrib import admin

from .models import Aluguel, Carro, Cliente

# O admin serve só para conferir dados durante o desenvolvimento.
admin.site.register(Cliente)
admin.site.register(Carro)
admin.site.register(Aluguel)
