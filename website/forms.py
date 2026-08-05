from django import forms
from captcha.fields import CaptchaField

from .models import ContactSubmission, NewsComment, NewsletterSubscriber
from .moderation import has_blocked_language

_CONTENT_POLICY_MSG = (
    'Your comment could not be posted because it contains improper language '
    'or hate speech. Please revise and try again.'
)


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
            'inputmode': 'text',
        })

    def clean_website_url(self):
        if self.cleaned_data.get('website_url'):
            raise forms.ValidationError('Invalid submission.')
        return ''


class NewsCommentForm(forms.ModelForm):
    website_url = forms.CharField(required=False, widget=forms.HiddenInput)
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = NewsComment
        fields = ('name', 'body')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mp-article__input',
                'placeholder': 'Your name',
                'autocomplete': 'name',
            }),
            'body': forms.Textarea(attrs={
                'class': 'mp-article__textarea',
                'rows': 4,
                'placeholder': 'Write your comment…',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['body'].required = True

    def clean_website_url(self):
        if self.cleaned_data.get('website_url'):
            raise forms.ValidationError('Invalid submission.')
        return ''

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if has_blocked_language(name):
            raise forms.ValidationError(_CONTENT_POLICY_MSG)
        return name

    def clean_body(self):
        body = (self.cleaned_data.get('body') or '').strip()
        if len(body) < 3:
            raise forms.ValidationError('Please write a longer comment.')
        if has_blocked_language(body):
            raise forms.ValidationError(_CONTENT_POLICY_MSG)
        return body


class NewsCommentEditForm(forms.Form):
    body = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'mp-article__textarea',
            'rows': 3,
            'placeholder': 'Edit your comment…',
        }),
    )

    def clean_body(self):
        body = (self.cleaned_data.get('body') or '').strip()
        if len(body) < 3:
            raise forms.ValidationError('Please write a longer comment.')
        if has_blocked_language(body):
            raise forms.ValidationError(_CONTENT_POLICY_MSG)
        return body


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        return email
