# your_app/tasks.py
from celery import shared_task
from django.db.models import F
from .models import AboutUsModel  # مدل مورد نظر شما

@shared_task
def increment_experience_monthly():
    # به همه رکوردها ۱ ماه اضافه می‌کند
    AboutUsModel.objects.update(work_experience_months=F('work_experience_months') + 1)