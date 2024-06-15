import plotly.graph_objs as go
from plotly.offline import plot
from django.db.models.functions import Concat
from django.shortcuts import render
from django.db.models import Sum, F, Value as V, Case, When, DecimalField
from datetime import datetime, timedelta
from purchases.models import PurchaseItem
from home.models import Category, SubCategory, Article
from .forms import ExpenseFilterForm
from django.http import JsonResponse

def index(request):
    today = datetime.today()
    first_day_of_month = today.replace(day=1)
    last_month = today - timedelta(days=31)
    last_week = today - timedelta(days=7)

    if request.GET:
        form = ExpenseFilterForm(request.GET)
    else:
        form = ExpenseFilterForm(initial={
            'time_range': 'This month',
            'start_date': first_day_of_month,
            'end_date': today,
            'view_type': 'Total',
            'account': 'All'
        })

    if form.is_valid():
        time_range = form.cleaned_data['time_range']
        view_type = form.cleaned_data['view_type']
        category = form.cleaned_data['category']
        subcategory = form.cleaned_data['subcategory']
        account = form.cleaned_data['account']

        if time_range == 'This month':
            start_date = first_day_of_month
            end_date = today
        elif time_range == 'Last month':
            start_date = last_month
            end_date = today
        elif time_range == 'Last week':
            start_date = last_week
            end_date = today
        else:  # Custom
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
    else:
        start_date = first_day_of_month
        end_date = today
        view_type = 'Total'
        category = None
        subcategory = None
        account = 'All'

    purchase_items = PurchaseItem.objects.filter(purchase__date__gte=start_date, purchase__date__lte=end_date)
    if account != 'All':
        purchase_items = purchase_items.filter(purchase__account_id=account)

    # Use Case and When to prefer promo_price over price
    purchase_items = purchase_items.annotate(
        effective_price=Case(
            When(promo_price__isnull=False, then=F('promo_price')),
            default=F('price'),
            output_field=DecimalField()
        )
    )

    if view_type == 'Category' and category:
        expenses = purchase_items.filter(article__subcategory__category=category).values(
            'article__subcategory__name').annotate(total=Sum('effective_price'))
        labels = [expense['article__subcategory__name'] for expense in expenses]
        values = [expense['total'] for expense in expenses]
    elif view_type == 'Subcategory' and subcategory:
        expenses = purchase_items.filter(article__subcategory=subcategory).annotate(
            name_with_producer=Concat(F('article__name'), V(', '), F('article__producer_name'))
        ).values('name_with_producer').annotate(total=Sum('effective_price'))
        labels = [expense['name_with_producer'] for expense in expenses]
        values = [expense['total'] for expense in expenses]
    else:  # Total
        expenses = purchase_items.values('article__subcategory__category__name').annotate(total=Sum('effective_price'))
        labels = [expense['article__subcategory__category__name'] for expense in expenses]
        values = [expense['total'] for expense in expenses]

    total_price = sum(values)

    # Create the Plotly pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hovertemplate="<b>%{label}</b><br>Total: %{value}zł<br>%{percent}</br>"
    )])
    fig.update_layout(title_text='Expenses Overview')
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        'form': form,
        'chart_html': chart_html,
        'total_price': total_price,
        'today': today.strftime('%Y-%m-%d'),
        'first_day_of_month': first_day_of_month.strftime('%Y-%m-%d')
    }

    return render(request, 'home/index.html', context)

def get_expenses(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    # Use Case and When to prefer promo_price over price
    purchase_items = PurchaseItem.objects.filter(
        purchase__date__gte=start_date,
        purchase__date__lte=end_date
    ).annotate(
        effective_price=Case(
            When(promo_price__isnull=False, then=F('promo_price')),
            default=F('price'),
            output_field=DecimalField()
        )
    )

    expenses_by_category = purchase_items.values('article__subcategory__category__name').annotate(
        total=Sum('effective_price'))

    data = {
        'labels': [expense['article__subcategory__category__name'] for expense in expenses_by_category],
        'expenses': [expense['total'] for expense in expenses_by_category]
    }

    return JsonResponse(data)