import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unit_Avto.settings')

import django
django.setup()

from django.urls import reverse
from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def read_endpoint(self):
        self.client.get(reverse("bitlyapp:accordance-create"))

    @task(2)
    def another_task(self):
        self.client.get(reverse("bitlyapp:accordance-list"))

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]  # Список задач, которые должен выполнять пользователь, UserBehavior - это класс TaskSet
    wait_time = between(1, 3)  # время ожидания между выполнением задач

# locust -f locust.py - запуск locust
# Перейти в браузере по адресу http://localhost:8089.
# В веб-интерфейсе введите количество пользователей (Number of users to simulate) и скорость их появления (Spawn rate),
# затем нажмите кнопку Start swarming.