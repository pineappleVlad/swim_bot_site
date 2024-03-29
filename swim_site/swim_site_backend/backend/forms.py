from django import forms
from .models import Training, Trainers, Child

class TrainingForm(forms.ModelForm):
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
    child = forms.ModelChoiceField(queryset=Child.objects.all(), label='Выберите ребенка')
    new_balance = forms.IntegerField(label='Новый баланс')

class TrainerDeleteForm(forms.Form):
    trainer = forms.ModelChoiceField(queryset=Trainers.objects.all(), label='Выберите тренера')

class ChildDeleteForm(forms.Form):
    child = forms.ModelChoiceField(queryset=Child.objects.all(), label='Выберите ребенка')
