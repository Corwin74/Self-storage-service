import stripe
from django.core import serializers
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseNotFound
from django.urls import reverse
from random import randint, choice

from .models import Warehouse, Size, Box, Order
from .forms import RegisterUser


def index(request):
    return render(request, template_name='index.html')


@login_required(login_url='login_page')
def my_rent(request):
    if request.GET:
        request.user.email = request.GET.get('EMAIL_EDIT')
        request.user.phone = request.GET.get('PHONE_EDIT')
        request.user.set_password(request.GET.get('PASSWORD_EDIT'))
        request.user.save()
        return redirect('login_page')
    orders = request.user.orders.all()  # TODO optimize query
    context = {"orders": orders}
    return render(request, template_name='my-rent.html', context=context)


def boxes(request):
    index = 0
    warehouses_info = []

    all_warehouses = Warehouse.objects.all()
    
    warehouses_benefits = [
        'Рядом с метро',
        'Парковка',
        'Высокие потолки',
        'Большие боксы',
    ]

    for warehouse in all_warehouses:
        index += 1

        warehouse_info = {
            'id': warehouse.id,
            'index': index,
            'city': warehouse.name,
            'address': warehouse.address,
            'total_free_boxes': warehouse.boxes.filter(occupied=False).count(),
            'total_boxes': warehouse.boxes.count(),
            'price_from': 1000,
            'benefit': choice(warehouses_benefits),
            'max_height': randint(3, 6),
            'temperature': randint(10, 25)
        }

        warehouses_info.append(warehouse_info)

    boxes_volume_to_3 = []
    boxes_volume_to_10 = []
    boxes_volume_from_10 = []
    available_boxes = Box.objects.filter(occupied=False)

    for box in available_boxes:
        if box.size.name < 3:
            boxes_volume_to_3.append(box)
        elif box.size.name < 10:
            boxes_volume_to_10.append(box)
        elif box.size.name >= 10:
            boxes_volume_from_10.append(box)

    context = {
        'warehouses': warehouses_info,
        'available_boxes': available_boxes,
        "boxes_volume_to_3": boxes_volume_to_3,
        "boxes_volume_to_10": boxes_volume_to_10,
        "boxes_volume_from_10": boxes_volume_from_10,
    }

    return render(request, template_name='boxes.html', context=context)


def fetch_boxes(request, id):
    boxes = Warehouse.objects.get(id=id).boxes.all()
    data = serializers.serialize("json", boxes)
    return HttpResponse(data)


def faq(request):
    return render(request, template_name='faq.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('my_rent')
    return render(request, template_name='login.html')


def logout_view(request):
    logout(request)
    return redirect('main')


def registration_view(request):
    if request.method == 'POST':
        form = RegisterUser(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('my_rent')
    else:
        form = RegisterUser()
    return render(request, 'registration.html', {'form': form})


@login_required(login_url='login_page')
def create_order(request, box_id: int):
    """Создание заказа на аренду."""
    box = get_object_or_404(Box, pk=box_id)
    
    order = Order()
    order.name = f"Заказ пользователя {request.user} со склада \"{box.warehouse}\""
    order.customer = request.user
    order.box = box
    order.save()

    payment_url = request.build_absolute_uri(
        reverse('make_payment', kwargs={'payment_id': order.payment_id}))

    return redirect(payment_url, code=303)

def make_payment(request, payment_id):
    """Производит платёж."""
    stripe.api_key = settings.STRIPE_API_KEY

    try:
        order = Order.objects.get(payment_id=payment_id)
    except ValidationError:
        return HttpResponseNotFound('Неверный формат id платежа.')
    except Rent.DoesNotExist:
        return HttpResponseNotFound(f'Платёж {payment_id} не найден.')

    if order.paid:
        return HttpResponseNotFound(f'Платёж {payment_id} оплачен.')

    amount = order.box.cost * 100
    payment_name = f"Заказ пользователя {request.user} со склада \"{order.box.warehouse}\""

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'rub',
                'product_data': {
                    'name': payment_name,
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse('successful_payment', kwargs={'payment_id': payment_id})),
        cancel_url=request.build_absolute_uri(
            reverse('cancelled_payment', kwargs={'payment_id': payment_id})),
        client_reference_id=payment_id,
        customer_email=order.customer.email,
    )

    order.stripe_payment_id = session.id
    order.save()

    return redirect(session.url, code=303)


def successful_payment(request, payment_id):
    context = {}

    try:
        order = Order.objects.get(payment_id=payment_id)
    except ValidationError:
        return HttpResponseNotFound('Неверный формат id платежа.')
    except Order.DoesNotExist:
        return HttpResponseNotFound(f'Платёж {payment_id} не найден.')

    order.paid = True
    order.save()

    box = Box.objects.get(id=order.box.id)
    box.occupied = True
    box.customer = request.user
    box.end_date = order.end_date
    box.save()

    return render(request, 'successful_payment.html', context)

def cancelled_payment(request, payment_id):
    context = {}

    try:
        order = Order.objects.filter(payment_id=payment_id).delete()
    except ValidationError:
        return HttpResponseNotFound('Неверный формат id платежа.')
    except Order.DoesNotExist:
        return HttpResponseNotFound(f'Платёж {payment_id} не найден.')

    return render(request, 'cancelled_payment.html', context)
