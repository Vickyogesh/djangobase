
from cookbook.models import TransactionTable


def get_TransactionID():
    # Queries 3 tables: cookbook_recipe, cookbook_ingredient,
    # and cookbook_food.
    return list(TransactionTable.objects.prefetch_related('Transaction_id'))