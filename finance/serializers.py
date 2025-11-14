from rest_framework import serializers
from .models import Category, Transaction, Budget


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories — excludes user, which is auto-assigned."""
    class Meta:
        model = Category
        fields = ['id', 'name']  # only include fields your frontend uses


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions — excludes user."""
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Transaction
        fields = ['id', 'date', 'amount', 'category', 'category_name', 'description']
        read_only_fields = ['category_name']


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for budgets — excludes user, which is set automatically."""
    class Meta:
        model = Budget
        fields = ['id', 'month', 'amount']  # only include these fields
