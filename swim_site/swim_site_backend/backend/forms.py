from django import forms
from .models import Training, Trainers, Child

class TrainingForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.DateInput(format='%d-%m-%Y'))
    time = forms.TimeField(input_formats=['%H:%M'])
    children = forms.ModelMultipleChoiceField(queryset=Child.objects.all(), required=False)
    class Meta:
        model = Training
        fields = '__all__'


class TrainersForm(forms.ModelForm):
    class Meta:
        model = Trainers
        fields = '__all__'

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = '__all__'

class UpdateBalanceForm(forms.Form):
    child = forms.ModelChoiceField(queryset=Child.objects.all().order_by('name'), label='Выберите ребенка')
    new_balance = forms.IntegerField(label='Новый баланс')

class TrainerDeleteForm(forms.Form):
    trainer = forms.ModelChoiceField(queryset=Trainers.objects.all().order_by('name'), label='Выберите тренера')

class ChildDeleteForm(forms.Form):
    child = forms.ModelChoiceField(queryset=Child.objects.all().order_by('name'), label='Выберите ребенка')

class ChildInfoUpdateForm(forms.Form):
    child = forms.ModelChoiceField(queryset=Child.objects.all().order_by('name'), label='Выберите ребенка')
    new_name = forms.CharField(label='Новое имя')

class TrainerInfoUpdateForm(forms.Form):
    trainer = forms.ModelChoiceField(queryset=Trainers.objects.all().order_by('name'), label='Выберите тренера')
    new_name = forms.CharField(label='Новое имя', required=False)
    new_club = forms.CharField(label='Новый клуб', required=False)
    new_info = forms.CharField(
        required=False,
        label="Новая информация о тренере",
        widget=forms.Textarea(attrs={"rows": 8, "class": "form-control"})
    )
