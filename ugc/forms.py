from django import forms
from .models import Profile, Vitamin, Training, Nutrition

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'external_id',
            'username',
            'name',
            'program_type',
            'gender',
            'age',
            'weight'
        )


class VitaminDataForm(forms.ModelForm):
    class Meta:
        model = Vitamin
        fields = (
            'id',
            'profile',
            'phys_loads',
            'stress',
            'weakness',
            'sun_frequency'
        )
        widgets = {
            'phys_loads': forms.TextInput,
        }


class NutritionDataForm(forms.ModelForm):
    class Meta:
        model = Nutrition
        fields = (
            'id',
            'profile',
            'nutrition_goal',
            'how_much',
            'if_meat',
            'height',
            'phys_loads'
        )
        widgets = {
            'phys_loads': forms.TextInput,
        }
