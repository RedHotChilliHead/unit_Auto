from .models import Accordance
from rest_framework import serializers
import requests


class AccordanceSerializer(serializers.Serializer):
    full_url = serializers.CharField()
    short_url = serializers.CharField(required=False)

    def validate_full_url(self, value):
        # проверка на существование сокращения полной ссылки
        try:
            obj = Accordance.objects.get(full_url=value)
            if obj:
                raise serializers.ValidationError("There is already a short link for this URL")
        except Accordance.DoesNotExist:
            pass
        # валидация URL
        try:
            response = requests.get(value)
            if response.status_code != 200:
                raise serializers.ValidationError("The URL is not available.")
        except requests.RequestException:
            raise serializers.ValidationError("The URL is not available.")
        return value

    def create(self, validated_data):
        full_url = validated_data.get('full_url')
        custom_url = self.context['request'].data.get('custom_url', None)
        if custom_url:
            # проверка на существование короткой ссылки с таким же custom_url
            try:
                obj = Accordance.objects.get(short_url="http://127.0.0.1:8000/bitly/" + custom_url + "/")
                if obj:
                    # {"full_url": "https://docs.djangoproject.com/en/5.0/ref/class-based-views/base/", "custom_url": "mycustomurl"}
                    raise serializers.ValidationError("Such a short link already exists")
            except Accordance.DoesNotExist:
                pass
            short_url = f"http://127.0.0.1:8000/bitly/{custom_url}/"
        else:
            last = Accordance.objects.last()
            next_pk = (last.pk + 1) if last else 1
            short_url = f"http://127.0.0.1:8000/bitly/{next_pk}/"
        accordance = Accordance.objects.create(full_url=full_url, short_url=short_url)
        return accordance