from django.contrib import admin
from .models import Unit, Purchase, BankAccount, PurchaseItem


# Register your models here.
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0  # No extra blank forms
    fields = ['article', 'amount', 'unit', 'price', 'promo_price']
    readonly_fields = []

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'get_items')
    inlines = [PurchaseItemInline]

    def get_items(self, obj):
        items = obj.items.all()
        return ", ".join([f"{item.article.name} ({item.amount} {item.unit.name if item.unit else ''})" for item in items])

    get_items.short_description = 'Purchased Items'


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance',)