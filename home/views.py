import plotly.graph_objs as go
from plotly.offline import plot
from django.db.models.functions import Concat
from django.shortcuts import render
from django.db.models import Sum, F, Case, When, DecimalField, Avg, Value as V
from datetime import datetime, timedelta
from purchases.models import PurchaseItem, Income, Purchase, BankAccount
from home.models import Category, SubCategory, Article
from .forms import ExpenseFilterForm, HistoricalPriceForm
from django.http import JsonResponse


def index(request):
    today = datetime.today()
    first_day_of_month = today.replace(day=1)
    last_month = today - timedelta(days=31)
    last_week = today - timedelta(days=7)

    total_balance = calculate_balance(request)

    # Initialize the forms
    expense_form = ExpenseFilterForm(request.GET or None, initial={
        'time_range': 'This month',
        'start_date': first_day_of_month,
        'end_date': today,
        'view_type': 'Total',
        'account': 'All'
    })
    historical_form = HistoricalPriceForm(request.GET or None)

    # Handle the expense overview logic
    if expense_form.is_valid():
        time_range = expense_form.cleaned_data['time_range']
        view_type = expense_form.cleaned_data['view_type']
        category = expense_form.cleaned_data['category']
        subcategory = expense_form.cleaned_data['subcategory']
        account = expense_form.cleaned_data['account']

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
            start_date = expense_form.cleaned_data['start_date']
            end_date = expense_form.cleaned_data['end_date']
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

    # Handle the historical prices logic
    hist_chart_html = ''
    if historical_form.is_valid():
        hist_view_type = historical_form.cleaned_data['view_type']
        hist_category = historical_form.cleaned_data['category']
        hist_subcategory = historical_form.cleaned_data['subcategory']
        hist_item = historical_form.cleaned_data['item']

        if hist_view_type == 'Item' and hist_item:
            data = get_historical_prices(item=hist_item)
        elif hist_view_type == 'Subcategory' and hist_subcategory:
            data = get_historical_prices(subcategory=hist_subcategory)
        elif hist_view_type == 'Category' and hist_category:
            data = get_historical_prices(category=hist_category)

        # Create the Plotly line chart for historical prices
        hist_fig = go.Figure()
        for label, prices in data.items():
            hist_fig.add_trace(go.Scatter(x=prices['dates'], y=prices['values'], mode='lines', name=label))
        hist_fig.update_layout(title_text='Historical Prices')
        hist_chart_html = hist_fig.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        'form': expense_form,
        'historical_form': historical_form,
        'chart_html': chart_html,
        'hist_chart_html': hist_chart_html,
        'total_price': total_price,
        'today': today.strftime('%Y-%m-%d'),
        'first_day_of_month': first_day_of_month.strftime('%Y-%m-%d')
    }
    context.update(total_balance)

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

def get_historical_prices(item=None, subcategory=None, category=None):
    data = {}
    if item:
        prices = PurchaseItem.objects.filter(article=item).values('purchase__date').annotate(avg_price=Avg('price')).order_by('purchase__date')
        dates = [price['purchase__date'] for price in prices]
        values = [price['avg_price'] for price in prices]
        data[item.name] = {'dates': dates, 'values': values}
    elif subcategory:
        articles = Article.objects.filter(subcategory=subcategory)
        for article in articles:
            prices = PurchaseItem.objects.filter(article=article).values('purchase__date').annotate(avg_price=Avg('price')).order_by('purchase__date')
            dates = [price['purchase__date'] for price in prices]
            values = [price['avg_price'] for price in prices]
            data[article.name] = {'dates': dates, 'values': values}
    elif category:
        subcategories = SubCategory.objects.filter(category=category)
        for subcategory in subcategories:
            articles = Article.objects.filter(subcategory=subcategory)
            for article in articles:
                prices = PurchaseItem.objects.filter(article=article).values('purchase__date').annotate(avg_price=Avg('price')).order_by('purchase__date')
                dates = [price['purchase__date'] for price in prices]
                values = [price['avg_price'] for price in prices]
                data[article.name] = {'dates': dates, 'values': values}
    return data


def calculate_balance(request):
    today = datetime.today()
    first_day_of_month = today.replace(day=1)

    start_date = request.GET.get('start_date', first_day_of_month)
    end_date = request.GET.get('end_date', today)

    # Total income and spending within the selected date range
    total_income = Income.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))[
                       'total'] or 0
    total_spending = \
    PurchaseItem.objects.filter(purchase__date__range=[start_date, end_date]).aggregate(total=Sum('price'))[
        'total'] or 0

    # Total balance from all accounts
    total_balance = BankAccount.objects.aggregate(total=Sum('balance'))['total'] or 0

    context = {
        'total_balance': total_balance,
        'total_income': total_income,
        'total_spending': total_spending,
        'start_date': start_date,
        'end_date': end_date,
    }

    return context