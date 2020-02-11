from django.contrib import admin
from .forms import ProfileForm, VitaminDataForm, NutritionDataForm
from .models import Profile, Vitamin, Training, Nutrition
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'username','name','program_type','gender','age','weight')
    form = ProfileForm

@admin.register(Vitamin)
class VitaminDataAdmin(admin.ModelAdmin):
    list_display = ('id','profile','created_at', 'phys_loads',
                    'stress',
                    'weakness',
                    'sun_frequency')
    form = VitaminDataForm
   # def get_queryset(self, request):
    #    return

@admin.register(Training)
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at', 'train_goal', 'how_much', 'sport_lvl')

@admin.register(Nutrition)
class NuritionDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at', 'nutrition_goal', 'how_much', 'if_meat', 'height', 'phys_loads')
    form = NutritionDataForm
