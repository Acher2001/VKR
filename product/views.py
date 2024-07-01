from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from .models import City, Product, Shop
from .forms import CategoriesForm

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime


def city_list(request):
    city_list = City.objects.all()
    category_list = set([prod.category for prod in Product.objects.all()])

    form = CategoriesForm()
    return render(request,
                  'product/city_list.html',
                  {'cities': city_list,
                   'title': 'Доступные города',
                    'form': form})

def product_list(request):
    if request.method == "POST":
        form = CategoriesForm(request.POST)
        city_id = int(request.GET.get('city'))
        if form.is_valid():

            products = []
            for category in form.cleaned_data.get('Categories'):
                products.extend(list(Product.objects.filter(category_id=int(category))))

            return render(request,
                          'product/product_list.html',
                          {'title': 'Список продукции',
                           'products': products})

def form_check(request):
    if request.method == "POST":
        basket = []
        for key, value in request.POST.dict().items():
            if key.startswith("typeNumber") and int(value) > 0:
                basket.append((int(key.replace('typeNumber', '')), int(value)))

        if not basket:
            return HttpResponse(status=203)
        buffer = io.BytesIO()

        p = SimpleDocTemplate(buffer)
        pdfmetrics.registerFont(TTFont('golos-text', 'fonts/golos-text_regular.ttf'))
        pdfmetrics.registerFont(TTFont('golos-text-bold', 'fonts/golos-text_bold.ttf'))
        elements = []
        data = []
        data.append(['Товар', 'Цена', 'Количество', 'Итого'])
        sumprice = 0
        addresses = set()
        for id, count in basket:
            product = Product.objects.get(id=id)
            data.append([product.name, product.price+'р.', str(count), str(int(product.price.replace(' ', ''))*count)+'р.'])
            sumprice += int(product.price.replace(' ', ''))*count
            addresses.add(product.shop.name + ': ' +product.shop.address)
        data.append(['','', 'Cумма', str(sumprice)+'р.'])
        data = [[], [], [], ['\n'.join(addresses)]] + data
        t = Table(data)
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'golos-text'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('FONTSIZE', (0,0), (-1, len(addresses)+3), 12),
            ('FONTSIZE', (0,-1), (-1,-1), 12),
        ]))

        header_style = ParagraphStyle(
            name="Header",
            fontName='golos-text-bold',
            fontSize=16,
            alignment=1
        )
        header = Paragraph("Сравнительный список датчиков для выбора и предложения решения\n\n", style=header_style)
        elements.append(header)
        elements.append(t)
        p.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"check {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}.pdf")
    return redirect('/')
