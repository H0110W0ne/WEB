import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .models import Comment, Direction, Registration

NAME_RE = re.compile(r'^[А-ЯЁA-Z][а-яёa-z]+$')
PHONE_RE = re.compile(r'^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$')
User = get_user_model()


class RegistrationForm(forms.Form):
    firstName = forms.CharField(min_length=2, max_length=20)
    lastName = forms.CharField(min_length=2, max_length=20)
    email = forms.EmailField()
    phone = forms.CharField(min_length=10, max_length=30)
    age = forms.IntegerField(min_value=10, max_value=70)
    direction = forms.ModelChoiceField(
        queryset=Direction.objects.all(),
        to_field_name='slug',
        empty_label=None,
    )
    password = forms.CharField(min_length=8, max_length=128, required=True)
    confirmPassword = forms.CharField(min_length=8, max_length=128, required=True)
    message = forms.CharField(required=False, max_length=1000)

    def clean_firstName(self):
        value = self.cleaned_data['firstName'].strip()
        if not NAME_RE.fullmatch(value):
            raise forms.ValidationError('Только буквы, первая буква заглавная, остальные строчные.')
        return value

    def clean_lastName(self):
        value = self.cleaned_data['lastName'].strip()
        if not NAME_RE.fullmatch(value):
            raise forms.ValidationError('Только буквы, первая буква заглавная, остальные строчные.')
        return value

    def clean_email(self):
        value = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username__iexact=value).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return value

    def clean_phone(self):
        value = self.cleaned_data['phone'].strip()
        if not PHONE_RE.fullmatch(value):
            raise forms.ValidationError('Введите телефон в формате +7 (999) 123-45-67.')
        return value

    def clean_message(self):
        return self.cleaned_data['message'].strip()

    def clean_password(self):
        value = self.cleaned_data['password']
        validate_password(value)
        return value

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', '')
        confirm_password = cleaned_data.get('confirmPassword', '')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirmPassword', 'Пароли не совпадают.')

        return cleaned_data

    @transaction.atomic
    def save(self):
        user = User(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName'],
        )
        user.set_password(self.cleaned_data['password'])
        user.save()

        registration = Registration.objects.create(
            user=user,
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            age=self.cleaned_data['age'],
            direction=self.cleaned_data['direction'],
            message=self.cleaned_data.get('message', ''),
        )
        return registration


class CommentForm(forms.Form):
    authorName = forms.CharField(min_length=2, max_length=60, required=False)
    text = forms.CharField(min_length=2, max_length=500)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_authorName(self):
        value = self.cleaned_data.get('authorName', '').strip()
        if self.user and getattr(self.user, 'is_authenticated', False):
            return value
        if len(value) < 2:
            raise forms.ValidationError('Укажите имя автора не короче 2 символов.')
        return value

    def clean_text(self):
        value = self.cleaned_data['text'].strip()
        if len(value) < 2:
            raise forms.ValidationError('Комментарий должен содержать минимум 2 символа.')
        return value

    def save(self):
        if self.user and getattr(self.user, 'is_authenticated', False):
            author_name = self.user.get_full_name().strip() or self.user.username
        else:
            author_name = self.cleaned_data['authorName'].strip()

        return Comment.objects.create(
            user=self.user if self.user and getattr(self.user, 'is_authenticated', False) else None,
            author_name=author_name,
            text=self.cleaned_data['text'].strip(),
        )
