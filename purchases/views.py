from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import PurchaseForm, PurchaseItemForm, ArticleForm
from .models import Purchase, PurchaseItem
from home.models import Article
from django.forms import inlineformset_factory
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
                purchase = form.save()
                items = formset.save(commit=False)
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
    return render(request, 'purchases/purchase_list.html', {'purchases': purchases})
