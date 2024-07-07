from django import forms
from bitlyapp.models import Accordance


class AccordanceForm(forms.ModelForm):
    """
    Форма создание короткой ссылки с возможностью задать кастомную ссылку
    """
    custom_url = forms.CharField(label='Custom url (optional)', help_text="Example: mysuperurl", max_length=100, required=False)

    class Meta:
        model = Accordance
        fields = ['full_url', 'custom_url']
        widgets = {
            'full_url': forms.URLInput(attrs={'initial': 'https://', 'max_length': 300, 'class': 'wide-input'}),
        }
        error_messages = {
            'full_url': {'required': 'Please enter your full url'},
        }


    def clean_full_url(self):
        full_url = self.cleaned_data.get('full_url')

        # проверка на существование сокращения полной ссылки
        if Accordance.objects.filter(full_url=full_url).exists():
            raise forms.ValidationError("There is already a short link for this URL")

        # Проверка доступности URL
        import requests
        try:
            response = requests.get(full_url)
            if response.status_code != 200:
                raise forms.ValidationError("The URL is not available.")
        except requests.RequestException:
            raise forms.ValidationError("The URL is not available.")

        return full_url