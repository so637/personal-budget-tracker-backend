from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
import datetime

from .models import Category, Transaction, Budget
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer

# -----------------------------
# Category View
# -----------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -----------------------------
# Transaction View
# -----------------------------
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')
        if amount_min:
            qs = qs.filter(amount__gte=amount_min)
        if amount_max:
            qs = qs.filter(amount__lte=amount_max)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__id=category)
        return qs.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        user = request.user
        summary = (
            Transaction.objects.filter(user=user)
            .values('category__name')
            .annotate(total_spent=Sum('amount'))
            .order_by('-total_spent')
        )
        return Response(summary)


# -----------------------------
# Budget View
# -----------------------------
class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = Transaction.objects.filter(user=request.user)
        month = request.query_params.get('month')
        if month:
            if len(month) == 7:
                start = parse_date(f"{month}-01")
            else:
                start = parse_date(month)
            if start:
                end_month = (start.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
                qs = qs.filter(date__gte=start, date__lt=end_month)
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category__id=category)
        summary = (
            qs.values('category__id', 'category__name')
            .annotate(total_spent=Sum('amount'))
            .order_by('-total_spent')
        )
        return Response(list(summary))


# -----------------------------
# ✅ Global Summary for Dashboard
# -----------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def transaction_global_summary(request):
    user = request.user
    total_income = (
        Transaction.objects.filter(user=user, type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    )
    total_expense = (
        Transaction.objects.filter(user=user, type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    )
    balance = total_income - total_expense
    data = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def budget_global_summary(request):
    user = request.user
    total_budget = Budget.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = Transaction.objects.filter(user=user, type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    remaining = total_budget - total_spent
    data = {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": remaining,
    }
    return Response(data)


# -----------------------------
# 🔹 Temporary endpoint to create a test user
# -----------------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_test_user(request):
    """
    Temporary endpoint for creating a superuser/test user on Render (no shell access).
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password)
    return Response({"message": f"User {username} created successfully!"}, status=201)
