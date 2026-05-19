from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_directions_and_copy(apps, schema_editor):
    Direction = apps.get_model('main', 'Direction')
    Registration = apps.get_model('main', 'Registration')

    direction_map = {
        'katana': Direction.objects.create(slug='katana', name='Катана', description='Работа с японским мечом.'),
        'naginata': Direction.objects.create(slug='naginata', name='Нагината', description='Работа с древковым оружием.'),
        'odachi': Direction.objects.create(slug='odachi', name='Одати', description='Работа с длинным мечом.'),
    }

    for registration in Registration.objects.all():
        registration.direction_ref = direction_map.get(registration.direction)
        registration.save(update_fields=['direction_ref'])


def reverse_seed_directions(apps, schema_editor):
    Direction = apps.get_model('main', 'Direction')
    Direction.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=30, unique=True, verbose_name='Код направления')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Направление',
                'verbose_name_plural': 'Направления',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='registration',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_registration', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='registration',
            name='direction_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='registrations_temp', to='main.direction', verbose_name='Направление'),
        ),
        migrations.RunPython(seed_directions_and_copy, reverse_seed_directions),
        migrations.RemoveField(
            model_name='registration',
            name='direction',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='direction_ref',
            new_name='direction',
        ),
        migrations.AlterField(
            model_name='registration',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='main.direction', verbose_name='Направление'),
        ),
        migrations.AlterModelOptions(
            name='registration',
            options={'ordering': ['-created_at'], 'verbose_name': 'Регистрация пользователя', 'verbose_name_plural': 'Регистрации пользователей'},
        ),
    ]
