import json
from django.test import TestCase

from django.urls import reverse
import requests
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from bitlyapp.forms import AccordanceForm
from bitlyapp.models import Accordance
from bitlyapp.serializers import AccordanceSerializer


class APIAccordanceTestCase(APITestCase):
    def setUp(self):
        self.short_url = "ggl"
        self.accordance = Accordance.objects.create(full_url="https://www.google.com/",
                                                    short_url=f"http://127.0.0.1:8000/bitly/{self.short_url}/")

    def tearDown(self) -> None:
        self.accordance.delete()

    def test_accordance_post_api_view(self):
        """
        Проверка получения стандартной ссылки через API
        """
        full_url = "https://www.django-rest-framework.org/api-guide/testing/"

        response = requests.get(full_url)  # проверяем, что ссылка рабочая
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('bitlyapp:accordance'), {"full_url": full_url}, format='json')
        self.assertEqual(response.status_code, 201)  # Убеждаемся, что ответ является Created (успешное создание)
        self.assertTrue(Accordance.objects.filter(full_url=full_url).exists())  # Убеждаемся, что соответствие создано
        self.assertTrue(
            Accordance.objects.get(full_url=full_url).short_url)  # Убеждаемся, что короткая ссылка существует

    def test_accordance_custom_url_api_view(self):
        """
        Проверка получения кастомной ссылки через API
        """
        post_data = {
            "full_url": "https://clck.ru/",
            "custom_url": "clicker"
        }
        response = self.client.post(reverse('bitlyapp:accordance'), json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Accordance.objects.filter(full_url=post_data['full_url']).exists())  # Убеждаемся, что соответствие создано
        accordance = Accordance.objects.get(full_url=post_data['full_url'])
        expected_data = "http://127.0.0.1:8000/bitly/" + post_data['custom_url'] + "/"
        self.assertEqual(accordance.short_url, expected_data)  # Убеждаемся, что кастомная ссылка создана правильно

    def test_accordance_validation_api_view(self):
        """
        Проверка валидации сериализатора
        """
        # проверяем, что валидация не пройдет, если дадим не рабочую ссылку
        invalid_url = "https://clsssfffck.ru/"
        invalid_response = self.client.post(reverse('bitlyapp:accordance'), {"full_url": invalid_url}, format='json')
        self.assertEqual(invalid_response.status_code, 400)  # Bad Request
        invalid_dict = json.loads(invalid_response.content)
        self.assertEqual(invalid_dict, {"full_url": ["The URL is not available."]})

        # проверяем, что будет выброшено правильное исключение
        serializer = AccordanceSerializer(data={"full_url": invalid_url})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        # проверяем, что валидация не пройдет, если будет дана уже существующая полная ссылка
        double_url = self.accordance.full_url
        response = self.client.post(reverse('bitlyapp:accordance'), {"full_url": double_url}, format='json')
        self.assertEqual(response.status_code, 400)  # Bad Request
        invalid_dict = json.loads(response.content)
        self.assertEqual(invalid_dict, {"full_url": ["There is already a short link for this URL"]})

        # проверяем, что будет выброшено правильное исключение
        serializer = AccordanceSerializer(data={"full_url": double_url})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        # проверяем, что валидация не пройдет, если будет дан уже существующий custom_url
        post_data = {
            "full_url": "https://clck.ru/",
            "custom_url": self.short_url
        }
        response = self.client.post(reverse('bitlyapp:accordance'), json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad Request
        invalid_list = json.loads(response.content)
        expected_list = ["Such a short link already exists"]
        self.assertEqual(invalid_list, expected_list)


class AccordanceTestCase(TestCase):
    def setUp(self):
        self.short_url = "ggl"
        self.accordance = Accordance.objects.create(full_url="https://www.google.com/",
                                                    short_url=f"http://127.0.0.1:8000/bitly/{self.short_url}/")

    def tearDown(self) -> None:
        self.accordance.delete()

    def test_accordance_redirect_view(self):
        """
        Проверка редиректа с короткой на исходную ссылку
        """
        response = self.client.get(self.accordance.short_url)
        self.assertEqual(response.status_code, 301)
        # fetch_redirect_response = False для проверки перенаправления на внешний URL
        self.assertRedirects(response, self.accordance.full_url, status_code=301, fetch_redirect_response=False)
        response = requests.get(response.url)
        self.assertEqual(response.status_code, 200)

    def test_accordance_get_view(self):
        """
        Проверка отображения приглашения для создания короткой ссылки
        """
        response = self.client.get(reverse('bitlyapp:accordance-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create a link', html=True)
        self.assertContains(response, 'List of links', html=True)
        self.assertContains(response, 'API', html=True)
        self.assertContains(response, 'Full url:', html=True)
        self.assertContains(response, 'Custom url (optional):', html=True)
        self.assertContains(response, 'Example: mysuperurl', html=True)

    def test_accordance_create_view(self):
        """
        Проверка получения стандартной ссылки через UI
        """
        full_url = "https://www.django-rest-framework.org/api-guide/testing/"

        response = requests.get(full_url)  # проверяем, что ссылка рабочая
        self.assertEqual(response.status_code, 200)

        # считаем будущий индекс
        last = Accordance.objects.last()
        next_pk = (last.pk + 1) if last else 1

        post_data = {"full_url": "https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context"}
        response = self.client.post(reverse('bitlyapp:accordance-create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bitlyapp:accordance-list'))
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post_data['full_url'])

        self.assertContains(response, f"http://127.0.0.1:8000/bitly/{next_pk}/")
        self.assertTrue(
            Accordance.objects.filter(full_url=post_data['full_url']).exists())  # Убеждаемся, что соответствие создано
        self.assertEqual(f"http://127.0.0.1:8000/bitly/{next_pk}/",
                         Accordance.objects.get(
                             full_url=post_data['full_url']).short_url)  # Убеждаемся, что короткая ссылка существует

    def test_accordance_create_custom_view(self):
        """
        Проверка получения кастомной ссылки через UI
        """
        full_url = "https://www.django-rest-framework.org/api-guide/testing/"

        response = requests.get(full_url)  # проверяем, что ссылка рабочая
        self.assertEqual(response.status_code, 200)

        post_data = {
            "full_url": "https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context",
            "custom_url": "test_custom_url"}
        response = self.client.post(reverse('bitlyapp:accordance-create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bitlyapp:accordance-list'))
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post_data['full_url'])
        self.assertContains(response, f"http://127.0.0.1:8000/bitly/{post_data['custom_url']}/")
        self.assertTrue(
            Accordance.objects.filter(full_url=post_data['full_url']).exists())  # Убеждаемся, что соответствие создано
        self.assertEqual(f"http://127.0.0.1:8000/bitly/{post_data['custom_url']}/",
                         Accordance.objects.get(
                             full_url=post_data['full_url']).short_url)  # Убеждаемся, что короткая ссылка существует


    def test_accordance_validation_view(self):
        """
        Проверка валидации формы
        """
        # проверяем, что валидация не пройдет, если не дадим полную ссылку
        invalid_response = self.client.post(reverse('bitlyapp:accordance-create'))
        self.assertContains(invalid_response, "Please enter your full url")

        # проверяем, что валидация не пройдет, если дадим не рабочую ссылку
        invalid_url = "https://clsssfffck.ru/"
        invalid_response = self.client.post(reverse('bitlyapp:accordance-create'), {"full_url": invalid_url})
        self.assertContains(invalid_response, "The URL is not available.")
        # проверяем, что будет выброшено правильное исключение
        form = AccordanceForm(data={"full_url": invalid_url})
        self.assertFalse(form.is_valid())
        self.assertIn("The URL is not available.", form.errors['full_url'])

        # проверяем, что валидация не пройдет, если дадим повторяющуюся полную ссылку
        double_url = self.accordance.full_url
        invalid_response = self.client.post(reverse('bitlyapp:accordance-create'), {"full_url": double_url})
        self.assertContains(invalid_response, "There is already a short link for this URL")
        # проверяем, что будет выброшено правильное исключение
        form = AccordanceForm(data={"full_url": double_url})
        self.assertFalse(form.is_valid())
        self.assertIn("There is already a short link for this URL", form.errors['full_url'])

        # проверяем, что валидация не пройдет, если дадим повторяющуюся кастомную ссылку
        double_custom_url = self.short_url
        invalid_response = self.client.post(reverse('bitlyapp:accordance-create'),
                                            {"full_url": "https://www.django-rest-framework.org/",
                                             "custom_url": double_custom_url})
        self.assertContains(invalid_response, "There is already a short link for this URL")



