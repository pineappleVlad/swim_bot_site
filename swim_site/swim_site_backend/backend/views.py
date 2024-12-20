import datetime

import openpyxl
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import xlrd
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Training, Child, Trainers, BalanceOperations
from .forms import TrainingForm, TrainersForm, ChildForm, UpdateBalanceForm, TrainerDeleteForm, ChildDeleteForm, TrainerInfoUpdateForm, ChildInfoUpdateForm


def home_page(request):
    sort_by = request.GET.get('sort', '-date')
    trainers = Trainers.objects.all()
    selected_trainer = request.session.get('selected_trainer')

    if request.method == 'GET':
        trainer_id = request.GET.get('trainer')

        if trainer_id == "":
            request.session.pop('selected_trainer', None)
            return redirect('home_page')

        if trainer_id is not None:
            request.session['selected_trainer'] = trainer_id
            selected_trainer = trainer_id


    request.session['sort_by'] = sort_by

    trainings = Training.objects.all().order_by(sort_by)
    trainings_open = Training.objects.all().order_by()

    if selected_trainer:
        trainings = trainings.filter(trainer_id=selected_trainer)

    context = {'trainings': trainings, 'trainers': trainers, 'selected_trainer': selected_trainer,
               'trainings_open': trainings_open}
    return render(request, 'home_page.html', context)


def add_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        delete_inactive_childs(request)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                return render(request, 'add_training.html', {'form': form, 'message': 'Training already exists.'})
            children_ids = form.cleaned_data.get('children')
            children = Child.objects.filter(id__in=children_ids).order_by('name')
            for child in children:
                child.paid_training_count -= 1
                child.last_balance_update = timezone.now()
                try:
                    child.save()
                except IntegrityError:
                    return render(request, 'add_training.html', {'form': form, 'message': 'Training already exists.'})
            # Создание расписания по шаблону на месяц вперед
            if 'create_schedule' in request.POST:
                start_date_str = request.POST.get('start_date')
                start_date = timezone.datetime.strptime(start_date_str, '%d-%m-%Y')
                for i in range(1, 4):  # Создать расписание на 4 недели (можете изменить на нужное количество)
                    new_training_date = start_date + datetime.timedelta(weeks=i)
                    new_training = form.instance  # Создаем копию тренировки, сохраненной в форме
                    new_training.pk = None  # Сбрасываем ID, чтобы создать новую запись
                    new_training.date = new_training_date
                    try:
                        new_training.save()
                    except IntegrityError:
                        return render(request, 'add_training.html', {'form': form, 'message': 'Training already exists.'})
            return redirect('home_page')
    else:
        form = TrainingForm()
    trainers = Trainers.objects.all().order_by('name')
    children = Child.objects.all().order_by('name')
    return render(request, 'add_training.html', {'form': form, 'trainers': trainers, 'children': children})

def delete_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    if request.method == 'POST':
        children = training.children.all()
        if training.training_status == '1':
            for child in children:
                child.paid_training_count += 1
                child.last_balance_update = timezone.now()
                try:
                    child.save()
                except IntegrityError:
                    return redirect('home_page')
        training.delete()
    return redirect('home_page')

def update_training_status(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    if request.method == 'POST':
        if training.training_status == '1':
            training.training_status = '2'
        elif training.training_status == '2':
            training.training_status = '1'
        try:
            training.save()
        except IntegrityError:
            return redirect(reverse('home_page'))
    return redirect(reverse('home_page'))


def edit_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    children = Child.objects.all().order_by('name')
    trainers = Trainers.objects.all().order_by('name')

    initial_children = list(training.children.all())

    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            try:
                updated_training = form.save()
            except IntegrityError:
                return redirect('home_page')
            updated_children = list(updated_training.children.all())

            for child in initial_children:
                if child not in updated_children:
                    child.paid_training_count += 1
                    child.last_balance_update = timezone.now()
                    try:
                        child.save()
                    except IntegrityError:
                        return redirect('home_page')

            for child in updated_children:
                if child not in initial_children:
                    child.paid_training_count -= 1
                    child.last_balance_update = timezone.now()
                    try:
                        child.save()
                    except IntegrityError:
                        return redirect('home_page')

            updated_training.save()
            return redirect('home_page')
    else:
        form = TrainingForm(instance=training)
    return render(request, 'edit_training.html',
                  {'form': form, 'trainers': trainers, 'children': children, 'training': training})


def add_trainer(request):
    if request.method == 'POST':
        form = TrainersForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                return redirect('home_page')
            return redirect('home_page')
    else:
        form = TrainersForm()
    return render(request, 'add_trainer.html', {'form': form})

def add_child_list(request):
    if request.method == 'POST':
        try:
            form = ChildForm(request.POST)
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                if uploaded_file.name.endswith('.xls'):
                    workbook = xlrd.open_workbook(file_contents=uploaded_file.read())
                    worksheet = workbook.sheet_by_index(0)
                    for row_num in range(1, worksheet.nrows):
                        row = worksheet.row_values(row_num)
                        name = row[0]
                        paid_training_count = int(row[1])
                        last_balance_update = timezone.now()
                        try:
                            Child.objects.create(name=name, paid_training_count=paid_training_count, last_balance_update=last_balance_update)
                        except IntegrityError:
                            continue
                elif uploaded_file.name.endswith('.xlsx'):
                    workbook = openpyxl.load_workbook(uploaded_file)
                    worksheet = workbook.active
                    for row in worksheet.iter_rows(min_row=2, values_only=True):
                        name = row[0]
                        paid_training_count = row[1]
                        last_balance_update = timezone.now()
                        try:
                            Child.objects.create(name=name, paid_training_count=paid_training_count, last_balance_update=last_balance_update)
                        except IntegrityError:
                            continue
                else:
                    raise ValidationError('Файл должен быть формата .xls или .xlsx')
                return redirect('home_page')
            elif form.is_valid():
                try:
                    form.save()
                except Exception:
                    return redirect('home_page')
                return redirect('home_page')
        except IntegrityError:
            return redirect('home_page')
    else:
        form = ChildForm()
    return render(request, 'add_child_list.html', {'form': form})


def add_child(request):
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                return redirect('home_page')
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
            child.last_balance_update = timezone.now()
            try:
                child.save()
            except IntegrityError:
                return redirect('home_page')
            return redirect('home_page')
    else:
         form = UpdateBalanceForm()
    return render(request, 'update_balance.html', {'form': form})

def trainer_delete(request):
    if request.method == 'POST':
        form = TrainerDeleteForm(request.POST)
        if form.is_valid():
            trainer = form.cleaned_data['trainer']
            try:
                trainer.delete()
            except Exception:
                return redirect('home_page')
            return redirect('home_page')
    else:
        form = TrainerDeleteForm()
    return render(request, 'trainer_delete.html', {'form': form})

def child_delete(request):
    if request.method == 'POST':
        form = ChildDeleteForm(request.POST)
        if form.is_valid():
            child = form.cleaned_data['child']
            try:
                child.delete()
            except Exception:
                return redirect('home_page')
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
        try:
            operation.delete()
        except Exception:
            return redirect('balance_operations')
        return redirect('balance_operations')
    return render(request, 'delete_balance_operation.html', {'operation': operation})

def clear_balance_history(request):
    if request.method == 'POST':
        try:
            BalanceOperations.objects.all().delete()
        except Exception:
            return redirect('balance_operations')
        return redirect('balance_operations')
    return render(request, 'clear_balance_history.html')


def update_child_info(request):
    if request.method == 'POST':
        form = ChildInfoUpdateForm(request.POST)
        if form.is_valid():
            child = form.cleaned_data['child']
            new_name = form.cleaned_data['new_name']
            child.name = new_name
            try:
                child.save()
            except Exception:
                return redirect('home_page')
            return redirect('home_page')
    else:
        form = ChildInfoUpdateForm()
    return render(request, 'update_child_info.html', {'form': form})


def update_trainer_info(request):
    if request.method == 'POST':
        form = TrainerInfoUpdateForm(request.POST)
        if form.is_valid():
            trainer = form.cleaned_data['trainer']
            new_name = form.cleaned_data['new_name']
            new_club = form.cleaned_data['new_club']
            if new_name:
                trainer.name = new_name
            if new_club:
                trainer.club = new_club
            try:
                trainer.save()
            except IntegrityError:
                return redirect('home_page')
            return redirect('home_page')
    else:
        form = TrainerInfoUpdateForm()
    return render(request, 'update_trainer_info.html', {'form': form})

def password_block(request):
    if request.method == 'POST':
        password = request.POST['password']
        if password == 'BrightFit25m':
            return redirect('home_page')
        else:
            return render(request, 'password_block.html', {'error_message': 'Неверный пароль. Попробуйте еще раз.'})
    else:
        return render(request, 'password_block.html')



def delete_inactive_childs(request):
    current_date = timezone.now()
    children = Child.objects.all()
    for child in children:
        last_update_date = child.last_balance_update
        days_difference = (current_date.date() - last_update_date).days
        if days_difference >= 100:
            child.delete()
    return redirect(reverse('child_delete'))


def duplicate_training(request, training_id):
    original_training = get_object_or_404(Training, id=training_id)

    new_training = Training.objects.create(
        date=original_training.date,
        time=original_training.time,
        pool_type=original_training.pool_type,
        trainer=original_training.trainer,
        training_status=original_training.training_status
    )
    new_training.children.set(original_training.children.all())

    return redirect(reverse('home_page'))


def close_expired_trainings(request):
    trainings = Training.objects.filter(date__lt=timezone.now(), training_status='1')
    for training in trainings:
        training.training_status = '2'
        training.save()
    return redirect(reverse('home_page'))