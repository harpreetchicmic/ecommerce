from django.urls import path
from myapp import views
from django.urls import path, include
from rest_framework import routers
from .views import *


router=routers.DefaultRouter()
router.register(r'signup',signupViewset,basename='signup')
router.register(r'product',ProductViewSet,basename='product')
router.register(r'cart',Add_to_cart_ViewSet,basename='cart')
router.register(r'getproduct',get_products,basename='getproduct')
router.register(r'recentlyviewed',recently_viewedViewSet,basename='recentlyviewed')
router.register(r'orderhistory',order_history,basename='orderhistory')
router.register(r'transactionhistory',transaction_history,basename='transactionhistory')
router.register(r'productreview',product_review,basename='productreview')

urlpatterns =[
    path('verify/',verifyView.as_view()),
    path('signin/',signin.as_view()),
    path('logout/',LogoutUserView.as_view()),
    path('category/',categoriesView.as_view()),
    path('resend_otp/',resend_otp.as_view()),
    path('forgot_password/',forgotpasswordView.as_view()),
    path('login_superuser/',login_superuser.as_view()),
    path('getname/',get_name.as_view()),
    path('create_checkout/',CreateCheckoutSession.as_view()),
    path('success/', SuccessView.as_view()),
    path('cancel/', views.cancel,),
    path('intent/',intent.as_view()),
    path('intent_success/',IntentSuccessView.as_view())
    
]
urlpatterns+=router.urls

