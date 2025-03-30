from datetime import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from bank.models import Loan, User_reg , Transactions , Supports, BillPayment
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from BankPortal import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

# Create your views here.
@login_required()
@user_passes_test(is_manager)
def manager(request):
    loans = Loan.objects.all()
    users = User_reg.objects.all()
    transactions = Transactions.objects.all()
    supports = Supports.objects.all()
    billpayments = BillPayment.objects.all()
    total_loans = Loan.Loan_count(self=loans)
    total_transactions = transactions.count()
    context = {
        'loans':loans, 
        'users':users, 
        'transactions':transactions,
        'supports':supports,
        'billpayments':billpayments,
        'total_loans':total_loans,
        'total_transactions':total_transactions
        }
    return render(request,'manager.html',context)

def Logout(request):
    logout(request)
    messages.success(request,"You are now logged out")
    return redirect('login page')

def loan_approve(request, id):
    if request.method == 'POST':
        try:
            loan = Loan.objects.get(id=id)
            if loan.loan_status != 'PENDING':
                messages.error(request, 'Loan has already been processed.')
                return redirect('Manager')
            user = User_reg.objects.get(id=loan.user.id)
            print(user.user.username)
            transactions = Transactions.objects.create(user=user,transaction_type='Loan',amount=loan.loan_amount,about=f'Loan for {loan.loan_type} approved',receiptent=loan.loan_amount,receiptent_no='Bank')
            user.balance += loan.loan_amount
            loan.loan_status = 'APPROVED'
            user.save()
            loan.save()
            return redirect('Manager')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('Manager')

def loan_reject(request, id):
    if request.method == 'POST':
        try:
            loan = Loan.objects.get(id=id)
            if loan.loan_status != 'PENDING':
                messages.error(request, 'Loan has already been processed.')
                return redirect('Manager')
            user = User_reg.objects.get(user=request.user)
            loan.loan_status = 'REJECTED'
            user.save()
            loan.save()
            return redirect('Manager')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('Manager')
        
def Customer_management(request):
    users = User_reg.objects.all()
    context = {
        'Users':users,
        'User_count':users.count(),
        'Transaction_count' : Transactions.objects.all().count(),
    }
    return render(request,'customers_management.html', context)

def Customer(request, user_id):
    user = User_reg.objects.get(user_id=user_id)
    user_loan = Loan.objects.filter(user=user)
    transactions = Transactions.objects.filter(user=user)
    total_loan_amount = 0
    for loan in user_loan:
        if loan.loan_status == 'APPROVED':
            total_loan_amount += loan.loan_amount
        
    # print(user.DoB,user.address)
    context = {
        'User':user,
        'loans':user_loan,
        'transactions':transactions,
        'total_loans': user_loan.count(),
        # 'total_transaction': transactions.count(),
        'total_loan_amount': total_loan_amount,
    }
    return render(request,'customer.html',context)

def support_page(request):
    customer_support = Supports.objects.all()
    context = {
        'customer_supports': customer_support,
    }
    return render(request, 'customer_support.html', context)

def reslove_support(request,id):
    if request.method == 'POST':
        support = get_object_or_404(Supports, id=id)
        support.support_status = 'RESOLVED'
        # support.resolved_by = request.user
        # support.resolved_at = timezone.now()
        support.save()
        body = request.POST.get('response_content')
        print(body)
        context = {
            'support': support,
            'body': body,
            'user': request.user,
        }

        html_message = render_to_string('email_template.html', context)
        plain_text = strip_tags(html_message)
        try:
            email_message = EmailMessage(subject=f"Support Request for {support.issue}",body=html_message,from_email=settings.EMAIL_HOST_USER,to=[support.email,])
            email_message.content_subtype = "html"  # Set email format to HTML
            email_message.send()
            messages.success(request, 'Support request resolved successfully')
        except BadHeaderError:
            messages.error(request, 'Invalid header found.')
            return redirect('Customer support')
        
        return redirect('Customer support')
    return JsonResponse({'status': 'error'}, status=405)