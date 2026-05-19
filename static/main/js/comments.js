document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('comment-form');
  const commentsList = document.getElementById('comments-list');
  const result = document.getElementById('comment-result');
  const submitButton = document.getElementById('comment-submit');
  const socketStatus = document.getElementById('socket-status');

  if (!form || !commentsList) {
    return;
  }

  const authorInput = document.getElementById('comment-author');
  const textInput = document.getElementById('comment-text');
  const authorMessage = document.getElementById('comment-author-message');
  const textMessage = document.getElementById('comment-text-message');
  const wsPath = form.dataset.wsUrl;
  let socket = null;

  function setResult(text, type = '') {
    result.textContent = text;
    result.className = 'form-result';
    if (type) {
      result.classList.add(type);
    }
  }

  function setFieldMessage(element, text, type = '') {
    if (!element) {
      return;
    }
    element.textContent = text;
    element.className = 'field-message';
    if (type) {
      element.classList.add(type);
    }
  }

  function setSocketStatus(text, type = '') {
    if (!socketStatus) {
      return;
    }
    socketStatus.textContent = text;
    socketStatus.className = 'field-hint';
    if (type) {
      socketStatus.classList.add(type);
    }
  }

  function validateAuthor() {
    if (!authorInput) {
      return true;
    }

    const value = authorInput.value.trim();
    if (value.length < 2) {
      setFieldMessage(authorMessage, 'Введите имя автора не короче 2 символов.', 'error');
      return false;
    }

    setFieldMessage(authorMessage, 'Имя автора указано.', 'success');
    return true;
  }

  function validateText() {
    const value = textInput.value.trim();
    if (value.length < 2) {
      setFieldMessage(textMessage, 'Комментарий должен содержать минимум 2 символа.', 'error');
      return false;
    }

    if (value.length > 500) {
      setFieldMessage(textMessage, 'Комментарий не должен быть длиннее 500 символов.', 'error');
      return false;
    }

    setFieldMessage(textMessage, 'Комментарий готов к отправке.', 'success');
    return true;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function renderComment(comment) {
    if (commentsList.querySelector(`[data-comment-id="${comment.id}"]`)) {
      return;
    }

    const emptyMessage = document.getElementById('comments-empty');
    if (emptyMessage) {
      emptyMessage.remove();
    }

    const article = document.createElement('article');
    article.className = 'comment-card';
    article.dataset.commentId = comment.id;
    article.innerHTML = `
      <div class="comment-meta">
        <strong>${escapeHtml(comment.author)}</strong>
        <span>${escapeHtml(comment.created_at)}</span>
      </div>
      <p>${escapeHtml(comment.text)}</p>
    `;

    commentsList.appendChild(article);
  }

  function connectSocket() {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    socket = new WebSocket(`${scheme}://${window.location.host}${wsPath}`);

    socket.addEventListener('open', () => {
      submitButton.disabled = false;
      setSocketStatus('WebSocket подключён. Комментарии приходят в реальном времени.', 'success');
    });

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);

      if (data.event === 'socket_ready') {
        setSocketStatus(data.detail, 'success');
        return;
      }

      if (data.event === 'comment_created' && data.comment) {
        renderComment(data.comment);
        return;
      }

      if (data.event === 'comment_saved') {
        textInput.value = '';
        setFieldMessage(textMessage, '', '');
        setResult(data.detail || 'Комментарий отправлен.', 'success');
        return;
      }

      if (data.event === 'comment_error') {
        setResult(data.detail || 'Не удалось отправить комментарий.', 'error');
        if (data.errors?.authorName) {
          setFieldMessage(authorMessage, data.errors.authorName, 'error');
        }
        if (data.errors?.text) {
          setFieldMessage(textMessage, data.errors.text, 'error');
        }
      }
    });

    socket.addEventListener('close', () => {
      submitButton.disabled = true;
      setSocketStatus('WebSocket отключён. Идёт переподключение...', 'error');
      window.setTimeout(connectSocket, 1500);
    });

    socket.addEventListener('error', () => {
      setSocketStatus('Ошибка WebSocket-соединения.', 'error');
    });
  }

  if (authorInput) {
    authorInput.addEventListener('input', validateAuthor);
  }
  textInput.addEventListener('input', validateText);

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const authorValid = validateAuthor();
    const textValid = validateText();
    if (!authorValid || !textValid) {
      setResult('Исправьте ошибки в форме комментария.', 'error');
      return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setResult('WebSocket ещё не подключён. Подождите пару секунд и повторите.', 'error');
      return;
    }

    const payload = {
      action: 'create_comment',
      payload: {
        authorName: authorInput ? authorInput.value.trim() : '',
        text: textInput.value.trim(),
      },
    };

    setResult('');
    submitButton.disabled = true;
    submitButton.textContent = 'Отправка...';
    socket.send(JSON.stringify(payload));
    window.setTimeout(() => {
      submitButton.disabled = false;
      submitButton.textContent = 'Отправить комментарий';
    }, 300);
  });

  connectSocket();
});
