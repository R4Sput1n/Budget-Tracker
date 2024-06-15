from django.db import models
from home.models import Article


class Unit(models.Model):
    name = models.CharField(max_length=5, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    name = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}: {self.balance}"

class Transfer(models.Model):
    source_account = models.ForeignKey(BankAccount, related_name='outgoing_transfers', on_delete=models.CASCADE)
    destination_account = models.ForeignKey(BankAccount, related_name='incoming_transfers', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    source_balance_before = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    destination_balance_before = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Transfer of {self.amount} from {self.source_account} to {self.destination_account} on {self.date}"


class Purchase(models.Model):
    date = models.DateField()
    account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Purchase on {self.date}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    amount = models.FloatField(default=1)
    unit = models.ForeignKey(Unit, default='inne', on_delete=models.SET_DEFAULT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promo_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        article_name = self.article.name if self.article else 'Unknown Article'
        unit_name = self.unit.name if self.unit else 'Unknown Unit'
        promo_price = self.promo_price if self.promo_price else 'N/A'
        return f"{article_name} ({self.amount} {unit_name}) at {self.price} (Promo: {promo_price}) for {self.purchase.date}"
