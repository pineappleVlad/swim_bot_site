import datetime
from urllib.parse import urlencode

import openpyxl
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import xlrd
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Training, Child, Trainers, BalanceOperations
from .forms import TrainingForm, TrainersForm, ChildForm, UpdateBalanceForm, TrainerDeleteForm, ChildDeleteForm, TrainerInfoUpdateForm, ChildInfoUpdateForm


def home_page(request):
    sort_by = request.GET.get('sort', '-date')
    selected_trainer = request.GET.get('trainer', '')

    trainers = Trainers.objects.all()

    trainings = Training.objects.all().order_by(sort_by)
    trainings_open = trainings.filter(training_status='1')

    if selected_trainer:
        trainings_open = trainings_open.filter(trainer_id=selected_trainer)

    context = {
        'trainings_open': trainings_open,
        'trainers': trainers,
        'selected_trainer': selected_trainer,
        'sort_by': sort_by,
    }

    return render(request, 'home_page.html', context)


def closed_trainings_page(request):
    sort_by = request.GET.get('sort', '-date')
    selected_trainer = request.GET.get('trainer', '')

    trainers = Trainers.objects.all()

    trainings_closed = Training.objects.filter(training_status='2').order_by(sort_by)
    if selected_trainer:
        trainings_closed = trainings_closed.filter(trainer_id=selected_trainer)

    context = {
        'trainings': trainings_closed,
        'trainers': trainers,
        'selected_trainer': selected_trainer,
        'sort_by': sort_by,
    }

    return render(request, 'closed_trainings.html', context)


def add_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        delete_inactive_childs(request)
        delete_old_trainings(request)
        if form.is_valid():
            training_date = form.cleaned_data.get('date')
            training_time = form.cleaned_data.get('time')

            existing_training = Training.objects.filter(
                date=training_date,
                time=training_time,
                training_status='1'
            ).exists()


            if existing_training:
                children = Child.objects.all().order_by('name')
                return render(request, 'add_training.html', {
                    'form': form,
                    'error_message': 'Тренировка с такой датой и временем уже существует',
                    'errors': ['Тренировка с такой датой и временем уже существует'],
                    'children': children
                })
            try:
                form.save()
                children_ids = form.cleaned_data.get('children')
                children = Child.objects.filter(id__in=children_ids).order_by('name')
                for child in children:
                    child.paid_training_count -= 1
                    child.last_balance_update = timezone.now()
                    child.save()

                if 'create_schedule' in request.POST:
                    start_date_str = request.POST.get('start_date')
                    start_date = timezone.datetime.strptime(start_date_str, '%d-%m-%Y')
                    for i in range(1, 4):  # Создаем расписание на 4 недели
                        new_training_date = start_date + datetime.timedelta(weeks=i)
                        new_training = form.instance
                        new_training.pk = None
                        new_training.date = new_training_date
                        new_training.save()
            except Exception:
                return render(request, 'add_training.html', {'form': form, 'error_message': 'Ошибка'})
            return redirect('home_page')
    else:
        form = TrainingForm()
    trainers = Trainers.objects.all().order_by('name')
    children = Child.objects.all().order_by('name')
    return render(request, 'add_training.html', {'form': form, 'trainers': trainers, 'children': children})

def delete_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    query_params = request.GET.dict()
    query_params.update(request.POST.dict())
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
    return HttpResponseRedirect(f"{reverse('home_page')}?{urlencode(query_params)}")

def update_training_status(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    query_params = request.GET.dict()
    query_params.update(request.POST.dict())
    if request.method == 'POST':
        if training.training_status == '1':
            training.training_status = '2'
        elif training.training_status == '2':
            training.training_status = '1'
        try:
            training.save()
        except IntegrityError:
            return HttpResponseRedirect(f"{reverse('home_page')}?{urlencode(query_params)}")
    return HttpResponseRedirect(f"{reverse('home_page')}?{urlencode(query_params)}")


def edit_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    children = Child.objects.all().order_by('name')
    trainers = Trainers.objects.all().order_by('name')

    initial_children = list(training.children.all())

    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)

        if form.is_valid():
            # Проверка на существование тренировки с такой же датой и временем
            date = form.cleaned_data.get('date')
            time = form.cleaned_data.get('time')

            if Training.objects.filter(date=date, time=time).exclude(id=training_id).exists():
                error_message = 'Тренировка на эту дату и время уже есть'
                return render(request, 'edit_training.html', {
                    'form': form,
                    'trainers': trainers,
                    'children': children,
                    'training': training,
                    'error_message': error_message
                })

            try:
                # Сохраняем обновленную тренировку
                updated_training = form.save()
            except IntegrityError:
                error_message = 'An error occurred while saving the training.'
                return render(request, 'edit_training.html', {
                    'form': form,
                    'trainers': trainers,
                    'children': children,
                    'training': training,
                    'error_message': error_message
                })

            updated_children = list(updated_training.children.all())

            # Обновление данных о детях, которые были добавлены или удалены
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

            # Сохраняем обновленную тренировку после изменений
            updated_training.save()
            return redirect('home_page')
    else:
        form = TrainingForm(instance=training)

    return render(request, 'edit_training.html', {
        'form': form,
        'trainers': trainers,
        'children': children,
        'training': training
    })


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
            new_info = form.cleaned_data['new_info']
            if new_name:
                trainer.name = new_name
            if new_club:
                trainer.club = new_club
            if new_info:
                trainer.info = new_info
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
    return

def delete_old_trainings(request):
    current_date = timezone.now()
    # Удаляем только закрытые тренировки старше 4 месяцев (~120 дней)
    trainings = Training.objects.filter(training_status='2')
    for training in trainings:
        days_difference = (current_date.date() - training.date).days
        if days_difference >= 120:
            training.delete()
    return


def duplicate_training(request, training_id):
    original_training = get_object_or_404(Training, id=training_id)
    query_params = request.GET.dict()
    query_params.update(request.POST.dict())

    new_training = Training.objects.create(
        date=original_training.date,
        time=original_training.time,
        pool_type=original_training.pool_type,
        trainer=original_training.trainer,
        training_status=original_training.training_status
    )
    new_training.children.set(original_training.children.all())

    return HttpResponseRedirect(f"{reverse('home_page')}?{urlencode(query_params)}")


def close_expired_trainings(request):
    trainings = Training.objects.filter(date__lt=timezone.now(), training_status='1')
    query_params = request.GET.dict()
    query_params.update(request.POST.dict())
    for training in trainings:
        training.training_status = '2'
        training.save()
    return HttpResponseRedirect(f"{reverse('home_page')}?{urlencode(query_params)}")