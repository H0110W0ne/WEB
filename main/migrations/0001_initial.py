from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=20, verbose_name='Фамилия')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('age', models.PositiveSmallIntegerField(verbose_name='Возраст')),
                ('direction', models.CharField(choices=[('katana', 'Катана'), ('naginata', 'Нагината'), ('odachi', 'Одати')], max_length=20, verbose_name='Направление')),
                ('message', models.TextField(blank=True, verbose_name='Комментарий')),
                ('telegram_sent', models.BooleanField(default=False, verbose_name='Отправлено в Telegram')),
                ('telegram_error', models.TextField(blank=True, verbose_name='Ошибка Telegram')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
                'ordering': ['-created_at'],
            },
        ),
    ]
