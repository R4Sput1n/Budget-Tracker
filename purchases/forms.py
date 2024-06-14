from django import forms
from .models import Purchase, PurchaseItem, Unit
from home.models import Article

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class PurchaseItemForm(forms.ModelForm):
    article = forms.ModelChoiceField(
        queryset=Article.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = PurchaseItem
        fields = ['article', 'amount', 'unit', 'price', 'promo_price']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'promo_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['name', 'producer_name', 'subcategory']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'producer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control', 'empty_label': 'Select subcategory (optional)'}),
        }
