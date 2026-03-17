# API Automation Framework Demo Project

Масштабований фреймворк для автоматизації тестування API, сфокусований на Clean Code, продуктивності та глибокій інтеграції в CI/CD процеси.

## 🛠 Tech Stack
- **Language:** Python
- **Testing Framework:** Pytest (xdist, pytest-check)
- **Validation:** Pydantic, JMESPath
- **Infrastructure:** GitHub Actions, Telegram Bot API
- **Reporting:** Allure Reports

## 🏗 Key Features

### 🎛️ Environment & Configuration
- **Multi-environment Support:** Гнучке налаштування під різні стенди (**Prod, Stage**) через конфігураційні файли та змінні оточення.
- **CLI Integration:** Можливість динамічного керування параметрами запуску (вибір середовища, кількість потоків, маркери, рівень логування) безпосередньо з командного рядка.

### 🏛 Architecture & Clean Code
- **BaseClient & DB Manager:** Інкапсуляція HTTP-логіки та окремий шар для валідації даних у БД (Data Persistence).
- **Session Management:** Робота з кількома профілями користувачів (Active/Empty state) без втрати контексту сесії.
- **Advanced Logging:** Повна прозорість діагностики завдяки детальному логуванню Request/Response Body та заголовків.

### 🧪 Advanced testing techniques
- **Smart Parametrization:** Реалізація Data-Driven підходу для перевірки граничних значень, позитивних та негативних сценаріїв.
- **Custom Markers:** Чітка сегментація тестів за типами (Smoke, Regression, Performance) для оптимізації часу виконання.
- **Soft Assertions:** Використання `pytest-check` для фіксації всіх знайдених невідповідностей без передчасного завершення тесту.

### 💎 Advanced Validation
- **Pydantic Models:** Сувора перевірка схем та типів даних (Contract Testing).
- **RFC 9110 Compliance:** Тестування обробки помилок згідно з індустріальним стандартом Problem Details.

### ⚡ Performance & Scalability
- **SLA & Thresholds:** Автоматичний контроль часу відповіді (Average Response Time) з падінням тесту при перевищенні заданих порогів.
- **Parallel Execution:** Оптимізація часу прогону через `pytest-xdist` та `ThreadPoolExecutor`.

### ⚙️ CI/CD Integration
- **Smart Pipeline:** У GitHub Actions налаштовано Smoke-gate (регресія запускається лише після успішного Smoke-тесту).
- **JUnit XML Aggregation:** Скрипт для консолідації даних із декількох звітів у єдине зведення.
- **Telegram Feedback:** Миттєва відправка агрегованої статистики прогону в месенджер.

## 📊 Reporting & Analytics
- **Step-by-step scenarios (`@allure.step`)** — детальне відстеження логіки виконання тесту для легкого розуміння бізнес-процесів.
- **Logs in attachments** — повна історія HTTP-взаємодій, що дозволяє миттєво діагностувати причини падіння.
- **Severity levels** — чітка пріоритезація тестів (Blocker, Critical, Normal тощо) для ефективного управління якістю.
- **Jira Integration** — можливість додавати прямі посилання на баг-тікети за допомогою декоратора @allure.issue.
- **Dynamic performance parameters** — візуалізація метрик швидкодії та автоматичний контроль виконання SLA безпосередньо у звіті.
