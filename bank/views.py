# imports 
import decimal
from io import BytesIO
import requests
import base64
import matplotlib

from BankPortal import settings
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render , redirect
from .models import Loan, User_reg , Transactions , Supports, BillPayment
from django.contrib.auth import login , logout , authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import json
import google.generativeai as genai 
from django.db.models import Sum  # Add this import

def auth_user(user):
    return user.groups.filter(name='User').exists()
# homepage 
def homepage(request):
    if request.user.is_anonymous: 
        return render(request,'./homepage.html')
    else:
        user = User_reg.objects.get(user=request.user)
        return render(request,'./homepage.html',{"User":user})

# User profile page
def User_profile(request):
    '''This Python function retrieves a user profile from a User_reg model based on the request user and
    renders it in a user.html template.
    
    Parameters
    ----------
    request
        The `request` parameter in the `User_profile` function is typically an HttpRequest object that
    represents the request made by a user to the server. It contains information about the request, such
    as the user making the request, the method used (GET, POST, etc.), and any data sent along with
    
    Returns
    -------
        The function `User_profile` is returning a rendered HTML template named 'user.html' with the
    context data containing the user information fetched from the `User_reg` model.
    
    '''

    user = User_reg.objects.get(user=request.user)

    context = {
        "User" : user ,
    }
    
    return render(request,'./user.html',context)

# Login page
def loginpg(request):
    '''The `loginpg` function handles user login authentication and redirects users based on the outcome.
    
    Parameters
    ----------
    request
        The `request` parameter in the `loginpg` function is an object that represents the HTTP request
    made by the user. It contains information such as the method used (GET, POST, etc.), data submitted
    in the request (form data, parameters), user session information, and more. In this
    
    Returns
    -------
        The `loginpg` function returns either a redirect to the "Dashboard" page if the user is
    successfully authenticated and logged in, or a redirect back to the "login page" with an error
    message if the credentials are invalid. If the request method is not POST, it returns the rendered
    "loginpg.html" template.
    
    '''

    if request.method == 'POST':
        username_user = str(request.POST['name'])
        password_user = str(request.POST['password'])
        user = authenticate(username=username_user, password=password_user)
        if user :
            login(request,user)
            messages.success(request,"You are now logged in")
            if user.groups.filter(name='Manager').exists() :
                return redirect("Manager")
            else:
                return redirect("Dashboard")
        else:
            messages.error(request,"invalid Credentials")
            return redirect("login page")
    
    return render(request,"./loginpg.html")

# customer support page
def support(request):
    """
    The function `support` handles a POST request to submit a support request, create a support ticket
    in the database, generate a polite and professional response using a GenerativeModel, and send an
    HTML email response to the customer.
    
    :param request: The code snippet you provided is a Django view function that handles a POST request
    for submitting a support request. It captures the user's name, email, and issue from the request,
    saves the support request to the database using a model called Supports, and then generates a
    response to the user's issue using
    :return: The code snippet provided is a view function in Django that handles a POST request for
    submitting a support request. If the request method is POST, it retrieves the name, email, and issue
    from the request, creates a new entry in the Supports model, generates a response using a
    GenerativeModel, and sends an HTML email response to the customer.
    """

    if request.method == 'POST':
        Name = request.POST['name']
        email = request.POST['email']
        issue = request.POST['issue']
        try :   
            support = Supports.objects.create(name=Name,email=email,issue=issue)
            support.save()
            messages.success(request,"Support request submitted successfully")
        except Exception as e:
                messages.error(request,"An error occurred while submitting the support request")
                return redirect("support page")

    return render(request,'./support.html')

# Transaction page
def transaction(request):
    '''The `transaction` function generates a bank statement PDF for a user within a specified date range,
    including transaction history and account information.
    
    Parameters
    ----------
    request
        The code you provided is a Django view function for generating a bank statement PDF for a user's
    transactions within a specified date range. Let me explain the parameters used in the function:
    
    Returns
    -------
        The code is returning an HTTP response containing a PDF file with the bank statement details for
    the user within the specified date range. The PDF includes the bank logo, account information,
    transaction history table, and a footer with the bank name and current year.
    
    '''

    if request.user.is_anonymous: 
        messages.error(request,"login in order to access Transaction")
        return redirect("login page")
    user = User_reg.objects.get(user=request.user)
    transactions = Transactions.objects.filter(user=user)
    context={
        "User" : user,
        "Transactions" : transactions,
    }
    if request.method=='POST':
        user_profile = User_reg.objects.get(user=request.user)
        start_date = request.POST.get("start_date","2024-01-01")
        end_date = request.POST.get("end_date","2024-12-31")

        pdfmetrics.registerFont(TTFont('ArialUnicodeMS', 'C:\\Windows\\Fonts\\ARIALUNI.TTF'))

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="Bank-Statement.pdf"'
        
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

    # Add Bank Header with logo
        styles = getSampleStyleSheet()
        styles["Normal"].fontName = "ArialUnicodeMS"
        styles["Heading2"].fontName = "ArialUnicodeMS"
        logo_url = "https://clipartcraft.com/images/bank-logo-icon-9.png"  # Replace with the actual logo URL
        try:
            logo_response = requests.get(logo_url, stream=True)
            if logo_response.status_code == 200:
                logo_image = Image(BytesIO(logo_response.content), width=50, height=50)
                elements.append(logo_image)
            else:
                print("Failed to fetch the logo")
        except Exception as e:
            print(f"Error fetching logo: {e}")

        header = Paragraph("<b>CHD Bank</b><br/>Bank Statement", styles["Title"])
        elements.append(header)

        account_info = Paragraph(
            f"Account Number: <b>{user_profile.account_number}</b><br/>"
            f"Date : {start_date} to {end_date}",
            styles["Normal"]
        )
        elements.append(account_info)
        elements.append(Spacer(1, 12))

        # Add transaction history header
        elements.append(Paragraph("<b>Transaction History:</b>", styles["Heading2"]))

        # Fetch transactions within the date range
        transactions = Transactions.objects.filter(
            user=user_profile,
            timestamp__date__gte=datetime.strptime(start_date, "%Y-%m-%d").date(),
            timestamp__date__lte=datetime.strptime(end_date, "%Y-%m-%d").date()
        ).order_by("-timestamp")

        # Create table data
        data = [["Date", "Transaction Type", "Amount", "Recipient Account"]]
        for transaction in transactions:
            data.append([
                transaction.timestamp.date().strftime("%Y-%m-%d"),
                transaction.transaction_type,
                f"\u20B9{transaction.amount:,.2f}",
                transaction.receiptent_no or "N/A"
            ])

        # Create Table Style
        table = Table(data, colWidths=[100, 150, 100, 150])
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),  
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),      
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),             
                ("FONTNAME", (0, 0), (-1, -1), "ArialUnicodeMS"),   
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),           
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),    
                ("GRID", (0, 0), (-1, -1), 1, colors.black),       
            ])
        )

        elements.append(table)

        # Add Footer
        def footer(canvas, doc):
            canvas.saveState()
            footer_text = f"CHD Bank \u00a9 {datetime.now().year} | Page {doc.page}"
            canvas.drawString(100, 30, footer_text)
            canvas.restoreState()

        # Build the PDF
        doc.build(elements, onFirstPage=footer, onLaterPages=footer)

        return response

    return render(request,'./transaction.html',context)

# Sign-up page
def sign_up(request):
    '''The `sign_up` function handles user registration by capturing user input, checking for existing
    usernames, creating a new user account, and redirecting to the dashboard upon successful
    registration.
    
    Parameters
    ----------
    request
        The `request` parameter in the `sign_up` function is an object that represents the HTTP request
    made by the user. It contains information such as the method used (GET or POST), data submitted
    through forms, files uploaded, user session data, and more. In this context, the function is
    
    Returns
    -------
        The `sign_up` function returns either a redirect to the "Dashboard" page if the account creation is
    successful, or a render of the "signup.html" template if the request method is not POST.
    
    '''

    if request.method == 'POST':
        username = request.POST["username"]
        Email = request.POST["email"]
        password = request.POST['password']
        ac_number = request.POST['account_number']
        phone = request.POST['phone']
        ac_type = request.POST['account-type']
        gender = request.POST['Gender']
        address = request.POST['address']
        Photo = request.FILES['photo']
        pan = request.POST['pan']
        Aadhaar = request.POST['aadhaar']
        dob = request.POST['dob']
        
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username exists")
            return redirect("Sign-up")
        else:
                user = User.objects.create(username=username,password=password,)
                user_group = Group.objects.get(name="User")
                user.groups.add(user_group)
                User_reg.objects.create(user=user,account_number=ac_number,phone=phone,email=Email,account_type=ac_type,gender=gender,image=Photo,address=address,Pan=pan,aadhaar=Aadhaar,DoB=dob)
                login(request,user)
                messages.success(request,"Your account was successfully created!!")
                return redirect("Dashboard")
    
    return render(request,"./signup.html")

# DashBoard page
@user_passes_test(auth_user)
def dashboard(request):
    '''The `dashboard` function in Python checks if a user is logged in, retrieves transaction data,
    generates a pie chart based on transaction types, and renders a dashboard template with user
    information and transaction details.
    
    Parameters
    ----------
    request
        The `request` parameter in the `dashboard` function is an object that represents the HTTP request
    made by a user to access the dashboard page. It contains information about the request, such as user
    authentication status, user data, and any data sent along with the request (e.g., form data,
    
    Returns
    -------
        The `dashboard` function returns a response based on the user's authentication status. If the user
    is anonymous, an error message is displayed prompting them to log in, and they are redirected to the
    login page. If the user is authenticated, the function retrieves user profile information and
    transaction data. It then generates a pie chart based on the transaction types (withdrawal, deposit,
    transfer) and includes this
    
    '''

    if request.user.is_anonymous: 
        messages.error(request,"login in order to access Dashboard")
        return redirect("login page")
        
    else:
        user_profile = User_reg.objects.get(user=request.user)
        funds = Transactions.objects.filter(user=user_profile)[4:]
        if not Transactions.objects.filter(user=user_profile):
            context = {
                "User" : user_profile,
                "Transactions":funds,
                "chart": None,
            }
        else:
            label = ['Withdrawal','Deposit','Transfer']
            value = [
                Transactions.objects.filter(user=user_profile,transaction_type="WITHDRAW").count(),
                Transactions.objects.filter(user=user_profile,transaction_type="DEPOSIT").count(),
                Transactions.objects.filter(user=user_profile,transaction_type="TRANSFER").count()
            ]

            assert len(label) == len(value)
            assert all(isinstance(v, (int, float)) for v in value)

            plt.figure(figsize=(4, 4))
            plt.pie(value, labels=label, autopct='%1.1f%%', startangle=140, colors=["red", "green", "blue"])

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            buf.close()
            context = {
                "User" : user_profile,
                "Transactions":funds,
                "chart": image_base64,
            }


        return render(request,"./dashboard.html",context)

# Deposit page
@login_required(login_url="login page")
def deposit(request):
    '''The `deposit` function processes a POST request to add a specified amount to a user's account
    balance and create a deposit transaction record.
    
    Parameters
    ----------
    request
        The `request` parameter in the `deposit` function is an object that contains information about the
    current HTTP request. It includes details such as the method used (POST or GET), data submitted
    through the request, user session information, and more. In this context, the function is handling a
    POST request
    
    Returns
    -------
        The `deposit` function is returning a redirect response to the "Dashboard" page if the request
    method is POST and the deposit is successful. Otherwise, it returns a render response to the
    "deposit.html" template.
    
    '''

    if request.method=="POST":
        amount = float(request.POST["deposit-amount"])
        account = request.POST["account-number"]
        user = User_reg.objects.get(account_number=account)
        user.balance += decimal.Decimal(amount)
        user.save()

        Transactions.objects.create(user=user,transaction_type="DEPOSIT",amount=amount,receiptent_no="Self",receiptent=amount,about="Deposit")
        messages.success(request,f"Deposit of {amount} is Successful !!")
        return redirect("Dashboard")

    return render(request,"./deposit.html")

# Withdrawal page
@login_required(login_url="login page")
def withdrawal(request):
    """
    The `withdrawal` function in Python processes a withdrawal request, checks if the user has
    sufficient balance, updates the balance, creates a transaction record, and displays success or error
    messages accordingly.
    
    Args:
      request: The `request` parameter in the `withdrawal` function is an object that contains
    information about the current HTTP request. It includes details such as the method used (POST or
    GET), data sent in the request (like form data), user session information, and more. In this
    context, the function
    
    Returns:
      The `withdrawal` function is returning a redirect to the "Dashboard" page after processing a
    withdrawal request. If the request method is POST and the withdrawal amount is successfully deducted
    from the user's balance, a success message is displayed, and the user is redirected to the
    dashboard. If the user's balance is insufficient, an error message is displayed, and the user is
    redirected to the dashboard without processing
    """
    if request.method=="POST":
        amount = decimal.Decimal(request.POST["withdrawal-amount"])
        account = request.POST["account-number"]
        user = User_reg.objects.get(account_number = account)
        discription = request.POST["transaction-description"]

        if user.balance < amount :
            messages.error(request,"Balance Low")
            return redirect("Dashboard")
        
        else:
            user.balance -= amount
            user.save()

        Transactions.objects.create(user=user,transaction_type="WITHDRAW",amount=amount,receiptent_no="Self",receiptent=amount,about=discription)
        messages.success(request,f"Withdrawal of {amount} is Successful !!")
        return redirect("Dashboard")
    return render(request,"./Withdrawal.html")

# Transfer page
@login_required(login_url="login page")
def Transfer(request):
    '''The function `Transfer` handles transferring funds between user accounts, updating balances, and
    creating transaction records.
    
    Parameters
    ----------
    request
        The `request` parameter in the `Transfer` function is an object that contains information about the
    current HTTP request. It includes details such as the method used (POST or GET), data submitted
    through the request, user information, and more. In this context, the function is handling a POST
    request for
    
    Returns
    -------
        The Transfer function is returning a redirect to the "Dashboard" page after a successful transfer
    transaction. If there are any errors during the transfer process, it will redirect back to the
    "Transfer" page.
    
    '''
    if request.method == "POST":
        user_account = request.POST["user-account"]
        receiptent_ac = request.POST["Receiptent-account"]
        amount = decimal.Decimal(request.POST["transfer-amount"])
        discription = request.POST["transaction-description"]
        user = User_reg.objects.get(user=request.user)
        
        try:
            receiptent_transfer = User_reg.objects.get(account_number=receiptent_ac)
        except User_reg.DoesNotExist:
            messages.error(request,"User does not exist")
            return redirect("Transfers")
        
        if amount > user.balance:
            messages.error(request,"Balance insufficient")
            return redirect("Transfers")
        
        else:
            user.balance -= amount
            receiptent_transfer.balance += amount
            user.save()
            receiptent_transfer.save()
            

        Transactions.objects.create(user=user,transaction_type="TRANSFER",amount=amount,receiptent_no=receiptent_ac,receiptent=receiptent_transfer.balance,about=discription)
        messages.success(request,f"{amount} is transferred to {receiptent_transfer.user.username}")
        return redirect("Dashboard")
    return render(request,"./transfer.html")


def change_password(request):
    '''The `change_password` function in Python handles changing a user's password based on a POST request,
    validating the input and updating the password in the database if conditions are met.
    
    Parameters
    ----------
    request
        The `request` parameter in the `change_password` function represents an HTTP request that is
    received by the server. It contains information such as the method used (POST in this case), data
    submitted through the form (user name, password, confirm password), and other metadata related to
    the request.
    
    Returns
    -------
        The `change_password` function returns a redirect to the 'Change Password' page if the passwords do
    not match or if the username entered is incorrect. If the password change is successful, it returns
    a redirect to the 'login page'. If the request method is not 'POST', it renders the 'password.html'
    template.
    
    '''
    if request.method == 'POST':
        user_name = str(request.POST.get('name'))
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        
        if password != confirm_password :
            messages.error(request, "Passwords do not match")
            return redirect('Change Password')
        
        elif not User.objects.filter(username=user_name):
            messages.error(request, "Enter correct name")
            return redirect('Change Password')
        
        else:
            user = User.objects.get(username=user_name)
            user.set_password(password)
            user.save()
            messages.success(request, "Password changed successfully")
            return redirect('login page')
    
    return render(request, "./password.html")


def edit_profile(request):
    '''The `edit_profile` function updates a user's profile information based on the form data submitted
    via POST request.
    
    Parameters
    ----------
    request
        The `request` parameter in the `edit_profile` function is an object that contains information about
    the current HTTP request. It includes details such as the user making the request, any data sent in
    the request (POST data), and other metadata related to the request. In this context, the `request
    
    Returns
    -------
        The `edit_profile` function is returning a response based on the request method. If the request
    method is POST, it updates the user profile information based on the form data submitted by the user
    and then redirects to the 'User' page with a success message. If the request method is not POST, it
    renders the 'edit_profile.html' template with the user profile data.
    
    '''
    user_profile = User_reg.objects.get(user=request.user)

    

    if request.method == 'POST':
        user_name = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        Dob = request.POST['dob']
        address = request.POST['address']

        if user_name:
            user_profile.user.username = user_name
        if email:
            user_profile.email = email
        if phone: 
            user_profile.phone = phone
        if Dob:
            user_profile.DoB = Dob
        if address:
            user_profile.address = address
        
        user_profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect('User')
    
    else:
        return render(request, './edit_profile.html', {'User': user_profile})

# Log-out function 
def user_logout(request):
    '''The function `user_logout` logs out the user, displays a success message, and redirects to the login
    page.
    
    Parameters
    ----------
    request
        The `request` parameter in the `user_logout` function is typically an HttpRequest object that
    represents the current request from the user's browser. It contains information about the request,
    such as the user's session, cookies, and any data sent with the request. In this context, it is used
    to
    
    Returns
    -------
        The `user_logout` function is returning a redirect response to the 'login page'.
    
    '''
    logout(request)
    messages.success(request,"You are now logged out")
    return redirect('login page')

def handler404(request,exception):
    '''The `handler404` function in Python returns a rendered 404.html template in response to a request.
    
    Parameters
    ----------
    request
        The `request` parameter in the `handler404` function represents the HTTP request that triggered the
    404 error. It contains information about the request such as the URL, method, headers, and data.
    This parameter allows the function to access and manipulate the request data to generate an
    appropriate response for the
    exception
        The `exception` parameter in the `handler404` function is used to capture the exception that
    occurred when a 404 error is encountered. This parameter allows you to handle the specific exception
    that led to the 404 error and customize the response accordingly.
    
    Returns
    -------
        The function `handler404` is returning a rendering of the `404.html` template when a 404 error
    occurs.
    
    '''
    return render(request,'./404.html')

@csrf_exempt
def Chatbot(request):
    """
    The `Chatbot` function processes user requests and generates replies using a generative model for a
    bank chatbot in a web application.
    
    :param request: The `request` parameter in the `Chatbot` function is used to handle incoming HTTP
    requests. It allows the function to access information sent by the client, such as form data or JSON
    payloads. In the provided code snippet, the function checks if the request method is POST and then
    processes the user
    """
    """
    The function Chatbot handles user requests, processes messages, and generates replies using a
    generative model for a bank chatbot.
    
    :param request: The `request` parameter in the `Chatbot` function is used to handle incoming HTTP
    requests. It is used to access information sent by the client, such as form data or JSON payloads.
    In this code snippet, the function checks if the request method is POST and then processes the
    user's message
    :return: The code snippet you provided is a Python function named `Chatbot` that seems to be a view
    function for handling requests in a web application.
    """
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
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data['message']
        print(user_message)
        genai.configure(api_key="")
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=f"You are a Bank Manager at CHD-BANK, and you are talking to a customer who wants to know about the bank and its services. these are some things you can keep in mind {context}")
        reply = model.generate_content(user_message)
        return JsonResponse({'reply': reply.text})

def Billing_dashboard(request):
    """
    The function `Billing_dashboard` processes bill payments for a user, deducting the amount from their
    balance if sufficient and updating the transaction records accordingly.
    
    :param request: The `request` parameter in the `Billing_dashboard` function is an object that
    contains information about the current HTTP request. It includes details such as the method used
    (GET, POST, etc.), user data, and any data sent in the request (e.g., form data)
    :return: The `Billing_dashboard` function returns a rendered template for the billing dashboard
    page, which displays the bills and loans associated with the logged-in user. The bills are fetched
    from the `BillPayment` model and loans from the `Loan` model for the current user. The function
    handles POST requests for bill payments, deducts the payment amount from the user's balance if
    sufficient funds are available, creates a
    """
    if request.method == "POST":
        user = User_reg.objects.get(user=request.user)
        bill_type = request.POST.get('billType')
        Amount = decimal.Decimal(request.POST.get('amount'))  # Convert amount to decimal
        bill_no = request.POST.get('Bill_no')

        if user.balance > Amount:
            user.balance -= Amount
            user.save()
            BillPayment.objects.create(user=user, bill_type=bill_type, amount=Amount, bill_status="PAID")
            messages.success(request, "Bill Payment Successful")
            Transactions.objects.create(user=user, amount=Amount, transaction_type="BILL", receiptent_no="Self", receiptent=Amount, about=bill_type)
            return redirect('Billing Dashboard')
        else:
            messages.error(request, "Insufficient Balance")
            return redirect('Billing Dashboard')
    
    user = User_reg.objects.get(user=request.user)
    Bill = BillPayment.objects.filter(user=user)
    loan = Loan.objects.filter(user=user)

    # Calculate total monthly spending
    total_monthly_spending = Bill.aggregate(total=Sum('amount'))['total'] or 0

    # Convert Decimal values to float for JSON serialization
    spending_data = list(Bill.values('bill_type').annotate(total=Sum('amount')))
    for item in spending_data:
        item['total'] = float(item['total'])

    context = {
        "Bills": Bill,
        "User": user,
        "total_monthly_spending": total_monthly_spending,
        "spending_data": json.dumps(spending_data),
        "loans" : loan
    }
    return render(request, './billing_dashboard.html', context)

def loans(request):
    """
    The `loans` function processes a loan application submitted via a POST request, creates a new Loan
    object in the database, and redirects the user to the Billing Dashboard with a success message.
    
    :param request: The `request` parameter in the `loans` function is an object that contains
    information about the current HTTP request. It includes details such as the method used (POST or
    GET), data submitted through the request, user information, and more. In this context, the function
    is checking if the request
    :return: The `loans` function returns a response based on the HTTP request method. If the request
    method is "POST", it processes the loan application data submitted through a form, creates a new
    Loan object in the database, and then redirects the user to the 'Billing Dashboard' page with a
    success message. If the request method is not "POST", it renders the 'loan.html' template for the
    """
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        tenure = request.POST.get("tenure")
        income = request.POST.get('income')
        employment = request.POST.get('employment')
        loan_type = request.POST.get('purpose')

        # Print for debugging
        user = User_reg.objects.get(user=request.user)
        Loan.objects.create(user=user, loan_amount=amount,loan_type=loan_type,loan_tenure=tenure,employment_type=employment,loan_status="PENDING")

        # Add your loan processing logic here
        messages.success(request, "Loan application submitted successfully!")
        return redirect('Billing Dashboard')

    return render(request, './loan.html')