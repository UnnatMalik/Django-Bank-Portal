from django.urls import path
from . import views

urlpatterns = [
    path('',views.manager,name='Manager'),
    path('loan_approve/<int:id>/',views.loan_approve,name='loan_approve'),
    path('loan_reject/<int:id>/',views.loan_reject,name='loan_reject'),
    path('Customers_management/',views.Customer_management,name='Customers management'),
    path('Customer/<int:user_id>/',views.Customer,name='Customer'),
    path('logout/',views.Logout,name='logout'),
    path('customersupports/',views.support_page,name='Customer support'),
    path('customersupports/<int:id>/',views.resolve_support,name='Resolve Customer support'),
    path('generate_ai_response/', views.generate_ai_response, name='generate_ai_response'),
    ]