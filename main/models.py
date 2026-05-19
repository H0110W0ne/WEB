from django.conf import settings
from django.db import models


class Direction(models.Model):
    slug = models.SlugField('Код направления', max_length=30, unique=True)
    name = models.CharField('Название', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'
        ordering = ['name']

    def __str__(self):
        return self.name


class Registration(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='training_registration',
        verbose_name='Пользователь',
        null=True,
        blank=True,
    )
    first_name = models.CharField('Имя', max_length=20)
    last_name = models.CharField('Фамилия', max_length=20)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=30)
    age = models.PositiveSmallIntegerField('Возраст')
    direction = models.ForeignKey(
        Direction,
        on_delete=models.PROTECT,
        related_name='registrations',
        verbose_name='Направление',
    )
    message = models.TextField('Комментарий', blank=True)
    telegram_sent = models.BooleanField('Отправлено в Telegram', default=False)
    telegram_error = models.TextField('Ошибка Telegram', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Регистрация пользователя'
        verbose_name_plural = 'Регистрации пользователей'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.last_name} {self.first_name} — {self.direction.name}'


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='dojo_comments',
        verbose_name='Пользователь',
        null=True,
        blank=True,
    )
    author_name = models.CharField('Имя автора', max_length=60)
    text = models.TextField('Комментарий', max_length=500)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['id']

    def __str__(self):
        return f'{self.author_name}: {self.text[:40]}'

    @property
    def author_display(self):
        if self.user:
            full_name = self.user.get_full_name().strip()
            if full_name:
                return full_name
            if self.user.username:
                return self.user.username
        return self.author_name
