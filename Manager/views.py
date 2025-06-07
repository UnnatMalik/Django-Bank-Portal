import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from bank.models import Loan, User_reg, Transactions, Supports, BillPayment
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import BadHeaderError, EmailMessage
from BankPortal import settings
from django.template.loader import render_to_string
import google.generativeai as genai 
from django.views.decorators.csrf import csrf_exempt
import logging
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

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
    customer_support = Supports.objects.all().order_by('timestamp')
    context = {
        'customer_supports': customer_support,
    }
    return render(request, 'customer_support.html', context)

def resolve_support(request,id):
    if request.method == 'POST':
        support = get_object_or_404(Supports, id=id)
        support.support_status = 'RESOLVED'
        support.save()
        body = request.POST.get('response_content')
        context = {
            'support': support,
            'body': body,
            'user': request.user,
        }

        html_message = render_to_string('email_template.html', context)
        try:
            email_message = EmailMessage(
                subject=f"Support Request for {support.issue}",
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[support.email,]
            )
            email_message.content_subtype = "html"
            email_message.send()
            messages.success(request, 'Support request resolved successfully')
        except BadHeaderError:
            messages.error(request, 'Invalid header found.')
            return redirect('Customer support')
        
        return redirect('Customer support')
    return JsonResponse({'status': 'error'}, status=405)

def AI_response(query, customer_name):
    try:
        services = [
            "Transfer Funds",
            "Deposit Funds",
            "Withdraw Funds",
            "Support",
            "Transaction history download"
        ]
        context = {
            "services": services,
            "account openning": "name,phone,email,account_number,account_type,address,pan,aadhaar,dob",
            "Account types" : ["Savings","Current","Business"]
        }
        
        # Configure Gemini AI
        try:
            genai.configure(api_key="")
        except Exception as config_error:
            logger.error(f"Failed to configure Gemini AI: {str(config_error)}")
            raise Exception("Failed to initialize AI service")

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",  # Updated to correct model name
                system_instruction=f"You are a Bank Manager at CHD-BANK, and you are talking to a customer who wants to know about the bank and its services. these are some things you can keep in mind {context}"
            )
        except Exception as model_error:
            logger.error(f"Failed to create Gemini model: {str(model_error)}")
            raise Exception("Failed to initialize AI model")

        try:
            response = model.generate_content(query)
            return response.text
        except Exception as generate_error:
            logger.error(f"Failed to generate content: {str(generate_error)}")
            raise Exception("Failed to generate AI response")

    except Exception as e:
        logger.error(f"AI_response error: {str(e)}")
        raise

@csrf_exempt
def generate_ai_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            if not query:
                return JsonResponse({'error': 'Query is required'}, status=400)
            
            logger.info(f"Processing AI response for query: {query[:100]}...")  # Log truncated query
            
            try:
                ai_response = AI_response(query, "Customer")
                return JsonResponse({
                    'response': ai_response,
                    'status': 'success'
                })
            except Exception as ai_error:
                logger.error(f"AI service error: {str(ai_error)}")
                # Return a more user-friendly error message
                return JsonResponse({
                    'error': 'Unable to generate response at the moment. Please try again.',
                    'status': 'error'
                }, status=500)
                
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON decode error: {str(json_error)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in generate_ai_response: {str(e)}")
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_customer_support_response(query):
    try:
        return AI_response(query, "Customer")
    except Exception:
        greeting = "Dear valued customer,\n\n"
        context = "Thank you for reaching out to CHD Bank customer support. I understand your concern regarding "
        closing = "\n\nIf you have any further questions, please don't hesitate to ask.\n\nBest regards,\nCHD Bank Customer Support"
        return f"{greeting}{context}{query}.{closing}"
