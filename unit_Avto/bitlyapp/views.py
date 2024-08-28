from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django import forms
from .forms import AccordanceForm
from .models import Accordance
from .serializers import AccordanceSerializer
from django.views.generic.base import RedirectView


class AccordanceApiView(APIView):
    """
    Метод POST предоставляет короткую ссылку
    Пример запроса:
    POST {"full_url": "https://www.google.com"}
    Также метод POST предоставляет возможность создания кастомной ссылки, для этого необходимо добавить параметр "custom_url"
    Пример запроса на создание кастомной ссылки:
    POST {"full_url": "https://docs.python.org/3/library/datetime.html", "custom_url": "mycustomurl"}
    """

    def post(self, request: Request) -> Response:
        """
        Метод предоставления короткой ссылки и сохранение ее соответствия в базе данных
        """
        serializer = AccordanceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AccordanceCreateView(CreateView):
    """
    Создание короткой ссылки
    """
    model = Accordance
    form_class = AccordanceForm
    template_name = "bitlyapp/accordance_form.html"
    success_url = reverse_lazy('bitlyapp:accordance-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        custom_url = self.request.POST.get('custom_url', None)
        if custom_url:
            if Accordance.objects.filter(short_url=f"http://127.0.0.1:8000/{custom_url}/").exists():
                form.add_error('custom_url', forms.ValidationError("There is already a short link for this URL"))
                return self.form_invalid(form)
            else:
                short_url = f"http://127.0.0.1:8000/{custom_url}/"
        else:
            last = Accordance.objects.last()
            next_pk = (last.pk + 1) if last else 1
            short_url = f"http://127.0.0.1:8000/{next_pk}/"
        self.object.short_url = short_url
        self.object.save()
        return super().form_valid(form)

class AccordanceListView(ListView):
    """
    Представление для отображения списка ссылок
    """
    model = Accordance
    template_name = "bitlyapp/accordance_list.html"
    paginate_by = 100


class AccordanceRedirect(RedirectView):
    """
    Класс перенаправления на полную ссылку
    """
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Accordance, short_url="http://127.0.0.1:8000/" + kwargs["short_url"] + "/")
        return obj.full_url
