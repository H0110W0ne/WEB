import json
from unittest.mock import patch

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from strannik_site.asgi import application

from .models import Comment, Direction, Registration
from .tasks import send_registration_to_telegram

User = get_user_model()


class RegistrationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Direction.objects.get_or_create(slug='katana', defaults={'name': 'Катана'})
        Direction.objects.get_or_create(slug='naginata', defaults={'name': 'Нагината'})
        Direction.objects.get_or_create(slug='odachi', defaults={'name': 'Одати'})

    @patch('main.views.enqueue_registration_notification')
    def test_api_registration_creates_user_and_hashed_password(self, mocked_enqueue):
        payload = {
            'firstName': 'Иван',
            'lastName': 'Петров',
            'email': 'ivan@example.com',
            'phone': '+7 (999) 123-45-67',
            'age': 21,
            'direction': 'katana',
            'password': 'SecurePass123',
            'confirmPassword': 'SecurePass123',
            'message': 'Хочу заниматься катаной',
        }

        response = self.client.post(
            reverse('main:api_registration'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='ivan@example.com')
        registration = Registration.objects.get(user=user)

        self.assertTrue(user.check_password('SecurePass123'))
        self.assertNotEqual(user.password, 'SecurePass123')
        self.assertTrue(user.password.startswith('pbkdf2_') or '$argon2' in user.password or user.password.startswith('bcrypt'))
        self.assertEqual(registration.direction.slug, 'katana')
        mocked_enqueue.assert_called_once_with(registration.id)

    @patch('main.tasks.send_telegram_message', return_value={'ok': True})
    def test_telegram_task_marks_registration_as_sent(self, mocked_send):
        direction = Direction.objects.get(slug='katana')
        user = User.objects.create_user(username='task@example.com', email='task@example.com', password='SecurePass123')
        registration = Registration.objects.create(
            user=user,
            first_name='Иван',
            last_name='Петров',
            email='task@example.com',
            phone='+7 (999) 123-45-67',
            age=21,
            direction=direction,
            message='Тест',
        )

        result = send_registration_to_telegram.apply(args=[registration.id])
        registration.refresh_from_db()

        self.assertTrue(result.successful())
        self.assertTrue(registration.telegram_sent)
        mocked_send.assert_called_once()

    def test_duplicate_email_is_rejected(self):
        user = User(username='ivan@example.com', email='ivan@example.com')
        user.set_password('SecurePass123')
        user.save()

        payload = {
            'firstName': 'Иван',
            'lastName': 'Петров',
            'email': 'ivan@example.com',
            'phone': '+7 (999) 123-45-67',
            'age': 21,
            'direction': 'katana',
            'password': 'SecurePass123',
            'confirmPassword': 'SecurePass123',
            'message': 'Повторная заявка',
        }

        response = self.client.post(
            reverse('main:api_registration'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(username='ivan@example.com').count(), 1)


class WebSocketCommentTests(TransactionTestCase):
    reset_sequences = True

    def test_guest_comment_is_broadcast_via_websocket(self):
        async def scenario():
            sender = WebsocketCommunicator(application, '/ws/comments/')
            watcher = WebsocketCommunicator(application, '/ws/comments/')

            connected_sender, _ = await sender.connect()
            connected_watcher, _ = await watcher.connect()
            self.assertTrue(connected_sender)
            self.assertTrue(connected_watcher)

            await sender.receive_json_from()
            await watcher.receive_json_from()

            await sender.send_json_to({
                'action': 'create_comment',
                'payload': {
                    'authorName': 'Гость',
                    'text': 'Комментарий через WebSocket',
                },
            })

            saved = await sender.receive_json_from()
            self.assertEqual(saved['event'], 'comment_saved')

            created_for_sender = await sender.receive_json_from()
            created_for_watcher = await watcher.receive_json_from()
            self.assertEqual(created_for_sender['event'], 'comment_created')
            self.assertEqual(created_for_watcher['event'], 'comment_created')
            self.assertEqual(created_for_watcher['comment']['text'], 'Комментарий через WebSocket')

            await sender.disconnect()
            await watcher.disconnect()

        async_to_sync(scenario)()
        self.assertEqual(Comment.objects.count(), 1)

    def test_invalid_payload_returns_error_event(self):
        async def scenario():
            communicator = WebsocketCommunicator(application, '/ws/comments/')
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            await communicator.receive_json_from()

            await communicator.send_json_to({
                'action': 'create_comment',
                'payload': {
                    'authorName': 'A',
                    'text': '',
                },
            })

            error = await communicator.receive_json_from()
            self.assertEqual(error['event'], 'comment_error')
            self.assertIn('errors', error)
            await communicator.disconnect()

        async_to_sync(scenario)()
