from django.contrib import admin
from .models import expense,income,token
# Register your models here.

admin.site.register(expense)
admin.site.register(income)
admin.site.register(token)
