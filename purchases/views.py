from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import PurchaseForm, PurchaseItemForm, ArticleForm, TransferForm
from .models import Purchase, PurchaseItem, Transfer
from home.models import Article
from django.forms import inlineformset_factory
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


def add_purchase(request):
    PurchaseItemFormSet = inlineformset_factory(Purchase, PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST, request.FILES)

        print(f"Form valid: {form.is_valid()}")
        print(f"Formset valid: {formset.is_valid()}")
        print(f"POST data: {request.POST}")

        if form.is_valid() and formset.is_valid():
            try:
                purchase = form.save(commit=False)
                items = formset.save(commit=False)

                # Calculate total purchase amount
                total_amount = sum(item.promo_price if item.promo_price else item.price for item in items if item.price)

                # Deduct total amount from the account balance
                account = purchase.account
                if account:
                    account.balance -= total_amount
                    account.save()

                purchase.save()  # Save the purchase instance after modifying the account balance

                for item in items:
                    item.purchase = purchase
                    item.save()
                formset.save_m2m()  # If there are any many-to-many relationships

                return redirect('purchases:purchase_list')
            except Exception as e:
                print(f"Error saving purchase: {e}")
                raise
        else:
            print(f"Form errors: {form.errors}")
            print(f"Formset errors: {formset.errors}")
            for form in formset:
                print(form.errors)
    else:
        form = PurchaseForm()
        formset = PurchaseItemFormSet()
        article_form = ArticleForm()

    return render(request, 'purchases/add_purchase.html',
                  {'form': form, 'formset': formset, 'article_form': article_form, 'articles': Article.objects.all()})


def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            return JsonResponse({'success': True, 'article': {'id': article.id, 'name': f"{article.name} by {article.producer_name}"}})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def purchase_list(request):
    purchases = Purchase.objects.all().prefetch_related('items__article')

    purchase_data = []
    for purchase in purchases:
        total_price = sum(
            item.promo_price if item.promo_price else item.price
            for item in purchase.items.all()
        )
        purchase_data.append({
            'purchase': purchase,
            'total_price': total_price
        })

    return render(request, 'purchases/purchase_list.html', {'purchase_data': purchase_data})

def add_transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            with transaction.atomic():
                transfer.source_account.balance -= transfer.amount
                transfer.destination_account.balance += transfer.amount
                transfer.source_account.save()
                transfer.destination_account.save()
                transfer.save()
            return redirect('purchases:transfer_list')
    else:
        form = TransferForm()
    return render(request, 'purchases/add_transfer.html', {'form': form})


def transfer_list(request):
    transfers = Transfer.objects.all()

    # Calculate the balances before and after the transfer
    transfer_data = []
    for transfer in transfers:
        source_balance_before = transfer.source_account.balance + transfer.amount
        destination_balance_before = transfer.destination_account.balance - transfer.amount
        transfer_data.append({
            'transfer': transfer,
            'source_balance_before': source_balance_before,
            'destination_balance_before': destination_balance_before,
        })

    return render(request, 'purchases/transfer_list.html', {'transfer_data': transfer_data})