from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from django.http import HttpResponse,JsonResponse
from users.models import Address
from books.models import Books
from order.models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from datetime import datetime
from django.conf import settings
import os
import time
# Create your views here.

@login_required
def order_place(request):
    '''显示提交订单页面'''
    # 接收数据
    books_ids = request.POST.getlist('books_ids')

    # 检验数据
    if not all(books_ids):
        # 跳转回购物车页面
        return redirect(reverse('cart:show'))

    # 用户收货地址
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)

    # 用户要购买商品的信息
    books_li = []
    # 商品的总数目和总金额
    total_count = 0
    total_price = 0

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id

    for id in books_ids:
        # 根据id获取商品的信息
        books = Books.objects.get_books_by_id(books_id=id)
        # 从redis中获取用户要购买的商品数目
        count = conn.hget(cart_key,id)
        books.count = count
        # 计算商品的小计
        amount = int(count) * books.price
        books.amount = amount
        books_li.append(books)

        # 累计计算商品的总数据和总金额