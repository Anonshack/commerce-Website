from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import Product, Order, Category, Customer
from django.views import View


class Index(View):
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})

        if cart:
            quantity = cart.get(product, 0)
            if quantity:
                if remove and quantity > 1:
                    cart[product] = quantity - 1
                elif remove:
                    cart.pop(product)
                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart[product] = 1

        request.session['cart'] = cart
        return redirect('homepage')

    def get(self, request):
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')


def store(request):
    cart = request.session.get('cart', {})

    if not cart:
        request.session['cart'] = {}

    category_id = request.GET.get('category')
    if category_id:
        products = Product.get_all_products_by_categoryid(category_id)
    else:
        products = Product.get_all_products()

    categories = Category.get_all_categories()
    data = {'products': products, 'categories': categories}

    print('you are : ', request.session.get('email'))
    return render(request, 'index.html', data)


class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = 'Invalid credentials'

        if customer and check_password(password, customer.password):
            request.session['customer'] = customer.id

            if Login.return_url:
                return HttpResponseRedirect(Login.return_url)
            else:
                Login.return_url = None
                return redirect('homepage')

        return render(request, 'login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return redirect('login')


class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        post_data = request.POST
        first_name = post_data.get('firstname')
        last_name = post_data.get('lastname')
        phone = post_data.get('phone')
        email = post_data.get('email')
        password = post_data.get('password')

        value = {'first_name': first_name, 'last_name': last_name, 'phone': phone, 'email': email}
        error_message = None

        customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password)
        error_message = self.validate_customer(customer)

        if not error_message:
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')
        else:
            data = {'error': error_message, 'values': value}
            return render(request, 'signup.html', data)

    def validate_customer(self, customer):
        error_message = None
        if not customer.first_name or len(customer.first_name) < 3:
            error_message = "Please enter a valid First Name (3 characters or more)"
        elif not customer.last_name or len(customer.last_name) < 3:
            error_message = 'Please enter a valid Last Name (3 characters or more)'
        elif not customer.phone or len(customer.phone) < 10:
            error_message = 'Please enter a valid Phone Number (10 characters or more)'
        elif len(customer.password) < 5:
            error_message = 'Password must be 5 characters or more'
        elif len(customer.email) < 5:
            error_message = 'Email must be 5 characters or more'
        elif customer.isExists():
            error_message = 'Email Address is already registered'

        return error_message


class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart', {})
        products = Product.get_products_by_id(list(cart.keys()))

        for product in products:
            order = Order(customer=Customer(id=customer), product=product,
                          price=product.price, address=address, phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()

        request.session['cart'] = {}
        return redirect('cart')


class OrderView(View):
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        return render(request, 'orders.html', {'orders': orders})
