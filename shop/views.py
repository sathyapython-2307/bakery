def about_view(request):
	return render(request, 'about.html')

def product_view(request):
	return render(request, 'product.html')

def blog_view(request):
	return render(request, 'blog.html')

def contact_view(request):
	return render(request, 'contact.html')

def home_view(request):
	return render(request, 'home.html')

def cake_view(request):
	return render(request, 'cake.html')

def savory_view(request):
	return render(request, 'savory.html')

def sweet_view(request):
	return render(request, 'sweet.html')

def cookie_view(request):
	return render(request, 'cookie.html')




from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.templatetags.static import static

import json

# Simple in-memory product catalog used by the search view.
# For production, replace with DB-backed Product models and proper indexing.
CATALOG = [
	{'name': 'Chocolate Truffle Cake', 'url': '/cake/', 'img': static('images/cake1.png'), 'category': 'cake'},
	{'name': 'Vanilla Cupcake', 'url': '/cake/', 'img': static('images/cake2.png'), 'category': 'cake'},
	{'name': 'Butter Cookies', 'url': '/cookie/', 'img': static('images/cookies1.png'), 'category': 'cookie'},
	{'name': 'Almond Biscotti', 'url': '/cookie/', 'img': static('images/cookies2.png'), 'category': 'cookie'},
	{'name': 'Savory Puff', 'url': '/savory/', 'img': static('images/savory1.png'), 'category': 'savory'},
	{'name': 'Gulab Jamun', 'url': '/sweet/', 'img': static('images/sweet1.png'), 'category': 'sweet'},
	{'name': 'Assorted Chocolates', 'url': '/product/', 'img': static('images/p11.png'), 'category': 'other'},
]

def add_to_wishlist(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
		except Exception:
			return JsonResponse({'status': 'error', 'message': 'invalid json'}, status=400)
		wishlist = request.session.get('wishlist', [])
		# dedupe by image path (or name if img missing)
		item_key = data.get('img') or data.get('name')
		if not any((it.get('img') == item_key or it.get('name') == item_key) for it in wishlist):
			wishlist.append(data)
			request.session['wishlist'] = wishlist
		return JsonResponse({'status': 'success', 'count': len(wishlist)})
	return JsonResponse({'status': 'error'}, status=400)


def add_to_cart(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
		except Exception:
			return JsonResponse({'status': 'error', 'message': 'invalid json'}, status=400)
		cart = request.session.get('cart', [])
		# dedupe by image or name; if exists, update quantity
		item_key = data.get('img') or data.get('name')
		existing = None
		for it in cart:
			if (it.get('img') == item_key) or (it.get('name') == item_key):
				existing = it
				break
		if existing:
			# update quantity if provided
			try:
				q = int(data.get('quantity', 1))
				existing['quantity'] = q
			except Exception:
				pass
			# update weight if provided
			if data.get('weight'):
				existing['weight'] = data.get('weight')
		else:
			# ensure default quantity
			if 'quantity' not in data:
				data['quantity'] = 1
			cart.append(data)
			request.session['cart'] = cart
		return JsonResponse({'status': 'success', 'count': len(cart)})
	return JsonResponse({'status': 'error'}, status=400)


def wishlist_view(request):
	"""Render the wishlist page using items stored in session."""
	wishlist = request.session.get('wishlist', [])
	return render(request, 'wishlist.html', {'wishlist': wishlist})


def cart_view(request):
	cart = request.session.get('cart', [])
	return render(request, 'cart.html', {'cart': cart})


def remove_from_wishlist(request):
	if request.method == 'POST':
		img = request.POST.get('img')
		wishlist = request.session.get('wishlist', [])
		wishlist = [item for item in wishlist if item.get('img') != img]
		request.session['wishlist'] = wishlist
	return redirect('wishlist')


def remove_from_cart(request):
	if request.method == 'POST':
		img = request.POST.get('img')
		cart = request.session.get('cart', [])
		cart = [item for item in cart if item.get('img') != img]
		request.session['cart'] = cart
	return redirect('cart')


def checkout_view(request):
	# If GET: render checkout page with query params or cart summary
	if request.method == 'GET':
		# allow one-item quick-buy via query params (name,img,price,quantity,weight)
		name = request.GET.get('name')
		img = request.GET.get('img')
		price = request.GET.get('price')
		quantity = request.GET.get('quantity', 1)
		weight = request.GET.get('weight')
		context = {
			'item': {
				'name': name,
				'img': img,
				'price': price,
				'quantity': quantity,
				'weight': weight
			}
		}
		return render(request, 'checkout.html', context)
	# POST: simulate order creation
	if request.method == 'POST':
		# collect order info from form
		order = {
			'name': request.POST.get('name'),
			'email': request.POST.get('email'),
			'address': request.POST.get('address'),
			'payment': request.POST.get('payment'),
			'item_name': request.POST.get('item_name'),
			'item_price': request.POST.get('item_price'),
			'quantity': request.POST.get('quantity', 1),
			'weight': request.POST.get('weight')
		}
		# store order in session as a simple success payload
		request.session['last_order'] = order
		return redirect('order_success')


def order_success_view(request):
	order = request.session.get('last_order')
	return render(request, 'order_success.html', {'order': order})


def clear_wishlist(request):
	"""Clear all items from wishlist stored in session."""
	if request.method == 'POST':
		request.session['wishlist'] = []
	return redirect('wishlist')


def product_detail_view(request, category=None, slug=None):
	"""Render a dynamic product detail page.

	Data may come from path params or from query parameters (name,img,price).
	"""
	# Prefer query params if present (JS will use them)
	name = request.GET.get('name') or request.GET.get('title')
	img = request.GET.get('img')
	price = request.GET.get('price')
	weight_options = request.GET.get('weights', '500 G,1 KG,2 KG,3 KG')
	if img and img.startswith('/static/'):
		img = img  # template will use as-is
	default_img = static('images/cake1.png')
	context = {
		'name': name or (slug.replace('-', ' ').upper() if slug else 'Product'),
		'img': img or default_img,
		'price': price or '₹ 0',
		'weights': [w.strip() for w in weight_options.split(',') if w.strip()]
	}
	return render(request, 'product_detail.html', context)

def search_view(request):
	"""A very small search endpoint that filters the in-memory CATALOG.

	Accepts GET param `q`. Returns `search_results.html` with `results` list.
	"""
	q = request.GET.get('q', '').strip()
	results = []
	if q:
		ql = q.lower()
		for item in CATALOG:
			if ql in item.get('name', '').lower() or ql in item.get('category', '').lower():
				results.append(item)
	return render(request, 'search_results.html', {'query': q, 'results': results})

def logout_view(request):
	"""Log the user out and redirect to the login page."""
	logout(request)
	return redirect('login')

def login_view(request):
	error = None
	reg_error = None
	reg_success = None
	if request.method == 'POST':
		form_type = request.POST.get('form-type', '')
		if form_type == 'login':
			# Login form submitted
			email = request.POST.get('login-email')
			password = request.POST.get('login-password')
			try:
				user_obj = User.objects.get(email=email)
				user = authenticate(request, username=user_obj.username, password=password)
			except User.DoesNotExist:
				user = None
			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				error = 'Invalid email or password.'
		elif form_type == 'register':
			# Register form submitted
			email = request.POST.get('register-email')
			password = request.POST.get('register-password')
			first_name = request.POST.get('first-name')
			last_name = request.POST.get('last-name')
			if not email or not password or not first_name or not last_name:
				reg_error = 'All fields are required.'
			elif User.objects.filter(username=email).exists():
				reg_error = 'A user with this email already exists.'
			else:
				user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
				reg_success = 'Registration successful! You can now log in.'
	return render(request, 'login.html', {'error': error, 'reg_error': reg_error, 'reg_success': reg_success})
