from django.shortcuts import render
from . models import *
from django. http import JsonResponse
import json
import datetime

# Create your views here.

# def cartCredentials(user):
#     # user = request.user
#     try:
#         customer = user.customer
#     except:
#         customer = False
#     if customer:
#         order = Order.objects.get(customer=customer)
#     else:
#         order = {'total_order_item':0, 'cart_total':0}

#     global total_order_item
#     global cart_total
#     total_order_item = order.total_order_item
#     cart_total = order.cart_total
    
#     return  cart_total
        
# cartCredentials(request)

def home(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        order= {'total_order_item':0, 'cart_total':0}
        items =[]
    # context ={'items':items, 'order':order}

    context = {"products":products, 'order':order}
    return render(request,'index.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        order= {'total_order_item':0, 'cart_total':0}
        items =[]

        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart={}

        items = [] 
        order = {'total_order_item':0, 'cart_total':0,'shipping':False}
        cartItems =order['total_order_item']
        for i in cart:
            try:
                cartItems += cart[i]['quantity']
            
                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])
                order['cart_total'] += total
                order['total_order_item'] += cart[i]['quantity']
            
                item = {
                    'product':{
                            'id':product.id,
                            'name':product.name,
                            'price':product.price,
                            'imageURL':product.imageURL,
                        },
                    'quantity':cart[i]['quantity'],
                    'cart_total':total
                    }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            
            except:
                pass
    context ={'items':items, 'order':order}

    return render(request,'cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
   
    else:
        order= {'total_order_item':0, 'cart_total':0}
        items =[]

        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart={}

        print('cart: ',cart)
        items = [] 
        order = {'total_order_item':0, 'cart_total':0,'shipping':False}
        cartItems =order['total_order_item']
        for i in cart:
            try:

           
                cartItems += cart[i]['quantity']
            
                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])
                order['cart_total'] += total
                order['total_order_item'] += cart[i]['quantity']
            
                item = {
                    'product':{
                            'id':product.id,
                            'name':product.name,
                            'price':product.price,
                            'imageURL':product.imageURL,
                        },
                    'quantity':cart[i]['quantity'],
                    'cart_total':total
                    }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            
            except:
                pass

    context ={'items':items, 'order':order}

    return render(request,'checkout.html',context)

def updateItems(request):
    print('func runnign')
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('productId:', productId)
    print('action:',action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, create = Order.objects.get_or_create(customer=customer,complete=False)
    order_item, create = OrderItem.objects.get_or_create(order=order,product=product)
    
    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1
    else:
        pass
    order_item.save()
    if order_item.quantity < 1:
        order_item.delete()


    return JsonResponse('cart updated succesfully',safe=False)

def processOrder(request):
    
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    cart = json.loads(request.COOKIES['cart'])
    

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        print('user not logged in')
        name = data['userFormData']['name']
        email = data['userFormData']['email']

        customer, created = Customer.objects.get_or_create(email=email,)
        customer.name = name
        customer.save()

        order, created = Order.objects.get_or_create(customer=customer,complete=True,transaction_id=transaction_id)

        for i in cart:
            product = Product.objects.get(id=i)
            quantity = cart[i]['quantity']
            print('product :',product)
            print('quantity :',quantity)

            OrderItem.objects.create(order=order,product=product,quantity=quantity)

    total = float(data['userFormData']['total'])
    order.transaction_id = transaction_id
        
    if total == order.cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address= data['shippingAddress']['address'],
                city=data['shippingAddress']['city'],
                state=data['shippingAddress']['state'],
                zipcode=data['shippingAddress']['zipcode'],
            )

    return JsonResponse('order processed successfully',safe=False)

    

