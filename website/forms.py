from django import forms
from captcha.fields import CaptchaField

from .models import ContactSubmission, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    # Honeypot — hidden from users; bots often fill it.
    website_url = forms.CharField(required=False, widget=forms.HiddenInput)
    captcha = CaptchaField(label='Security check')

    class Meta:
        model = ContactSubmission
        fields = ('name', 'email', 'phone', 'subject', 'details')
        widgets = {
            'name': forms.TextInput(attrs={'id': 'contact_name'}),
            'email': forms.EmailInput(attrs={'id': 'contact_email'}),
            'phone': forms.TextInput(attrs={'id': 'contact_phone'}),
            'subject': forms.TextInput(attrs={'id': 'subject'}),
            'details': forms.Textarea(attrs={'id': 'details', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional = {'phone', 'website_url'}
        for name, field in self.fields.items():
            if name not in optional and name != 'captcha':
                field.required = True
            elif name == 'phone':
                field.required = False
        self.fields['captcha'].widget.attrs.update({
            'class': 'contact-form__captcha-input',
            'autocomplete': 'off',
            'inputmode': 'numeric',
        })

    def clean_website_url(self):
        if self.cleaned_data.get('website_url'):
            raise forms.ValidationError('Invalid submission.')
        return ''


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        return email
