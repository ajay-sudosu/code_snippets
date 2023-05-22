from django.contrib import admin
from .models import *


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_mobile', 'is_laptop', 'item', 'remarks')


admin.site.register(Inventory, InventoryAdmin)
