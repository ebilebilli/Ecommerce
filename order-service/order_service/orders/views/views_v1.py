from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny  # prod-da öz permission-ların
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from ..models import * 
from ..serializers import *


#Order Create
@api_view(['GET', 'POST'])
def orders_list_create(request):
    if request.method == 'GET':
        orders = Order.objects.all().order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
@api_view(['GET', 'PATCH', 'DELETE'])
def orders_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#OrderItem
# GET / POST
@api_view(['GET', 'POST'])
def orderitems_list_create(request):
    if request.method == 'GET':
        items = OrderItem.objects.select_related('order').all().order_by('-id')
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET / PATCH / DELETE /order-items/<id>/
@api_view(['GET', 'PATCH', 'DELETE'])
def orderitems_detail(request, pk):
    try:
        item = OrderItem.objects.get(pk=pk)
    except OrderItem.DoesNotExist:
        return Response({"error": "OrderItem not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrderItemSerializer(item)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = OrderItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
def create_order_from_shopcart(request):
    data = request.data
    items = data.pop('items', [])

        # 1️⃣ Order yarat
    order_serializer = OrderSerializer(data=data)
    if order_serializer.is_valid():
        order = order_serializer.save()
    else:
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2️⃣ OrderItem-ları yarat
    for item in items:
        item['order'] = order.id  # ForeignKey-a order.id əlavə et
        item_serializer = OrderItemSerializer(data=item)
        if item_serializer.is_valid():
            item_serializer.save()
        else:
            return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Order and items created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['PATCH'])
def update_order_item_status(request, pk):
    try:
        item = OrderItem.objects.get(pk=pk)
    except OrderItem.DoesNotExist:
        return Response({"error": "OrderItem not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if new_status not in dict(OrderItem.Status.choices):
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    item.status = new_status
    item.save()

    item.order.check_and_approve()

    serializer = OrderItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)
