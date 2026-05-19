from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .forms import CommentForm
from .utils import serialize_comment


class CommentConsumer(AsyncJsonWebsocketConsumer):
    group_name = 'dojo_comments'

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({
            'event': 'socket_ready',
            'detail': 'WebSocket-соединение установлено.',
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action')
        if action != 'create_comment':
            await self.send_json({
                'event': 'comment_error',
                'detail': 'Неизвестное действие WebSocket.',
            })
            return

        payload = content.get('payload', {})
        result = await self._validate_and_save(payload)
        if not result['ok']:
            await self.send_json({
                'event': 'comment_error',
                'detail': 'Комментарий содержит ошибки.',
                'errors': result['errors'],
            })
            return

        comment = result['comment']
        await self.send_json({
            'event': 'comment_saved',
            'detail': 'Комментарий отправлен через WebSocket.',
            'comment_id': comment['id'],
        })
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'comment.created',
                'comment': comment,
            },
        )

    async def comment_created(self, event):
        await self.send_json({
            'event': 'comment_created',
            'comment': event['comment'],
        })

    @database_sync_to_async
    def _validate_and_save(self, payload):
        form = CommentForm(payload, user=self.scope['user'])
        if not form.is_valid():
            errors = {field: error_list[0] for field, error_list in form.errors.items()}
            return {
                'ok': False,
                'errors': errors,
            }

        comment = form.save()
        return {
            'ok': True,
            'comment': serialize_comment(comment),
        }
