import json

from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('Cart: ', cart)

    getItems = []
    getOrder = { 'getCartTotal' : 0, 'getCartItems' : 0, 'allowedShipping' : False}
    getCartItems = getOrder['getCartItems']

    for i in cart:
        try:
            getCartItems += cart[i]['quantity']

            getProduct = Product.objects.get(id=i)
            getTotal = (getProduct.priceProduct * cart[i]['quantity'])

            getOrder['getCartTotal'] += getTotal
            getOrder['getCartItems'] += cart[i]['quantity']
            
            getItem = {
                'productOrdered' : {
                    'id' : getProduct.id,
                    'nameProduct' : getProduct.nameProduct,
                    'priceProduct' : getProduct.priceProduct,
                    'imageURL' : getProduct.imageURL,
                },
                'quantityOrdered' : cart[i]['quantity'],
                'getOrderTotal' : getTotal,
            }
            getItems.append(getItem)

            if getProduct.digitalProduct == False:
                getOrder['allowedShipping'] = True
        except:
            pass
    return{
        'CartItems' : getCartItems,
        'Order' : getOrder,
        'Items' : getItems,
    }

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        getOrder, created = Order.objects.get_or_create(customerOrder=customer, completeOrder=False)
        getItems = getOrder.orderitem_set.all()
        getCartItems = getOrder.getCartItems
    else:
        getCookieData = cookieCart(request)
        getItems = getCookieData['Items']
        getOrder = getCookieData['Order']
        getCartItems = getCookieData['CartItems']

    return{
        'CartItems' : getCartItems,
        'Order' : getOrder,
        'Items' : getItems,
    }

def guestOrder(request, getData):
    print('User is not logged in')

    nameCustomer = getData['form']['name']
    emailCustomer = getData['form']['email']

    getCookieData = cookieCart(request)
    getItems = getCookieData['Items']

    getCustomer, created = Customer.objects.get_or_create(
        emailCustomer = emailCustomer.lower(),
    )
    getCustomer.nameCustomer = nameCustomer
    getCustomer.save()

    getOrder = Order.objects.create(customerOrder=getCustomer, completeOrder=False)

    for item in getItems:
        getProduct = Product.objects.get(id=item['productOrdered']['id'])
        getOrderItem = OrderItem.objects.create(
            productOrdered=getProduct,
            itemOrdered=getOrder,
            quantityOrdered=item['quantityOrdered'],
        )
    return getCustomer, getOrder