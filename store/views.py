from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category,Order,OrderItem
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout


def home(request):
    products = Product.objects.all()

    context = {
        'products': products
    }

    return render(request, 'home.html', context)

def products(request):
    products = Product.objects.all()

    search = request.GET.get('search')
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    if search:
        products = products.filter(name__icontains=search)

    if category:
        products = products.filter(category_id=category)

    if sort == 'low':
        products = products.order_by('price')

    elif sort == 'high':
        products = products.order_by('-price')

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories
    }

    return render(request, 'products.html', context)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    context = {
        'product': product
    }

    return render(request, 'product_detail.html', context)

def cart(request):
    cart = request.session.get('cart', {})

    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    context = {
        'cart_items': cart_items,
        'total': total
    }

    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + quantity

    if cart[product_id] > product.stock:
        cart[product_id] = product.stock

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        product = Product.objects.get(id=product_id)

        if action == 'increase':
            if cart[product_id] < product.stock:
                cart[product_id] += 1

        elif action == 'decrease':
            if cart[product_id] > 1:
                cart[product_id] -= 1
            else:
                del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')

@login_required
@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]

        # Check whether enough stock is available
        if quantity > product.stock:
            return redirect('cart')

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':

        order = Order.objects.create(
            user=request.user,
            customer_name=request.POST.get('customer_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            total_amount=total
        )

        for item in cart_items:

            product = item['product']
            quantity = item['quantity']

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            product.stock -= quantity
            product.save()

        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'total': total
    }

    return render(request, 'checkout.html', context)

@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)

    context = {
        'order': order
    }

    return render(request, 'order_success.html', context)

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'orders': orders
    }

    return render(request, 'orders.html', context)

@login_required
def order_detail(request, order_id):
    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    context = {
        'order': order
    }

    return render(request, 'order_detail.html', context)
from django.contrib.auth.models import User
from django.contrib.auth import login
def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'register.html',
                {'error': 'Username already exists.'}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('home')

    return render(request, 'register.html')

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(
            request,
            'login.html',
            {'error': 'Invalid username or password.'}
        )

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    return render(request, 'profile.html')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')