from decimal import Decimal
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from catalog.models import Category,Product
from preorders.models import Release
from .models import Variant,Location,Inventory,VariantCartItem,Purchase,PreorderAllocation
from .services import put_cart,reserve_checkout,cancel_purchase,reserve_preorder,CommerceError

class VariantFlowTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='vc_test',password='SecureTestPass_123')
        cat=Category.objects.create(name='Women',slug='women')
        self.product=Product.objects.create(category=cat,name='Cotton Shirt',slug='cotton-shirt',price=Decimal('100'),currency='BDT')
        self.variant=Variant.objects.create(product=self.product,sku='SHIRT-M-BLK',size='M',color='Black',price=Decimal('120'))
        self.location=Location.objects.create(code='dhaka',name='Dhaka')
        self.stock=Inventory.objects.create(variant=self.variant,location=self.location,on_hand=3)
    def test_checkout_reserves_and_cancels(self):
        put_cart(self.user,self.variant.pk,2)
        p,created=reserve_checkout(self.user,'checkout-key-0001')
        self.assertTrue(created)
        self.stock.refresh_from_db();self.assertEqual(self.stock.reserved,2)
        same,created=reserve_checkout(self.user,'checkout-key-0001')
        self.assertFalse(created);self.assertEqual(p.pk,same.pk)
        cancel_purchase(self.user,p.pk)
        self.stock.refresh_from_db();self.assertEqual(self.stock.reserved,0)
    def test_insufficient_stock_rolls_back(self):
        put_cart(self.user,self.variant.pk,4)
        with self.assertRaises(CommerceError): reserve_checkout(self.user,'checkout-key-0002')
        self.assertFalse(Purchase.objects.exists())
        self.stock.refresh_from_db();self.assertEqual(self.stock.reserved,0)
    def test_preorder_variant_allocation(self):
        now=timezone.now()
        release=Release.objects.create(product=self.product,state='preorder',reveal_at=now-timedelta(days=2),opens_at=now-timedelta(days=1),closes_at=now+timedelta(days=2),expected_ship_start=(now+timedelta(days=15)).date(),expected_ship_end=(now+timedelta(days=30)).date(),allocation=5,per_customer_limit=2)
        alloc=PreorderAllocation.objects.create(release=release,variant=self.variant,capacity=3)
        req,created=reserve_preorder(self.user,alloc.pk,2,'preorder-key-0001')
        self.assertTrue(created);alloc.refresh_from_db();self.assertEqual(alloc.reserved,2)
        with self.assertRaises(CommerceError): reserve_preorder(self.user,alloc.pk,1,'preorder-key-0002')
