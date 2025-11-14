# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    TransactionViewSet,
    BudgetViewSet,
    transaction_global_summary,
    budget_global_summary,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')

urlpatterns = [
    # ✅ Custom summary routes FIRST
    path('api/transactions/global-summary/', transaction_global_summary, name='transaction_global_summary'),
    path('api/budgets/global-summary/', budget_global_summary, name='budget_global_summary'),

    # 🔐 Auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🚀 Router endpoints (keep last)
    path('api/', include(router.urls)),
]
