# API Automation Framework Demo Project

## 🎯 Purpose of the Project
Друзі, хочу поділитися результатами свого Demo-проєкту з автоматизації API. Цей проєкт став етапом практичного закріплення навичок під час проходження курсу QA Automation (Python). 

Я прагнув побудувати не просто набір скриптів, який перевіряє статус-коди, а повноцінний, надійний та масштабований фреймворк. 

## 🛠 Tech Stack
- **Language:** Python
- **Testing Framework:** Pytest (xdist, pytest-check)
- **Validation:** Pydantic, JMESPath
- **Containerization:** Docker, Docker Compose
- **Tracing:** OpenTelemetry SDK (Distributed Tracing)
- **Storage & Visualization:** Grafana Cloud (Tempo)
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

### 🐳 Docker-infrastructure
- **Full isolation:** Проект повністю контейнеризовано, що дозволяє уникнути проблем "it works on my machine and doesn't work on other machine".
- **Instant Sync (Hot-Reload):** Завдяки налаштованим Volumes, будь-які зміни в коді тесту у вашій IDE миттєво з'являються в контейнері. Не потрібно перезбирати образ після кожного виправленого рядка коду.

### 📊 Reporting & Analytics
- **Step-by-step scenarios** — детальне відстеження логіки виконання тесту для легкого розуміння бізнес-процесів за допомогою декоратора @allure.step.
- **Logs in attachments** — повна історія HTTP-взаємодій, що дозволяє миттєво діагностувати причини падіння.
- **Auto-generated cURL** — кожен запит у звіті супроводжується готовою cURL-командою для миттєвого відтворення (Replication Steps).
- **Severity levels** — чітка пріоритезація тестів (Blocker, Critical, Normal тощо) для ефективного управління якістю.
- **Smart Data Masking** — автоматичне маскування чутливих даних (session_id, tokens, passwords) у логах та звітах Allure.
- **Jira Integration** — можливість додавати прямі посилання на баг-тікети за допомогою декоратора @allure.issue.
- **Dynamic performance parameters** — візуалізація метрик швидкодії та автоматичний контроль виконання SLA безпосередньо у звіті.

### 🔭 Observability & Distributed Tracing
- **OpenTelemetry Integration** — Повна наскрізна видимість HTTP-запитів завдяки впровадженню OpenTelemetry SDK. Кожен тест тепер є частиною глобального трейсу системи.
- **Trace Context Propagation** — Автоматична передача та синхронізація trace_id між тестами та мікросервісами, що дозволяє миттєво знаходити "корінь" проблеми в розподіленій архітектурі.
- **Direct Deep Linking** — Динамічні посилання в Allure-звітах, що ведуть прямо на детальний Timeline конкретного трейсу в Grafana Cloud (Tempo).
- **Parallel Tracing Stability** — Надійна ініціалізація та ізоляція передачі даних при паралельному запуску через pytest-xdist — кожен воркер працює як незалежний агент моніторингу.
- **Rich Span Metadata** — Фіксація деталізованих івентів (Request/Response Body до 64KB) безпосередньо всередині спанів для аналізу стану системи без доступу до внутрішніх логів розробки.
- **Graceful Data Delivery** — Гарантована відправка всіх накопичених трейсів перед завершенням роботи контейнера завдяки налаштованим механізмам flush та shutdown.

### 🤖 AI-Assisted Development
- **Architectural optimization**
- **Code review & Refactoring**
- **Dynamic Configuration Strategy**
- **Troubleshooting & Debugging**
- **Documentation generation**

### 🚀 How to Run

- **1. Clone Project**
```
git clone https://github.com/SlavaPykhydko/QA_Demo_Project
cd QA_Demo_Project
```
- **2. Configure Secrets**

 Create a .env file in the root based on .env.example and add your credentials.
- **3. Build Image**

Executed once on the first run or after changes to requirements.txt
```
docker compose build
```
- **4. Run Tests**

Runs all test groups (Smoke, Regression, Performance) defined in docker-compose.yml
```
docker compose up
```
For choosing specific env and threads quantity 
```
TARGET_ENV=stage THREADS=4 docker compose up
```
To run specific markers or files, use the run command
```
# Smoke tests only
docker compose run --rm api-tests pytest -m smoke --env=prod -n 2

# Regression tests only (excluding smoke)
docker compose run --rm api-tests pytest -m "regression and not smoke"
```
- **5. Open Report**

Results are automatically synchronized with your local allure-results folder. Simply generate the report:
```
allure serve allure-results
```
- **6. Cleanup**

Stop the containers and clean up temporary networks.
```
docker compose down
```
