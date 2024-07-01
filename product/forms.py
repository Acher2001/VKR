from django import forms
from .models import Category

class CategoriesForm(forms.Form):
    choices = tuple(enumerate([cat.name for cat in Category.objects.all()], 1))
    Categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          choices=choices)
