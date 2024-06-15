from django import forms
from home.models import Category, SubCategory
from purchases.models import BankAccount


class ExpenseFilterForm(forms.Form):
    VIEW_TYPE_CHOICES = [
        ('Total', 'Total'),
        ('Category', 'Category'),
        ('Subcategory', 'Subcategory'),
    ]
    TIME_RANGE_CHOICES = [
        ('This month', 'This month'),
        ('Last month', 'Last month'),
        ('Last week', 'Last week'),
        ('Custom', 'Custom'),
    ]
    ACCOUNT_CHOICES = [('All', 'All')] + [(account.id, account.name) for account in BankAccount.objects.all()]

    view_type = forms.ChoiceField(choices=VIEW_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    subcategory = forms.ModelChoiceField(queryset=SubCategory.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    time_range = forms.ChoiceField(choices=TIME_RANGE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    account = forms.ChoiceField(choices=ACCOUNT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
