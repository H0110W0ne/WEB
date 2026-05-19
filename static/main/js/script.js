document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registration-form");

  if (!form) {
    return;
  }

  const apiUrl = form.dataset.apiUrl;
  const firstName = document.getElementById("firstName");
  const lastName = document.getElementById("lastName");
  const email = document.getElementById("email");
  const phone = document.getElementById("phone");
  const age = document.getElementById("age");
  const direction = document.getElementById("direction");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const message = document.getElementById("message");
  const result = document.getElementById("form-result");
  const submitButton = form.querySelector('button[type="submit"]');

  function getCookie(name) {
    const cookieValue = document.cookie
      .split('; ')
      .find((row) => row.startsWith(`${name}=`));

    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
  }

  function setMessage(fieldId, text, type) {
    const messageElement = document.getElementById(`${fieldId}-message`);
    if (!messageElement) return;

    messageElement.textContent = text;
    messageElement.className = type ? `field-message ${type}` : 'field-message';
  }

  function validateNameField(field, fieldId) {
    const value = field.value.trim();
    const namePattern = /^[А-ЯЁA-Z][а-яёa-z]+$/;

    if (value === "") {
      field.setCustomValidity("Поле обязательно для заполнения.");
      setMessage(fieldId, "Поле обязательно для заполнения.", "error");
      return false;
    }

    if (value.length < 2 || value.length > 20) {
      field.setCustomValidity("Имя должно содержать от 2 до 20 символов.");
      setMessage(fieldId, "Имя должно содержать от 2 до 20 символов.", "error");
      return false;
    }

    if (!namePattern.test(value)) {
      field.setCustomValidity("Только буквы, первая буква заглавная, остальные строчные.");
      setMessage(fieldId, "Только буквы, первая буква заглавная, остальные строчные.", "error");
      return false;
    }

    field.setCustomValidity("");
    setMessage(fieldId, "Поле заполнено верно.", "success");
    return true;
  }

  function validateEmailField() {
    const value = email.value.trim();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (value === "") {
      email.setCustomValidity("Введите email.");
      setMessage("email", "Введите email.", "error");
      return false;
    }

    if (!emailPattern.test(value)) {
      email.setCustomValidity("Некорректный формат email.");
      setMessage("email", "Некорректный формат email.", "error");
      return false;
    }

    email.setCustomValidity("");
    setMessage("email", "Email заполнен верно.", "success");
    return true;
  }

  function applyPhoneMask(value) {
    const digits = value.replace(/\D/g, "").replace(/^8/, "7");
    let cleaned = digits;

    if (!cleaned.startsWith("7")) {
      cleaned = "7" + cleaned;
    }

    cleaned = cleaned.substring(0, 11);

    let resultValue = "+7";
    if (cleaned.length > 1) {
      resultValue += " (" + cleaned.substring(1, 4);
    }
    if (cleaned.length >= 4) {
      resultValue += ")";
    }
    if (cleaned.length > 4) {
      resultValue += " " + cleaned.substring(4, 7);
    }
    if (cleaned.length > 7) {
      resultValue += "-" + cleaned.substring(7, 9);
    }
    if (cleaned.length > 9) {
      resultValue += "-" + cleaned.substring(9, 11);
    }

    return resultValue;
  }

  function validatePhoneField() {
    const value = phone.value.trim();
    const phonePattern = /^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$/;

    if (value === "") {
      phone.setCustomValidity("Введите номер телефона.");
      setMessage("phone", "Введите номер телефона.", "error");
      return false;
    }

    if (!phonePattern.test(value)) {
      phone.setCustomValidity("Введите телефон в формате +7 (999) 123-45-67.");
      setMessage("phone", "Введите телефон в формате +7 (999) 123-45-67.", "error");
      return false;
    }

    phone.setCustomValidity("");
    setMessage("phone", "Телефон заполнен верно.", "success");
    return true;
  }

  function validateAgeField() {
    const value = Number(age.value);

    if (age.value.trim() === "") {
      age.setCustomValidity("Введите возраст.");
      setMessage("age", "Введите возраст.", "error");
      return false;
    }

    if (value < 10 || value > 70) {
      age.setCustomValidity("Возраст должен быть от 10 до 70 лет.");
      setMessage("age", "Возраст должен быть от 10 до 70 лет.", "error");
      return false;
    }

    age.setCustomValidity("");
    setMessage("age", "Возраст указан верно.", "success");
    return true;
  }

  function validateDirectionField() {
    if (direction.value === "") {
      direction.setCustomValidity("Выберите направление.");
      setMessage("direction", "Выберите направление.", "error");
      return false;
    }

    direction.setCustomValidity("");
    setMessage("direction", "Направление выбрано.", "success");
    return true;
  }

  function validatePasswordField() {
    const value = password.value.trim();
    const weakPasswords = [
      "12345678",
      "123456789",
      "qwerty123",
      "password",
      "password123",
      "admin123",
      "11111111",
      "00000000"
    ];

    if (value === "") {
      password.setCustomValidity("Введите пароль.");
      setMessage("password", "Введите пароль.", "error");
      return false;
    }

    if (value.length < 8 || value.length > 128) {
      password.setCustomValidity("Пароль должен содержать минимум 8 символов.");
      setMessage("password", "Пароль должен содержать минимум 8 символов.", "error");
      return false;
    }

    if (/^\d+$/.test(value)) {
      password.setCustomValidity("Пароль не должен состоять только из цифр.");
      setMessage("password", "Пароль не должен состоять только из цифр.", "error");
      return false;
    }

    if (weakPasswords.includes(value.toLowerCase())) {
      password.setCustomValidity("Слишком простой пароль.");
      setMessage("password", "Слишком простой пароль.", "error");
      return false;
    }

    const first = firstName.value.trim().toLowerCase();
    const last = lastName.value.trim().toLowerCase();
    const mail = email.value.trim().toLowerCase();

    if (
      (first && value.toLowerCase().includes(first)) ||
      (last && value.toLowerCase().includes(last)) ||
      (mail && value.toLowerCase().includes(mail.split("@")[0]))
    ) {
      password.setCustomValidity("Пароль слишком похож на личные данные.");
      setMessage("password", "Пароль слишком похож на личные данные.", "error");
      return false;
    }

    password.setCustomValidity("");
    setMessage("password", "Пароль прошёл предварительную проверку.", "success");
    return true;
  }

  function validateConfirmPasswordField() {
    const value = confirmPassword.value.trim();

    if (value === "") {
      confirmPassword.setCustomValidity("Подтвердите пароль.");
      setMessage("confirmPassword", "Подтвердите пароль.", "error");
      return false;
    }

    if (!validatePasswordField()) {
      confirmPassword.setCustomValidity("Сначала введите корректный пароль.");
      setMessage("confirmPassword", "Сначала введите корректный пароль.", "error");
      return false;
    }

    if (value !== password.value) {
      confirmPassword.setCustomValidity("Пароли не совпадают.");
      setMessage("confirmPassword", "Пароли не совпадают.", "error");
      return false;
    }

    confirmPassword.setCustomValidity("");
    setMessage("confirmPassword", "Пароли совпадают.", "success");
    return true;
  }

  function validateOptionalMessageField() {
    message.setCustomValidity("");
    setMessage("message", message.value.trim() ? "Комментарий добавлен." : "", message.value.trim() ? "success" : "");
    return true;
  }

  async function submitRegistration() {
    const payload = {
      firstName: firstName.value.trim(),
      lastName: lastName.value.trim(),
      email: email.value.trim(),
      phone: phone.value.trim(),
      age: Number(age.value),
      direction: direction.value,
      password: password.value,
      confirmPassword: confirmPassword.value,
      message: message.value.trim()
    };

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken') || ''
      },
      body: JSON.stringify(payload)
    });

    let data = null;

    try {
      data = await response.json();
    } catch (error) {
      data = null;
    }

    if (!response.ok) {
      if (data?.errors) {
        Object.entries(data.errors).forEach(([field, text]) => {
          setMessage(field, text, 'error');
        });
      }
      throw new Error(data?.detail || `Ошибка сервера: ${response.status}`);
    }

    return data;
  }

  firstName.addEventListener("input", () => validateNameField(firstName, "firstName"));
  lastName.addEventListener("input", () => validateNameField(lastName, "lastName"));
  email.addEventListener("input", validateEmailField);

  phone.addEventListener("input", () => {
    phone.value = applyPhoneMask(phone.value);
    validatePhoneField();
  });

  age.addEventListener("input", validateAgeField);
  direction.addEventListener("change", validateDirectionField);
  password.addEventListener("input", () => {
    validatePasswordField();
    validateConfirmPasswordField();
  });
  confirmPassword.addEventListener("input", validateConfirmPasswordField);
  message.addEventListener("input", validateOptionalMessageField);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const isFirstNameValid = validateNameField(firstName, "firstName");
    const isLastNameValid = validateNameField(lastName, "lastName");
    const isEmailValid = validateEmailField();
    const isPhoneValid = validatePhoneField();
    const isAgeValid = validateAgeField();
    const isDirectionValid = validateDirectionField();
    const isPasswordValid = validatePasswordField();
    const isConfirmPasswordValid = validateConfirmPasswordField();
    validateOptionalMessageField();

    if (
      !isFirstNameValid ||
      !isLastNameValid ||
      !isEmailValid ||
      !isPhoneValid ||
      !isAgeValid ||
      !isDirectionValid ||
      !isPasswordValid ||
      !isConfirmPasswordValid
    ) {
      result.textContent = "Форма содержит ошибки. Исправьте поля, подсвеченные красным.";
      result.className = "form-result error";
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Отправка...";
    result.textContent = "";
    result.className = "form-result";

    try {
      const data = await submitRegistration();
      result.textContent = data?.detail || "Заявка успешно отправлена.";
      result.className = "form-result success";
      form.reset();

      document.querySelectorAll(".field-message").forEach((element) => {
        element.textContent = "";
        element.className = "field-message";
      });
    } catch (error) {
      result.textContent = error.message || "Не удалось отправить заявку.";
      result.className = "form-result error";
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Зарегистрироваться";
    }
  });
});
