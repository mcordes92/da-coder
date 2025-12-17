# da-coder

A complete Django REST API for a freelancer platform that enables managing offers, orders, and reviews between customers and service providers.

The project provides a modern backend solution with token-based authentication, extensive filtering capabilities, and a clear separation between business and customer profiles. The API is fully documented and features a comprehensive test suite with 99% code coverage.

## Features

* 🔐 **Token-based Authentication** – Secure user registration and login with Django REST Framework Token Authentication
* 👤 **Dual Profile Management** – Separate profiles for business (service providers) and customers with extended information
* 💼 **Offer Management** – Create, edit, and manage service offers with details and pricing
* 📝 **Order System** – Complete order workflow with status tracking (pending, in_progress, completed, declined, canceled)
* ⭐ **Review System** – Detailed reviews with ratings, descriptions, and timestamps
* 🔍 **Advanced Filtering** – Django-Filter integration for complex queries
* 📊 **Base Information** – Management of categories, programming languages, and other metadata
* 🧪 **Comprehensive Testing** – 117 tests with 99% code coverage
* 📚 **API Documentation** – Complete endpoint documentation in [API.md](API.md)

## Prerequisites

* **Python**: 3.10 or higher (tested with Python 3.13.7)
* **Operating System**: Windows, macOS, or Linux
* **Database**: SQLite (default) or PostgreSQL/MySQL (configurable)
* **Tools**: pip (Python Package Manager)

## Installation

### With pip (Standard)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd da-coder
   ```

2. **Create and activate virtual environment**

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (see Configuration)

5. **Initialize database**

   ```bash
   python manage.py migrate
   ```

6. **Start development server**

   ```bash
   python manage.py runserver
   ```

   The API is now available at `http://localhost:8000/`.

### Editable Install (for Development)

For active development, you can install the project in editable mode:

```bash
pip install -e .
```

## Configuration

### Environment Variables

The project uses `python-dotenv` for configuration. Create a `.env` file in the root directory:

```env
# Django Secret Key (generate your own for production!)
DJANGO_SECRET_KEY=your-secret-key-here

# Debug mode (set to False in production)
DEBUG=True

# Database configuration (optional, defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Important:** The `DJANGO_SECRET_KEY` is mandatory. The project will not start without this variable.

### Example for Secret Key Generation

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Project Structure

```
da-coder/
├── auth_app/           # Authentication (Registration, Login)
│   ├── api/           # Serializers, Views, URLs
│   └── tests/         # Auth tests
├── profile_app/        # User profiles (Business/Customer)
│   ├── api/           # Profile API endpoints
│   └── tests/         # Profile tests
├── offer_app/          # Offer management
│   ├── api/           # Offer & OfferDetail APIs
│   ├── filters/       # Custom offer filters
│   └── tests/         # Offer tests
├── order_app/          # Order system
│   ├── api/           # Order API with status management
│   └── tests/         # Order tests
├── review_app/         # Review system
│   ├── api/           # Review APIs
│   ├── filters/       # Review filters
│   └── tests/         # Review tests
├── baseinfo_app/       # Base information (categories, etc.)
│   ├── api/           # BaseInfo APIs
│   └── tests/         # BaseInfo tests
├── core/               # Django main configuration
│   ├── settings.py    # Project settings
│   ├── urls.py        # URL routing
│   └── wsgi.py        # WSGI configuration
├── static/             # Static files
├── htmlcov/            # Coverage HTML report
├── manage.py           # Django management script
├── setup.py            # Setup script for test data
├── requirements.txt    # Python dependencies
├── pytest.ini          # Pytest configuration
├── API.md              # Detailed API documentation
└── db.sqlite3          # SQLite database
```

### Main Modules

* **auth_app**: Token-based authentication with custom registration
* **profile_app**: Extended user profiles with business/customer distinction
* **offer_app**: Offers with details, prices, delivery times, and revisions
* **order_app**: Order management with status workflow and permission system
* **review_app**: Rating system with filtering and business assignment

## Tests

The project has a comprehensive test suite with 117 tests.

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# Single test file
pytest auth_app/tests/test_login.py

# Single test
pytest auth_app/tests/test_login.py::TestLoginView::test_login_success
```

### Running Coverage

```bash
# Coverage report in terminal
pytest --cov

# Detailed report with missing lines
pytest --cov --cov-report=term-missing

# Generate HTML report
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser

# XML report (for CI/CD)
pytest --cov --cov-report=xml
```

### Test Coverage

**Current Coverage: 99%** (Status: 117 tests, all passed)

```
Coverage Summary:
- Total Statements: 1710
- Missing: 11
- Coverage: 99%
```

**All other modules: 100% Coverage**

### Django Tests

Alternatively, Django's own test runner can be used:

```bash
python manage.py test
```

## API Documentation

Complete API documentation with all endpoints, request/response examples, and status codes can be found in [API.md](API.md).

## Contributing

Contributions are welcome! Please follow these steps:

1. **Create a fork** of the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Add tests** for new functionality
5. **Run tests**: Make sure all tests pass and coverage remains high
6. **Push the branch**: `git push origin feature/amazing-feature`
7. **Open a pull request**

### Coding Guidelines

* Write meaningful commit messages
* Add tests for new features
* Keep code coverage above 95%
* Follow Django best practices
* Document new API endpoints in API.md

---

**Project created as part of a Backend Intensive Course**

For questions or issues, please open an issue in the repository.
