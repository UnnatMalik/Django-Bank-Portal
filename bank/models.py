
# imports
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# User Model
# This class defines a model for user registration with various fields such as phone number, account
# number, email, gender, account type, balance, address, image, PAN, Aadhaar, and date of birth.
class User_reg(models.Model):

    user_type = [
        ('User', 'User'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
    ]

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.IntegerField(default=0)
    account_number = models.CharField(max_length=20,unique=True)
    email = models.EmailField(max_length=30)
    gender = models.CharField(max_length=20)
    account_type = models.CharField(max_length=40)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=500,default="")
    image = models.ImageField(upload_to="User/Images",default="",null=True)
    Pan = models.CharField(max_length=50,default="")
    aadhaar = models.CharField(max_length=50,default="")
    DoB = models.CharField(max_length=20,default="")
    Role = models.CharField(max_length=100,default="User",choices=user_type)

    def __str__(self):
        return self.user.username

# Transaction Model    
# This Python class defines a model for transactions with fields like user, transaction type,
# timestamp, amount, about, recipient, and recipient number.
class Transactions(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('TRANSFER', 'Transfer'),
        ('LOAN', 'Loan'),
        ('BILL', 'Bill Payment'),
    ]

    user = models.ForeignKey(User_reg,on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20,choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(default=timezone.now())
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    about = models.CharField(max_length=100)
    receiptent = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    receiptent_no = models.CharField(max_length=30, default="",null=True)

    def __str__(self):
        return self.user.user.username

    
class Loan(models.Model):
    LOAN_TYPES = [
        ('HOME_LOAN', 'Home Loan'),
        ('PERSONAL_LOAN', 'Personal Loan'),
        ('EDUCATION_LOAN', 'Education Loan'),
        ('CAR_LOAN', 'Car Loan'),
        ('GOLD_LOAN', 'Gold loan'),
        ('OTHERS', 'Others')
    ]
    loan_status = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    user = models.ForeignKey(User_reg,on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50,choices=LOAN_TYPES)
    loan_tenure = models.IntegerField(default=1)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_status = models.CharField(max_length=20,choices=loan_status,default='PENDING')
    employment_type = models.CharField(max_length=90,default="")
    timestamp = models.DateTimeField(default=timezone.now())
    def __str__(self):
        return self.user.account_number + '-' + self.loan_type
    
    def Loan_count(self):
        laon = int(Loan.objects.filter(loan_status="PENDING").count())
        return laon

class BillPayment(models.Model):
    BILL_TYPES = (
        ('Electricity', 'Electricity'),
        ('Water', 'Water'),
        ('Internet', 'Internet'),
        ('Rent', 'Rent'),
        ('Other', 'Other'),
    )

    BILL_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    )
    
    user = models.ForeignKey(User_reg, on_delete=models.CASCADE)
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    bill_status = models.CharField(max_length=20, choices=BILL_STATUS, default='PENDING')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.user.username + '-' + self.bill_type

# Support Model    
# This Python class defines a model called Supports with fields for name, email, and issue.
class Supports(models.Model):

    SUPPORT_STATUS = [
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed')
    ]

    name = models.CharField(max_length=20,default="")
    email = models.EmailField(max_length=40)
    issue = models.CharField(max_length=300,default="")
    timestamp = models.DateTimeField(default=timezone.now())
    support_status = models.CharField(max_length=20,default="PENDING",choices=SUPPORT_STATUS)
    
    def __str__(self):
        return self.name