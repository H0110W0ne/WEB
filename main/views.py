import json

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .forms import RegistrationForm
from .models import Comment, Direction
from .tasks import enqueue_registration_notification


@require_GET
def index(request):
    comments = Comment.objects.order_by('-id')[:20]
    comments = list(reversed(comments))
    return render(
        request,
        'main/index.html',
        {
            'comments': comments,
            'comment_author_initial': request.user.get_full_name().strip() or request.user.username if request.user.is_authenticated else '',
        },
    )


@require_GET
def catalog(request):
    return render(request, 'main/catalog.html')


@require_GET
def healthcheck(request):
    return JsonResponse({'status': 'ok'})


def contacts(request):
    context = {
        'directions': Direction.objects.all(),
        'submitted_data': request.POST if request.method == 'POST' else {},
        'server_errors': {},
    }

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if not form.is_valid():
            context['server_result'] = 'Форма содержит ошибки. Проверьте введённые данные.'
            context['server_result_type'] = 'error'
            context['server_errors'] = {field: error_list[0] for field, error_list in form.errors.items()}
            return render(request, 'main/contacts.html', context)

        registration = form.save()
        login(request, registration.user)
        enqueue_registration_notification(registration.id)
        context['server_result'] = 'Пользователь создан, пароль сохранён в хешированном виде, уведомление в Telegram поставлено в очередь.'
        context['server_result_type'] = 'success'
        context['submitted_data'] = {}

    return render(request, 'main/contacts.html', context)


@require_POST
def api_registration(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'detail': 'Некорректный JSON.'}, status=400)

    form = RegistrationForm(payload)

    if not form.is_valid():
        errors = {field: error_list[0] for field, error_list in form.errors.items()}
        return JsonResponse(
            {
                'ok': False,
                'detail': 'Форма содержит ошибки.',
                'errors': errors,
            },
            status=400,
        )

    registration = form.save()
    login(request, registration.user)
    enqueue_registration_notification(registration.id)

    return JsonResponse(
        {
            'ok': True,
            'detail': 'Пользователь успешно создан, пароль сохранён в хешированном виде, уведомление в Telegram поставлено в очередь.',
            'username': registration.user.username,
        }
    )
