from django.contrib import admin
from django.urls import path

from .views import home_page, add_training, delete_training, update_training_status, edit_training, add_trainer, \
    add_child, update_balance, trainer_delete, child_delete, balance_operations, delete_balance_operation, \
    clear_balance_history

urlpatterns = [
    path('', home_page, name='home_page'),
    path('add_training/', add_training, name='add_training'),
    path('delete_training/<int:training_id>', delete_training, name='delete_training'),
    path('update_training_status/<int:training_id>', update_training_status, name='update_training_status'),
    path('edit_training/<int:training_id>/', edit_training, name='edit_training'),
    path('add_trainer/', add_trainer, name='add_trainer'),
    path('add_child/', add_child, name='add_child'),
    path('update_balance/', update_balance, name='update_balance'),
    path('trainer_delete/', trainer_delete, name='trainer_delete'),
    path('child_delete/', child_delete, name='child_delete'),
    path('balance_operations/', balance_operations, name='balance_operations'),
    path('delete_balance_operation/<int:operation_id>/', delete_balance_operation, name='delete_balance_operation'),
    path('clear_balance_history/', clear_balance_history, name='clear_balance_history'),
]