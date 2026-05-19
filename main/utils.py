def serialize_comment(comment):
    return {
        'id': comment.id,
        'author': comment.author_display,
        'text': comment.text,
        'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M:%S'),
    }
