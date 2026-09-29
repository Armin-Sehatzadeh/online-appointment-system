# Online Appointment System

## Overview

Online Appointment System is a RESTful API for managing medical appointments between patients and doctors. Patients can browse available doctors and book appointments, while doctors and administrators can manage appointments, doctor availability, holidays, and leave periods. The system also includes JWT authentication, role-based access control, appointment validation, filtering, ordering, pagination, and concurrency-safe booking.

## Features

* JWT-based authentication
* Role-based access control for patients, doctors, and administrators
* Patient registration and profile management
* Doctor management and doctor profile access
* Doctor availability and working-hour management
* Appointment booking with validation
* Appointment status management and valid status transitions
* Holiday and doctor leave management
* Prevention of double booking using database constraints and transaction locking
* Appointment filtering, ordering, and pagination
* RESTful API built with Django REST Framework
* Interactive API documentation with Swagger / OpenAPI
* MySQL database support
* Docker and Docker Compose support
* Error logging with log rotation

## Tech Stack

* **Backend:** Python, Django, Django REST Framework
* **Authentication:** JWT (JSON Web Tokens)
* **Database:** MySQL
* **API Documentation:** OpenAPI, Swagger UI
* **Filtering & Pagination:** django-filter, DRF Pagination
* **Containerization:** Docker, Docker Compose
* **Web Server:** Django Development Server
* **Version Control:** Git, GitHub

## Project Structure

```text
project-django/
├── appointments/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── admin.py
│   └── tests.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
├── .dockerignore
├── .gitignore
└── README.md
```

### Main Components

* **`appointments/models.py`** — Defines users, doctors, patients, availability, appointments, holidays, and doctor leave.
* **`appointments/serializers.py`** — Handles API serialization and input validation.
* **`appointments/views.py`** — Contains API endpoints and business logic.
* **`appointments/permissions.py`** — Implements role-based access control.
* **`appointments/tests.py`** — Contains automated tests for API behavior and business rules.
* **`config/settings.py`** — Contains Django configuration, database, REST framework, logging, and environment settings.
* **`config/urls.py`** — Defines API routes, JWT endpoints, and Swagger/OpenAPI documentation.
* **`Dockerfile`** — Defines the Django application container.
* **`docker-compose.yml`** — Defines and connects the Django and MySQL services.

## Authentication

The API uses **JWT (JSON Web Token)** authentication through Django REST Framework and `djangorestframework-simplejwt`.

### Authentication Flow

1. Users authenticate using their username and password.
2. The API returns an access token and a refresh token.
3. The access token is sent with protected API requests using the `Authorization` header.
4. The refresh token can be used to obtain a new access token when the access token expires.

### JWT Endpoints

```text
POST /api/token/
POST /api/token/refresh/
```

Example authorization header:

```text
Authorization: Bearer <access_token>
```

### User Roles

The system supports three roles:

* **Patient** — Can manage their own profile and appointments and browse available doctors.
* **Doctor** — Can manage their own availability and manage appointments associated with them.
* **Admin** — Has administrative access to the system's doctors, patients, appointments, availability, holidays, and doctor leave.

Role-based permissions are enforced at the API level using custom DRF permission classes.

## API Documentation

The project provides interactive API documentation using **OpenAPI** and **Swagger UI**.

### Swagger UI

When the application is running, Swagger UI is available at:

http://127.0.0.1:8000/api/docs/

Swagger provides an interactive interface for exploring and testing the available API endpoints.

### OpenAPI Schema

The generated OpenAPI schema is available at:

http://127.0.0.1:8000/api/schema/

The documentation includes the available endpoints, request parameters, serializers, authentication requirements, and response schemas.

## Running with Docker

The project can be run using **Docker Compose**, which starts the Django application and MySQL database as separate services.

### Prerequisites

Make sure the following are installed:

* Docker
* Docker Compose

### Setup

Clone the repository:

```bash
git clone https://github.com/Armin-Sehatzadeh/online-appointment-system.git
cd online-appointment-system
```

Create a `.env` file based on the required environment variables:

```env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

MYSQL_DATABASE=appointment_db
MYSQL_USER=appointment_user
MYSQL_PASSWORD=your_password
MYSQL_ROOT_PASSWORD=your_root_password
```

Build and start the containers:

```bash
docker compose up -d --build
```

Run database migrations:

```bash
docker compose exec web python manage.py migrate
```

The API will be available at:

http://127.0.0.1:8000/

Swagger documentation:

http://127.0.0.1:8000/api/docs/

### Stopping the Application

To stop and remove the containers:

```bash
docker compose down
```

The MySQL data is stored in a Docker volume, so stopping the containers does not remove the database data.

## Running Locally

The project can also be run directly on a local Python environment without Docker.

### Prerequisites

Make sure the following are installed:

* Python 3.10+
* MySQL 8.0+

### Setup

Clone the repository:

```bash
git clone https://github.com/Armin-Sehatzadeh/online-appointment-system.git
cd online-appointment-system
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure the Django and MySQL environment variables.

Run the database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

http://127.0.0.1:8000/

Swagger documentation:

http://127.0.0.1:8000/api/docs/

## Testing

The project includes automated tests for API behavior, permissions, validation, appointment booking, and concurrency-related behavior.

Run the test suite with:

```bash
python manage.py test
```

When using Docker:

```bash
docker compose exec web python manage.py test
```

The test suite covers areas such as:

* Authentication and user roles
* Patient and doctor access control
* Appointment validation
* Appointment status transitions
* Doctor availability
* Holiday and doctor leave rules
* Filtering, ordering, and pagination
* Prevention of duplicate appointment bookings
* Concurrency-safe appointment creation
* Database query optimization

## Database & Concurrency

The project uses **MySQL** as its relational database.

### Database Constraint

A unique constraint is defined on:

```text
doctor + date + time
```

This ensures that two appointments cannot be created for the same doctor, date, and time slot.

### Database Indexing

An index is defined on the `Appointment.date` field to improve the performance of date-based appointment queries.

Query performance was also analyzed using MySQL query plans and `EXPLAIN` where appropriate.

### Query Optimization

The API uses Django ORM optimization techniques such as:

* `select_related()` for foreign-key relationships
* `prefetch_related()` for related collections
* Query-count tests using `assertNumQueries`

These techniques help reduce unnecessary database queries and improve API performance.

### Transaction Locking

Appointment creation uses a database transaction together with `select_for_update()` to lock the relevant doctor record while the booking operation is performed.

This helps prevent race conditions when multiple users attempt to book the same appointment slot at the same time.

If another request attempts to create an appointment for an already-booked slot, the database constraint prevents the duplicate booking and the API returns an appropriate validation error.

## License

This project is currently provided for educational and portfolio purposes.
