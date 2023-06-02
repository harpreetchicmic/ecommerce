from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
class signupSerializer(serializers.ModelSerializer):
    class Meta:
        model=signup
        fields=('__all__')

class categorySerializer(serializers.ModelSerializer):
    class Meta:
        model=category
        fields=('__all__')


class productSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Addproduct
        fields=('__all__')


class CartItemSerializer(serializers.ModelSerializer):
    product_name=serializers.SerializerMethodField()
    product_description=serializers.SerializerMethodField()
    image_url=serializers.SerializerMethodField()
    class Meta:
        model=cart
        fields=('__all__')        

    def get_product_name(self,obj):
        try:
            data=Addproduct.objects.get(id=obj.product_id_id).name
        except:
            data='No product Name'
        return data
    
    def get_product_description(self,obj):
        try:
            data=Addproduct.objects.get(id=obj.product_id_id).product_details
        except:
            data='No product Name'
        return data     
    def get_image_url(self,obj):
        try:
            data=Addproduct.objects.get(id=obj.product_id_id).photo.url
        except:
            data='No product Name'
        return data       

class product_reviewSerializer(serializers.ModelSerializer):
    username=serializers.SerializerMethodField()
    date=serializers.SerializerMethodField()
    class Meta:
        model=productreview
        fields=('__all__')

    def get_username(self,obj):
        try:
            data=User.objects.get(id=obj.user_id_id).username
        except:
            data='No username'
        return data
    
    def get_date(self,obj):
        try:
            data=str(self.Meta.model.objects.get(id=obj.id).created_at)[:10]
        except:
            data='No Date'
        return data


class name_serializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username']


class recently_viewedSerializer(serializers.ModelSerializer):
    class Meta:
        model=recently_viewed
        fields=('__all__')


class pro_serializer(serializers.ModelSerializer):
    class Meta:
        model=Addproduct
        fields=['name','product_details','photo']

class order_historySerializer(serializers.ModelSerializer):
    date=serializers.SerializerMethodField()
    product_name=serializers.SerializerMethodField()
    username=serializers.SerializerMethodField()
    price=serializers.SerializerMethodField()
    total_count=serializers.SerializerMethodField()
    class Meta:
        model=order
        fields=['order_id','quantity','date_of_payment','product_name','address','username','price','date','total_count']

    def get_product_name(self,obj):
        try:
            data=pro_serializer(Addproduct.objects.get(id=obj.product_id_id)).data
        except:
            data='no data found'
        return data

    def get_username(self,obj):
        id=self.context.get('id')
        try:
            data=User.objects.get(id=id).username
        except:
            data='No username'
        return data

    def get_price(self,obj):
        try:
            data=Addproduct.objects.get(id=obj.product_id_id).price
        except:
            data='No price'
        return data
    
    def get_date(self,obj):
        try:
            data=str(self.Meta.model.objects.get(id=obj.id).date_of_payment)[:10]
        except:
            data='No Date'
        return data

    def get_total_count(self,obj):
        id=self.context.get('id')
        try:
            data=self.Meta.model.objects.filter(user_id_id=id).count()
        except:
            data='No Date'
        return data



class transaction_historySer(serializers.ModelSerializer):
    date=serializers.SerializerMethodField()
    product_name=serializers.SerializerMethodField()
    product_details=serializers.SerializerMethodField()
    class  Meta:
        model=order
        fields=['transaction_id','paid','date','product_name','product_details']

    def get_product_name(self,obj):
        try:
            ins=Addproduct.objects.get(id=obj.product_id_id).name
        except:
            ins='no data fetched'
        return f'{ins}'
    def get_date(self,obj):
        try:
            data=str(self.Meta.model.objects.get(id=obj.id).date_of_payment)[:10]
        except:
            data='No Date'
        return data
    def get_product_details(self,obj):
        try:
            ins=productSerializer(Addproduct.objects.get(id=obj.product_id_id)).data
        except:
            ins='No Date'
        return ins
    

class new_order_serializer(serializers.ModelSerializer):
    date=serializers.SerializerMethodField()
    data=serializers.SerializerMethodField()
    class Meta:
        model=order
        fields=['order_id','date','address','data']
    def get_date(self,obj):
        try:
            data=str(self.Meta.model.objects.get(id=obj.id).date_of_payment)[:10]
        except:
            data='No Date'
        return data
    
    def get_data(self,obj):
        id=self.context.get('id')
        try:
            if obj.order_id is '':
                data='no data'
            else:
                data=order_historySerializer(order.objects.filter(order_id=obj.order_id),many=True,context={'id':id}).data
        except:
            data='No data'
        return data