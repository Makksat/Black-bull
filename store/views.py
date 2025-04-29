from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from store.models import Product
from django.contrib.auth import logout
from django.shortcuts import redirect


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    # Get search query from GET request
    query = request.GET.get('q')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |  # Search in name
            Q(description__icontains=query)  # Search in description
        ).distinct()  # Remove duplicates if a product matches both name and description
    else:
        products = Product.objects.all()

    # Get featured reviews (latest 3 reviews)
    featured_reviews = Feedback.objects.select_related('user', 'product').order_by('-created_at')[:3]

    context = {
        'products': products, 
        'cartItems': cartItems,
        'search_query': query,  # Pass the query back to the template
        'featured_reviews': featured_reviews,  # Add featured reviews to context
    }
    return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == float(order.get_cart_total):
		order.complete = True
		# Create a new order for future purchases
		if request.user.is_authenticated:
			Order.objects.create(customer=customer, complete=False)
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)  # Fetch product by ID
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Feedback
from django.contrib.auth.decorators import login_required

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    feedbacks = Feedback.objects.filter(product=product).order_by('-created_at')

    if request.method == "POST":
        comment = request.POST.get("comment")
        if request.user.is_authenticated:
            Feedback.objects.create(product=product, user=request.user, comment=comment)
            return redirect('product_detail', pk=pk)

    context = {'product': product, 'feedbacks': feedbacks}
    return render(request, 'store/product_detail.html', context)

def logout_view(request):
    logout(request)
    return redirect('store')

def contact(request):
    if request.method == 'POST':
        # Here you can add email sending functionality
        # For now, we'll just redirect back to the contact page
        return redirect('contact')
    return render(request, 'store/contact.html', {'cartItems': cartData(request)['cartItems']})

def about(request):
    return render(request, 'store/about.html', {'cartItems': cartData(request)['cartItems']})
