from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class signup(models.Model):
    
    phone_number=models.BigIntegerField()
    otp=models.IntegerField(null=True)
    verified=models.BooleanField(default=False)
    rel_id=models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    is_vendor=models.BooleanField(default=False,null=True)

class category(models.Model):
    category_name=models.CharField(max_length=260)


class Addproduct(models.Model):
    name=models.CharField(max_length=100)
    price=models.IntegerField(null=True, blank=True)
    cat_name=models.ForeignKey(category,on_delete=models.CASCADE)
    photo=models.FileField(upload_to='images',null=True,blank=True)
    product_details=models.CharField(max_length=500)  
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,null=True) 
    quantity=models.IntegerField(null=True,blank=True)


class cart(models.Model):
    product_id=models.ForeignKey(Addproduct,on_delete=models.CASCADE,null=True)
    category_id=models.ForeignKey(category,on_delete=models.CASCADE,null=True)
    product_price=models.BigIntegerField(null=True,blank=True)
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    quantity=models.IntegerField(null=True,blank=True)

class productreview(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Addproduct,on_delete=models.CASCADE)
    review=models.TextField()
    rating=models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class recently_viewed(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Addproduct,on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

class order(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product_id=models.ForeignKey(Addproduct,on_delete=models.CASCADE,null=True,blank=True)
    quantity=models.IntegerField(null=True)
    date_of_payment=models.DateTimeField(auto_now_add=True)
    address=models.TextField()
    paid=models.BooleanField(default=False)
    checkout_session=models.CharField(max_length=400,null=True)
    in_progress=models.BooleanField(default=False)
    order_id=models.BigIntegerField(null=True)
    transaction_id=models.CharField(null=True,max_length=17)