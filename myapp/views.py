from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from .helpers import send_otp_to_phone
import random
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework import status
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from random import randrange
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import stripe
from django.db.models import Sum
from ecommerce.settings import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
from datetime import datetime


# Create your views here.
class signupViewset(ModelViewSet):
    queryset = signup.objects
    serializer_class = signupSerializer

    def create(self, request, *args, **kwargs):

        try:
            data = request.data
            phone_number = data['phone_number']
            if self.queryset.filter(phone_number=phone_number, verified=False).exists():
                record = self.queryset.get(
                    phone_number=phone_number, verified=False)
                User.objects.get(id=record.rel_id_id).delete()
                record.delete()
            password = data['password']
            name = data['name']
            details = data['detail']
            if phone_number is None or password is None or name is None or details is None:
                return Response({'error': 'All fields required'},
                                status=HTTP_400_BAD_REQUEST)
            phone = signup.objects.filter(phone_number=phone_number)
            if not phone:
                ob = User.objects.create(
                    username=data['name'],

                )
                ob.set_password(data['password'])
                ob.save()
                obj = signup.objects.create(
                    rel_id_id=ob.id,
                    phone_number=999009
                )

                obj.phone_number = data['phone_number']
                otp = random.randint(1000, 9999)
                obj.otp = otp
                obj.save()
                if int(data['detail']) == 1:
                    obj.is_vendor = True
                    obj.save()
                send_otp_to_phone(obj.phone_number, otp)
                return Response({
                    'status': True,
                    'message': 'otp sent successfully',
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'message': 'phone_number already exists',
                    'response': 'fail',
                    'status': False,

                }, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e), 'message': 'fail'})


class verifyView(APIView):
    @action(detail=True, methods=['post'])
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            cred = signup.objects.get(phone_number=data['phone_number'])
            if cred:
                if cred.otp == int(data['otp']):
                    cred.verified = True
                    cred.save()
                    print('saved')
                    return Response({
                        'status': True,
                        'response': 'success',
                        'message': 'user verified'
                    }, status=HTTP_200_OK)

                else:
                    return Response({
                        'status': False,
                        'response': 'fail',
                        'message': 'otp does not match'
                    }, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({
                'status': False,
                'response': 'fail',
                'message': 'phone or otp field is invalid'
            })


class signin(APIView):
    @csrf_exempt
    @action(detail=True, methods=['post'])
    @permission_classes((AllowAny,))
    def post(self, request):
        try:
            data = request.data
            password = data['password']
            phone_number = data['phone_number']

            if phone_number is None or password is None:
                return Response({'error': 'Please provide both phonenumber and password'},
                                status=HTTP_400_BAD_REQUEST)
            obj = signup.objects.get(phone_number=phone_number)
            user = User.objects.get(id=obj.rel_id_id)
            serializer = name_serializer(user)
            if user:
                if obj.verified == 0:
                    return Response({'message': 'user not verified please complete registration',
                                    'status': False})
                elif check_password(password, user.password):
                    user_with_token = Token.objects.filter(user=user).exists()
                    if not user_with_token:
                        token, _ = Token.objects.get_or_create(user=user)
                        login(request, user)
                        return Response({'token': token.key,
                                        'message': 'logined successfully',
                                         'data': serializer.data,
                                         'status': True},
                                        status=HTTP_200_OK)
                    else:
                        Token.objects.get(user=user).delete()
                        token, _ = Token.objects.get_or_create(user=user)
                        login(request, user)
                        return Response({'token': token.key,
                                        'message': 'logined successfully',
                                         'status': True,
                                         'data': serializer.data},
                                        status=HTTP_200_OK)
                else:
                    return Response({'message': 'Incorrect password',
                                    'status': False},
                                    )
        except:
            return Response({'error': 'Invalid Credentials',
                             'status': False},
                            status=HTTP_400_BAD_REQUEST)


class LogoutUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id)
            Token.objects.get(user=user).delete()
            logout(request)
            print('Logout success')
            return Response({'response': 'Success',
                            'status': True,
                             'message': 'User logout Successful'}, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({'error': str(error),
                             'status': False,
                             'message': 'User logout failed'}, status=status.HTTP_400_BAD_REQUEST)


class categoriesView(APIView):
    def get(self, request):
        result = category.objects.all()
        serializer = categorySerializer(result, many=True)
        return Response({'status': 'success', "data": serializer.data}, status=200)


class ProductViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Addproduct.objects
    serializer_class = productSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            obj = category.objects.get(id=data['cat_name'])
            user = signup.objects.get(rel_id_id=request.user.id)
            if obj and user.is_vendor:
                Addproduct.objects.create(
                    name=data['name'],
                    price=data['price'],
                    product_details=data['product_details'],
                    photo=data['photo'],
                    cat_name_id=data['cat_name'],
                    user_id_id=request.user.id,
                    quantity=data['quantity']
                )

                return Response({
                    'status': True,
                    'response': 'success',
                    'message': 'Product added successfully'
                }, status=HTTP_200_OK)
        except Exception as error:
            return Response({
                'error': str(error),
                'status': False,
                'message': 'category does not exist'
            })

    def list(self, request, *args, **kwargs):
        try:
            user = signup.objects.get(rel_id_id=request.user.id)
            if user.is_vendor:
                result = self.queryset.filter(user_id_id=request.user.id)
                serialized = self.serializer_class(result, many=True)
                return Response({'data': serialized.data, })
        except Exception as error:
            return Response({
                'status': False,
                'message': 'product does not exist'
            }, status=HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            user = signup.objects.get(rel_id_id=request.user.id)
            if user.is_vendor:
                obj = self.queryset.get(
                    user_id_id=request.user.id, id=self.kwargs['pk'])
                obj.delete()
                return Response({'status': 200,
                                 'message': 'product deleted successfully'})
        except Exception as error:
            return Response({
                'status': 401,
                'message': 'PRODUCTS NOT FOUND'
            })

    def retrieve(self, request, *args, **kwargs):
        try:
            user = signup.objects.get(rel_id_id=request.user.id)
            if user.is_vendor:
                obj = self.queryset.get(
                    user_id_id=request.user.id, id=self.kwargs['pk'])
                serializer = self.serializer_class(obj)
                return Response({'status': True,
                                'data': serializer.data})
        except Exception as error:
            return Response({'status': False,
                             'message': 'product not found'})


class resend_otp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            obj = signup.objects.get(phone_number=data['phone_number'])
            if obj:
                otp = random.randint(1000, 9999)
                obj.otp = otp
                obj.save()
                send_otp_to_phone(obj.phone_number, otp)
                return Response({
                    'status': True,
                    'response': 'success',
                    'message': 'otp sent successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'status': False,
                    'message': 'phone_number  not registered so create an account',
                    'response': 'success',
                }, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'fail'})


class forgotpasswordView(APIView):  # 1  resend te 2nd reset pass
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            obj = signup.objects.get(phone_number=data['phone_number'])
            if obj:
                reset_password = data['reset_password']
                confirm_password = data['confirm_password']
                if reset_password == confirm_password:
                    print(reset_password)
                    print(confirm_password)
                    print(obj.rel_id)
                    ins = User.objects.get(id=obj.rel_id_id)
                    ins.set_password(confirm_password)
                    ins.save()
                    return Response({
                        'status': True,
                        'message': 'password changed successfully'
                    })
                else:
                    return Response({'status': True,
                                    'message': 'reset password DOES NOT matched with confirm password'})
        except Exception as error:
            return Response({'status': False,
                             'message': 'fill phone number'})


class Add_to_cart_ViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = cart.objects
    serializer_class = CartItemSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            product_id = data['product_id']
            quantity = int(data['quantity'])
            obj = Addproduct.objects.get(id=product_id)
            ins = signup.objects.get(rel_id_id=request.user.id)
            if not ins.is_vendor:
                if obj.quantity == 0:
                    return Response({'message': 'product currently out of stock ',
                                     'status': False}, status=HTTP_404_NOT_FOUND)
                elif obj.quantity > quantity or obj.quantity == quantity:
                    try:
                        cart_item = self.queryset.get(
                            product_id_id=obj.id, user_id_id=request.user.id)

                        cart_item.quantity = quantity
                        cart_item.save()
                        pro_price = Addproduct.objects.get(
                            id=cart_item.product_id_id).price
                        cart_item.product_price = cart_item.quantity*pro_price
                        cart_item.save()
                        # product_price = quantity*pro_price.price
                        # cart_item.product_price=product_price
                        # cart_item.product_price*=quantity
                        # cart_item.save()
                        # obj.quantity-=quantity
                        # obj.save()
                        return Response({'message': 'PRODUCT ADDED TO CART SUCCESSFULLY',
                                         'response': "Success",
                                        'status': True}, status=HTTP_200_OK)
                    except:
                        cart_item = self.queryset.create(
                            product_id_id=obj.id,
                            product_price=obj.price*quantity,
                            category_id_id=obj.cat_name_id,
                            user_id_id=request.user.id)
                        cart_item.quantity = quantity
                        cart_item.save()
                        # obj.quantity-=quantity
                        # obj.save()
                        return Response({'message': 'PRODUCT ADDED TO CART SUCCESSFULLY',
                                        'status': True})
                elif obj.quantity < quantity:
                    return Response({'message': 'Limit Exceded,please decrease the quantity of products'})
            else:
                return Response({'message': 'not an authenticated user'})

        except Exception as error:
            return Response({
                'status': 404,
                'message': 'product does not exist'
            }, status=HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        try:
            try:
                page = int(request.GET.get('page'))
            except:
                return Response({'message': 'page  not found'})
            if page > 1:
                offset = (page-1)*5
                limit = 5
            else:
                offset = 0
                limit = 5
            result = self.queryset.filter(user_id_id=request.user.id).order_by(
                '-id')[offset:offset+limit]
            res = self.queryset.filter(user_id_id=request.user.id).count()
            result2 = self.queryset.filter(
                user_id_id=request.user.id).aggregate(Sum('product_price'))
            serialized = self.serializer_class(result, many=True)
            return Response({'data': serialized.data,
                             'status': True,
                             'Total_price': result2,
                             'product_count': res},
                            status=HTTP_200_OK)
        except Exception as error:
            return Response({
                'status': 401,
                'message': 'user does not exist'
            })

    def destroy(self, request, *args, **kwargs):
        try:
            result = self.queryset.get(
                user_id_id=request.user.id, id=self.kwargs['pk']).delete()
            return Response({'message': 'product deleted from cart successfully'})
        except Exception as error:
            return Response({
                'status': 401,
                'message': 'product does not exist'
            })


class login_superuser(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data['email']
        password = data['password']
        if email is None or password is None:
            return Response({'error': 'Please provide both phonenumber and password'},
                            status=HTTP_400_BAD_REQUEST)

        obj = User.objects.get(email=email)

        if obj.is_superuser:

            if obj.email == data['email'] and check_password(password, obj.password):
                user_with_token = Token.objects.filter(user=obj).exists()
                if not user_with_token:
                    token, _ = Token.objects.get_or_create(user=obj)
                    login(request, obj)
                    return Response({'token': token.key,
                                    'message': 'logined successfully'},
                                    status=HTTP_200_OK)
                else:
                    Token.objects.get(user=obj).delete()
                    token, _ = Token.objects.get_or_create(user=obj)
                    login(request, obj)
                    return Response({'token': token.key,
                                    'message': 'logined successfully'},
                                    status=HTTP_200_OK)
            else:
                return Response({'message': 'email or password does  not match'})
        else:
            return Response({'message': 'user not a super_user'})


class get_products(viewsets.ViewSet):
    queryset = Addproduct.objects
    serializer_class = productSerializer

    def list(self, request):
        result = self.queryset.all()
        serializer = self.serializer_class(result, many=True)
        return Response({'status': 'success', "data": serializer.data}, status=200)

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.queryset.get(id=self.kwargs['pk'])
            serializer = self.serializer_class(obj)
            return Response({'status': True,
                            'data': serializer.data})
        except Exception as error:
            return Response({'status': False,
                             'message': 'product not found'})


class product_review(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = productreview.objects
    serializer_class = product_reviewSerializer

    def create(self, request):
        try:
            data = request.data
            print(request.user.id)
            print(data['product_id'])
            ins = order.objects.filter(user_id_id=request.user.id, product_id_id=int(
                data['product_id']), paid=True).first()
            if ins is None:
                return Response({'message': 'you can not add reviews and rating ..you need to purchase the product for adding reviews or rating',
                                 'status': False}, status=HTTP_404_NOT_FOUND)
            try:
                obj = productreview.objects.get(
                user_id_id=request.user.id, product_id_id=int(data['product_id']))
                obj.rating = data['rating']
                obj.review = data['review']
                if int(data['rating']) > 5:
                    return Response({'message': 'rating can be in the scale of 1 to 5'})
                obj.save()
                return Response({'message': 'review and rating added successfully'},
                                status=HTTP_200_OK)
            except:
                if int(data['rating']) > 5:
                    return Response({'message': 'rating can be in the scale of 1 to 5'})
                self.queryset.create(
                    user_id_id=request.user.id,
                    product_id_id=data['product_id'],
                    review=data['review'],
                    rating=data['rating'],
                )
                return Response({'message': 'review and rating added successfully'},
                                status=HTTP_200_OK)
        except:
            return Response({'message': 'fail',
                             'status': False}, status=HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        try:
            data = int(request.GET.get('product_id'))
            ins = self.queryset.filter(product_id_id=data)
            if not ins:
                return Response({'message': 'no reviews and ratings found for this product', 'status': 200}, status=HTTP_200_OK)
            avg_rating = []
            for i in ins:
                avg_rating.append(i.rating)
            final_rating = sum(avg_rating)/len(avg_rating)
            serializer = self.serializer_class(ins, many=True)
            return Response({'data': serializer.data,
                             'message': 'all reviews and rating fetched of product',
                             'response': 'success',
                             'status': True,
                             'avg_rating': final_rating},
                            status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e),
                            'message': 'no reviews and ratings found for this product',
                             'response': 'fail',
                             'status': False},
                            status=HTTP_404_NOT_FOUND)


class get_name(APIView):
    def post(self, request):
        try:
            data = request.data
            print(data)
            phone = data['phone_number']
            obj = signup.objects.get(phone_number=phone)
            result = User.objects.get(id=obj.rel_id_id)
            serializer = name_serializer(result)
            if result:
                return Response({'data': serializer.data,
                                 'status': True}, status=HTTP_200_OK)
        except:
            return Response({'message': 'invalid phone_number',
                             'status': False}, status=HTTP_404_NOT_FOUND)


class recently_viewedViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = recently_viewed.objects
    serializer_class = recently_viewedSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data['product_id']
            obj = self.queryset.get(
                product_id_id=data,
                user_id_id=request.user.id,
            )
            obj.viewed_at = datetime.now()
            obj.save()
            return Response({'message': 'product viewed',
                             'response': 'success'}, status=HTTP_200_OK)
        except:
            obj = self.queryset.create(
                product_id_id=data,
                user_id_id=request.user.id,
            )
            return Response({'message': 'product viewed',
                             'response': 'success'})

    def list(self, request):
        try:
            obj = self.queryset.filter(
                user_id_id=request.user.id).order_by('-viewed_at')[0:5]
            serialized = self.serializer_class(obj, many=True)
            return Response({'data': serialized.data,
                             'message': 'recently viewed items',
                             'response': 'success',
                             'status': True}, status=HTTP_200_OK)
        except:
            return Response({
                'status': False,
                'response': 'fail'
            }, status=HTTP_404_NOT_FOUND)


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        data = request.data
        var = data['address']
        stripe.api_key = STRIPE_SECRET_KEY
        orders = cart.objects.filter(user_id_id=request.user.id)
        print(orders)
        mylist = []
        for i in orders:
            asdf = Addproduct.objects.get(id=i.product_id_id)
            data = {
                'price_data': {

                    'currency': 'inr',
                    'product_data': {
                        'name': asdf.name,
                    },
                    'unit_amount': asdf.price*100
                },
                'quantity': i.quantity
            }
            mylist.append(data)
            print(mylist)
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=mylist,
                mode='payment',
                success_url='https://eccomercechicmic.netlify.app/success',
                cancel_url='https://eccomercechicmic.netlify.app/failure',
            )

            order_id = random.randrange(111111111111, 999999999999)

            for i in orders:
                asdf = Addproduct.objects.get(id=i.product_id_id)
                order.objects.create(product_id_id=asdf.id,
                                     checkout_session=checkout_session['id'],
                                     address=var,
                                     quantity=i.quantity,
                                     user_id_id=request.user.id,
                                     in_progress=True,
                                     order_id=order_id
                                     )
            return JsonResponse({'sessionId': checkout_session['id'],
                                 'url': checkout_session['url']})
        except Exception as e:
            print(e)
            return Response({'error': str(e), 'message': 'fail'})


class SuccessView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # session_id = request.GET.get('checkout_session')
            # stripe.api_key = STRIPE_SECRET_KEY
            # session = stripe.checkout.Session.retrieve(session_id)
            # if session.payment_status == 'paid':
            transaction_id = randrange(11111111111111111, 99999999999999999)
            obj = order.objects.filter(
                user_id=request.user.id, in_progress=True)
            for i in obj:
                i.paid = True
                i.in_progress = False
                i.transaction_id = transaction_id
                i.save()

            for i in obj:
                ins = Addproduct.objects.get(id=i.product_id_id)
                ins.quantity -= i.quantity
                if ins.quantity < 0:
                    ins.quantity = 0
                ins.save()

            cart.objects.filter(user_id_id=request.user.id).delete()
            return Response({'message': 'success',
                             'status': True,
                             'response': 'success', }, status=HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': str(e), 'message': 'fail'})


@api_view
def cancel(request):
    ins = order.objects.get(user_id_id=request.user.id)
    session_id = ins.checkout_session
    stripe.api_key = STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status == 'unpaid':
        return Response({'message': 'fail'})


class order_history(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serilaizer_class = new_order_serializer
    queryset = order.objects

    def list(self, request):
        try:
            try:
                page = int(request.GET.get('page'))
            except:
                return Response({'message': 'page  not found'})
            if page > 1:
                offset = (page-1)*5
                limit = 5
            else:
                offset = 0
                limit = 5
            dummy = self.queryset.all()[0:20][offset:offset+limit]
            dummy_data = self.serilaizer_class(dummy, many=True).data
            obj = self.queryset.filter(user_id_id=request.user.id, paid=True).order_by(
                '-date_of_payment')[offset:offset+limit]

            if obj is None:
                return Response({'data': dummy_data,
                                'message': 'order history fetched successfully',
                                 'response': 'success',
                                 'status': True},
                                status=HTTP_200_OK)
            list_data = self.serilaizer_class(
                obj, many=True, context={'id': request.user.id})

            return Response({'data': list_data.data,
                             'message': 'order history fetched successfully',
                             'response': 'success',
                             'status': True},
                            status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e),
                             'response': 'fail',
                             'status': False},
                            status=HTTP_404_NOT_FOUND)


class transaction_history(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serilaizer_class = transaction_historySer
    queryset = order.objects

    def list(self, request):
        try:
            try:
                page = int(request.GET.get('page'))
            except:
                return Response({'message': 'page  not found'})
            if page > 1:
                offset = (page-1)*5
                limit = 5
            else:
                offset = 0
                limit = 5

            dummy = self.queryset.all()[0:20][offset:offset+limit]
            print(dummy)
            dummy_data = self.serilaizer_class(dummy, many=True).data

            order_count = self.queryset.filter(
                user_id_id=request.user.id).count()
            print(order_count)
            if order_count == 0:
                return Response({'data': dummy_data,
                                 'order_count': order_count,
                                'message': 'transaction history fetched successfully',
                                 'response': 'success',
                                 'status': True},
                                status=HTTP_200_OK)
            obj = self.queryset.filter(user_id_id=request.user.id).order_by(
                '-id')[offset:offset+limit]
            list_data = self.serilaizer_class(obj, many=True).data

            # for i in dummy_data:
            #     list_data.append(i)

            return Response({'data': list_data,
                             'order_count': order_count,
                             'message': 'transaction history fetched successfully',
                             'response': 'success',
                             'status': True},
                            status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e),
                             'response': 'fail',
                             'status': False},
                            status=HTTP_404_NOT_FOUND)


class intent(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        stripe.api_key = STRIPE_SECRET_KEY
        data = request.data
        address = data['address']
        amount = int(data['amount'])
        # code to pass list to metadata
        orders = cart.objects.filter(user_id_id=request.user.id)
        print(orders)
        mylist = []
        for i in orders:
            asdf = Addproduct.objects.get(id=i.product_id_id)
            data = {'product_name': asdf.name,
                    ' paid_status': True,
                    'date_of_payment': datetime.now()}
            mylist.append(data)
            print(mylist)

        try:
            paymentIntent = stripe.PaymentIntent.create(
                amount=amount,
                currency='inr',
                automatic_payment_methods={
                    'enabled': True,
                })
            for i in orders:
                asdf = Addproduct.objects.get(id=i.product_id_id)
                order.objects.create(product_id_id=asdf.id,
                                     address=address,
                                     quantity=i.quantity,
                                     user_id_id=request.user.id,
                                     in_progress=True,
                                     checkout_session=paymentIntent.client_secret

                                     )
            return Response({'paymentIntent': paymentIntent.client_secret,
                            'publishable key': STRIPE_PUBLISHABLE_KEY})
        except Exception as e:
            return Response({'error': str(e)})


class IntentSuccessView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    stripe.api_key = STRIPE_SECRET_KEY

    def get(self, request, *args, **kwargs):
        intent_id = request.GET.get('intent_id')
        try:
            obj = order.objects.filter(checkout_session=intent_id)
            for i in obj:
                i.paid = True
                i.in_progress = False
                i.save()

            for i in obj:
                ins = Addproduct.objects.get(id=i.product_id_id)
                ins.quantity -= i.quantity
                ins.save()

            cart.objects.filter(user_id_id=request.user.id).delete()

            return Response({
                            'message': 'success',
                            'status': True,
                            }, status=HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': str(e), 'message': 'fail'}, status=HTTP_404_NOT_FOUND)
