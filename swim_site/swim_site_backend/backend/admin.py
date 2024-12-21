from django.contrib import admin

from .models import Training, Child, Trainers

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'pool_type')

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'paid_training_count')

@admin.register(Trainers)
class TrainersAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'info')