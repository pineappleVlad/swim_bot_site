from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Training, Child, Trainers, BalanceOperations
from .forms import TrainingForm, TrainersForm, ChildForm, UpdateBalanceForm, TrainerDeleteForm, ChildDeleteForm


def home_page(request):
    trainings = Training.objects.all().order_by('-date')
    context = {'trainings': trainings}
    return render(request, 'home_page.html', context)

def add_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_page')
    else:
        form = TrainingForm()
    trainers = Trainers.objects.all()
    children = Child.objects.all()
    return render(request, 'add_training.html', {'form': form, 'trainers': trainers, 'children': children})

def delete_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    if request.method == 'POST':
        training.delete()
    return redirect('home_page')

def update_training_status(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    if request.method == 'POST':
        if training.training_status == '1':
            training.training_status = '2'
        elif training.training_status == '2':
            training.training_status = '1'
        training.save()
    return redirect(reverse('home_page'))

def edit_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    children = Child.objects.all()
    trainers = Trainers.objects.all()
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            return redirect('home_page')
    else:
        form = TrainingForm(instance=training)
    return render(request, 'edit_training.html', {'form': form, 'trainers': trainers, 'children': children, 'training': training})


def add_trainer(request):
    if request.method == 'POST':
        form = TrainersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_page')
    else:
        form = TrainersForm()
    return render(request, 'add_trainer.html', {'form': form})

def add_child(request):
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_page')
    else:
        form = ChildForm()
    return render(request, 'add_child.html', {'form': form})

def update_balance(request):
    if request.method == 'POST':
        form = UpdateBalanceForm(request.POST)
        if form.is_valid():
            child = form.cleaned_data['child']
            new_balance = form.cleaned_data['new_balance']
            child.paid_training_count = new_balance
            child.save()
            return redirect('home_page')
    else:
         form = UpdateBalanceForm()
    return render(request, 'update_balance.html', {'form': form})

def trainer_delete(request):
    if request.method == 'POST':
        form = TrainerDeleteForm(request.POST)
        if form.is_valid():
            trainer = form.cleaned_data['trainer']
            trainer.delete()
            return redirect('home_page')
    else:
        form = TrainerDeleteForm()
    return render(request, 'trainer_delete.html', {'form': form})

def child_delete(request):
    if request.method == 'POST':
        form = ChildDeleteForm(request.POST)
        if form.is_valid():
            child = form.cleaned_data['child']
            child.delete()
            return redirect('home_page')
    else:
        form = ChildDeleteForm()
    return render(request, 'child_delete.html', {'form':form})

def balance_operations(request):
    operations = BalanceOperations.objects.all()
    context = {'operations': operations}
    return render(request, 'balance_operations.html', context)

def delete_balance_operation(request, operation_id):
    operation = get_object_or_404(BalanceOperations, pk=operation_id)
    if request.method == 'POST':
        operation.delete()
        return redirect('balance_operations')
    return render(request, 'delete_balance_operation.html', {'operation': operation})

def clear_balance_history(request):
    if request.method == 'POST':
        BalanceOperations.objects.all().delete()
        return redirect('balance_operations')
    return render(request, 'clear_balance_history.html')
