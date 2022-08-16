from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json, uuid
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import midtransclient
import requests

from .forms import SignUpForm, ContactForm, APWNForm
from .models import *
from .utils import *

# ---------------------------------------------------------- Index Views ---------------------------------------------------------- #
def IndexView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems'] 
    getNewProducts = Product.objects.all().order_by('-id')[:3].annotate(discPrice=F('priceProduct')+10000)

    context = {
        'Type' : 'Kuffa',
        'NewProducts' : getNewProducts,
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
    }
    return render(request, 'index.html', context)

def StoreView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    getAllProducts = Product.objects.all().order_by('-id')[:3].annotate(discPrice=F('priceProduct')+10000)

    context = {
        'Type' : 'Store',
        'Products' : getAllProducts,
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/index.html', context)

def APWNView(request):
    if request.method == 'POST':
        getForm = APWNForm(request.POST, request.FILES)
        if getForm.is_valid():
            getNameProduct = getForm.cleaned_data['nameProduct']
            getImageProduct = getForm.cleaned_data['imageProduct']
            getPriceProduct = getForm.cleaned_data['priceProduct']
            getCategoryProduct = getForm.cleaned_data['categoryProduct']
            getDescriptionProduct = getForm.cleaned_data['descriptionProduct']
            setCategoryProduct = Category.objects.get(nameCategory=getCategoryProduct)
            
            Product.objects.create(
                nameProduct = getNameProduct,
                priceProduct = float(getPriceProduct),
                imageProduct = getImageProduct,
                categoryProduct = setCategoryProduct,
                descriptionProduct = getDescriptionProduct,
            )

            getCustomer = Customer.objects.values_list('emailCustomer', flat=True)

            getSubject = 'Kuffa New Product! ' + getNameProduct
            body = {
            'getNameProduct': getNameProduct,
            }
            getMessage = "\n".join(body.values())

            try:
                send_mail(getSubject, getMessage, settings.DEFAULT_FROM_EMAIL, list(getCustomer))
                messages.success(request, 'Product successfully added with newsletter!.')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("/admin/store/product/")
    
    form = APWNForm()

    context = {
        'Type' : 'Add Product (Newsletter)',
        'form' : form,
    }

    if request.user.is_superuser:
        return render(request, 'admin/add_product_with_newsletter.html', context)
    else:
        return redirect("admin:index")

def ProcessAPWNView(request):
    pass
    
# ---------------------------------------------------------- Index Views ---------------------------------------------------------- #

# ---------------------------------------------------- Cart and Checkout Views ---------------------------------------------------- #
def CartView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']

    context = {
        'Type' : 'Cart',
        'Items' : getItems,
        'Order' : getOrder,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/cart.html', context)

def CheckoutView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    getOrderID = ''
    getTransactionToken = ''

    if request.user.is_authenticated:
        getTotalOrder = getOrder.getCartTotal
    else:
        getTotalOrder = getOrder['getCartTotal']

    if getTotalOrder != 0:
        getOrderID = uuid.uuid4().hex[:30].upper()
        getSnap  = midtransclient.Snap(
            server_key=settings.PAYMENT_SERVER_KEY,
            client_key=settings.PAYMENT_CLIENT_KEY
        )
        getParam = {
            "transaction_details": {
                "order_id": str(getOrderID),
                "gross_amount": getTotalOrder
            }, "credit_card":{
                "secure" : True
            }
        }
        getTransaction = getSnap.create_transaction(getParam)
        getTransactionToken = getTransaction['token']

    context = {
        'Type' : 'Checkout',
        'Items' : getItems,
        'Order' : getOrder,
        'CartItems' : getCartItems,
        'TransactionOrder': getOrderID,
        'TransactionToken' : getTransactionToken,
        'ClientKey' : settings.PAYMENT_CLIENT_KEY,
    }
    return render(request, 'store/checkout.html', context)

def UpdateItemView(request):
    data = json.loads(request.body)
    getProductId = data['getProductId']
    getAction = data['getAction']
    print('Action: ', getAction)
    print('Product: ', getProductId)

    customer = request.user.customer
    product = Product.objects.get(id=getProductId)
    order, created = Order.objects.get_or_create(customerOrder=customer, completeOrder=False)

    orderItem, created = OrderItem.objects.get_or_create(itemOrdered=order, productOrdered=product)
    if getAction == 'add':
        orderItem.quantityOrdered = (orderItem.quantityOrdered + 1)
    elif getAction == 'remove':
        orderItem.quantityOrdered = (orderItem.quantityOrdered - 1)

    orderItem.save()

    if orderItem.quantityOrdered <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)
# ---------------------------------------------------- Cart and Checkout Views ---------------------------------------------------- #

# ---------------------------------------------------------- Order Views ---------------------------------------------------------- #
@csrf_exempt
def ProcessOrderView(request):
    getData = json.loads(request.body)

    if request.user.is_authenticated:
        getCustomer = request.user.customer
        getOrder, created = Order.objects.get_or_create(customerOrder=getCustomer, completeOrder=False)
    else:
        getCustomer, getOrder = guestOrder(request, getData)

    getTotal = float(getData['form']['getTotal'])
    getOrder.transactionOrder = getData['form']['getTransactionOrder']
    setTransactionCode = getOrder.transactionOrder

    if getTotal == float(getOrder.getCartTotal):
        getOrder.totalOrder = getTotal
        getOrder.completeOrder = True
        getOrder.totalProductOrder = getOrder.getCartItems
    getOrder.save()

    if getOrder.getShipping == True:
        # Get data dari Midtrans menggunakan REST Api #
        getHeaders = {
            'Accept': settings.HEADERS_ACCEPT,
            'Content-Type': settings.HEADERS_CONTENT_TYPE,
            'Authorization': settings.HEADERS_AUTHORIZATION
        }
        getPayment = requests.get(settings.API_STATUS_URL + setTransactionCode +'/status', headers=getHeaders)
        getPaymentData = getPayment.json()
        getTransactionId = getPaymentData['transaction_id']
        getGrossAmount = getPaymentData['gross_amount']
        getPaymentType = getPaymentData['payment_type']
        getTransactionStatus = getPaymentData['transaction_status']
        if getTransactionStatus == 'capture' or getTransactionStatus == 'settlement':
            getCompletePayment = True
        else:
            getCompletePayment = False

        # Save data ke table Payment #
        Payment.objects.create(
            transactionId = getTransactionId,
            pricePayment = float(getGrossAmount),
            statusPayment = getTransactionStatus,
            methodPayment = getPaymentType,
            completePayment = getCompletePayment,
        )
        getPaymentOrder = Payment.objects.get(transactionId=getTransactionId)

        # Save data ke table ShippingAddress #
        ShippingAddress.objects.create(
            customerOrder=getCustomer,
            itemOrdered=getOrder,
            paymentOrder=getPaymentOrder,
            nameShipping=getData['shipping']['nameShipping'],
            addressShipping=getData['shipping']['addressShipping'],
            cityShipping=getData['shipping']['cityShipping'],
            stateShipping=getData['shipping']['stateShipping'],
            zipcodeShipping=getData['shipping']['zipcodeShipping'],
            countryShipping=getData['shipping']['countryShipping'],
            phoneShipping=getData['shipping']['phoneShipping'],
            emailShipping=getData['shipping']['emailShipping'],
        )
        
        # Email detail order #
        getDataEmail = {
            'TransactionOrder': getOrder.transactionOrder, 'TotalOrder': getOrder.totalOrder, 'TotalProduct': getOrder.totalProductOrder, 'Payment' : getPaymentOrder,
            'Phone': getData['shipping']['phoneShipping'], 'Email': getData['shipping']['emailShipping'],
            'Address': getData['shipping']['addressShipping'], 'City': getData['shipping']['cityShipping'], 'State': getData['shipping']['stateShipping'],
            'ZipCode': getData['shipping']['zipcodeShipping'], 'Country': getData['shipping']['countryShipping'],
        }
        getHTML = render_to_string("store/orders/order-created-email.html", getDataEmail)
        getMessage = EmailMultiAlternatives(
            subject = 'Kuffa - Order Confirmation: ' + str(getOrder.transactionOrder),
            body="Order Mail",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[getData['shipping']['emailShipping']],
        )
        getMessage.attach_alternative(getHTML, "text/html")
        getMessage.send(fail_silently=False)
    return JsonResponse('Payment submitted..', safe=False)

def SuccessOrderView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']

    context = {
        'Type' : 'Order Confirmation',
        'Items' : getItems,
        'Order' : getOrder,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/orders/success_order.html', context)

def CheckOrderView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']

    if request.user.is_authenticated:
        getCustomer = request.user.customer
        getDetailOrder = ShippingAddress.objects.filter(customerOrder=getCustomer)
    
    else:
        getDetailOrder = ShippingAddress.objects.all()

    context = {
        'Type' : 'Orders',
        'Items' : getItems,
        'Order' : getOrder,
        'CartItems' : getCartItems,
        'CheckOrder' : getDetailOrder,
        'TotalCheckOrder' : getDetailOrder.count(),
    }
    return render(request, 'store/orders/orders.html', context)

def DetailOrderView(request, idDetailOrder):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    getShippingOrder = ShippingAddress.objects.get(itemOrdered__transactionOrder=idDetailOrder)
    setTransactionId = getShippingOrder.paymentOrder.transactionId
    getItemsOrder = OrderItem.objects.filter(itemOrdered__transactionOrder=idDetailOrder)
    getTotalOrder = Order.objects.get(transactionOrder=idDetailOrder)
    getPaymentOrder = Payment.objects.get(transactionId=setTransactionId)

    context = {
        'Type' : 'Orders Detail',
        'PaymentOrder' : getPaymentOrder,
        'ShippingOrder' : getShippingOrder,
        'ItemsOrder' : getItemsOrder,
        'TotalOrder' : getTotalOrder,
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/orders/order_detail.html', context)
# ---------------------------------------------------------- Order Views ---------------------------------------------------------- #

# -------------------------------------------------------- Products Views --------------------------------------------------------- #
def ProductsView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    getAllProducts = Product.objects.all().annotate(discPrice=F('priceProduct')+10000)
    getProductsPage = Paginator(getAllProducts, 6)
    getPageNumber = request.GET.get('page')
    getPage = getProductsPage.get_page(getPageNumber)

    context = {
        'Type' : 'Store',
        'Products' : getAllProducts,
        'Page' : getPage,
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
        'TotalProduct' : getProductsPage.count,
    }
    return render(request, 'store/products/product.html', context)

def DetailProductsView(request, idProducts):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    getDetailProducts = Product.objects.annotate(discPrice=F('priceProduct')+10000).get(id=idProducts)

    context = {
        'Type' : getDetailProducts.nameProduct + ' - ' + getDetailProducts.categoryProduct.nameCategory,
        'Products' : getDetailProducts,
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/products/detail_product.html', context)

def CategoryProductsView(request, categoryProducts):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    getCategory = Category.objects.values('nameCategory').order_by('nameCategory').distinct()
    getCategoryProducts = Product.objects.annotate(discPrice=F('priceProduct')+10000).filter(categoryProduct__nameCategory=categoryProducts)
    
    context = {
        'Type' : categoryProducts + ' Products',
        'Products' : getCategoryProducts,
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
        'Category' : getCategory,
        'CategoryProduct' : categoryProducts,
        'TotalCategory' : getCategoryProducts.count(),
    }
    return render(request, 'store/products/category_product.html', context)
# -------------------------------------------------------- Products Views --------------------------------------------------------- #

# --------------------------------------------------------- Users Views ----------------------------------------------------------- #
def ProfileView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems']
    if request.user.is_authenticated:
        getUser = request.user.username

    context = {
        'Type' : 'Profile - ' + getUser,
        'Items' : getItems,
        'Order' : getOrder,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/users/profile.html', context)

def RegisterView(request):
    if request.method == "POST":
        getForm = SignUpForm(request.POST)
        if getForm.is_valid():
            getFirstName = getForm.cleaned_data.get('first_name')
            getLastName = getForm.cleaned_data.get('last_name')
            getEmail = getForm.cleaned_data.get('email')
            setEmailLower = getEmail.lower()
            getUsername = getForm.cleaned_data.get('username')
            getPassword = getForm.cleaned_data.get('password1')
            getHashedPassword = make_password(getPassword)
            try:
                getCustomer = Customer.objects.get(emailCustomer=setEmailLower)
                getData = User(username=getUsername, password=getHashedPassword, email=setEmailLower, first_name=getFirstName, last_name=getLastName)
                getData.save()
                Customer.objects.filter(emailCustomer=setEmailLower).update(userCustomer=getData)
                messages.success(request, f'Account created for {getUsername}')
                new_user = authenticate(username=getForm.cleaned_data['username'], password=getForm.cleaned_data['password1'])
                login(request, new_user)
                return redirect("store:profile")
            except Customer.DoesNotExist:
                getData = User(username=getUsername, password=getHashedPassword, email=setEmailLower, first_name=getFirstName, last_name=getLastName)
                getData.save()
                Customer.objects.create(userCustomer=getData, nameCustomer=getFirstName, emailCustomer=setEmailLower)
                messages.success(request, f'Account created for {getUsername}')
                new_user = authenticate(username=getForm.cleaned_data['username'], password=getForm.cleaned_data['password1'])
                login(request, new_user)
                return redirect("store:profile")
        else:
            for msg in getForm.error_messages:
                print(getForm.error_messages[msg])

            return render(request=request, template_name="store/users/register.html", context={"form": getForm})
    
    getForm = SignUpForm
    return render(request=request, template_name="store/users/register.html", context={"form": getForm})
# --------------------------------------------------------- Users Views ----------------------------------------------------------- #

# ---------------------------------------------------- About and Contact Views ---------------------------------------------------- #
def AboutUsView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems'] 

    context = {
        'Type' : 'About Us',
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
    }
    return render(request, 'store/about/about_us.html', context)

def ContactUsView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems'] 

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            getSubject = 'Kuffa - Website Contact! From : ' + form.cleaned_data['nameContact'] + ' - ' + form.cleaned_data['emailContact']
            body = {
            'nameContact': form.cleaned_data['nameContact'],
            'emailContact': form.cleaned_data['emailContact'], 
            'messageContact': form.cleaned_data['messageContact'], 
            }
            getMessage = "\n".join(body.values())

            try:
                send_mail(getSubject, getMessage, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_CONTACT_EMAIL])
                messages.success(request, 'Contact form submitted successfully.')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("store:contact_us")
        
    form = ContactForm()

    context = {
        'Type' : 'Contact Us',
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
        'form' : form,
    }
    return render(request, 'store/about/contact_us.html', context)

def TestimonialsView(request):
    getData = cartData(request)
    getItems = getData['Items']
    getOrder = getData['Order']
    getCartItems = getData['CartItems'] 
    getOldestimonials = Testimonials.objects.all().order_by('-id')[:6]

    context = {
        'Type' : 'Testimonials',
        'Order' : getOrder,
        'Items' : getItems,
        'CartItems' : getCartItems,
        'OldTestimonials' : getOldestimonials,
    }
    return render(request, 'store/about/testimonials.html', context)
# ---------------------------------------------------- About and Contact Views ---------------------------------------------------- #