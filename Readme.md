# Menu Foods Store

> A Django-based e-commerce example for a food/menu store (sample project).

## Summary

`menu-foods-store` is a Django web application that implements a small online food store. It includes user accounts and membership support, a custom admin interface, product management, shopping cart and checkout flows, order management, and payment integration (Stripe). The project uses SQLite by default for development.

## Key Features

- Product catalog and categories
- Cart and checkout flow
- Order management and order detail views
- Stripe payments integration
- Custom admin area and templates
- User accounts with social authentication (`django-allauth`) and membership pages

## Tech Stack

- Python + Django (Django==5.2.7)
- Packages listed in `requirements.txt` (see below)
- SQLite (`db.sqlite3`) for development
- Stripe for payments

## Requirements

Install dependencies from `requirements.txt`. The main packages are:

- `Django==5.2.7`
- `django-allauth` (social authentication)
- `pillow` (image handling)
- `stripe` (payments)
- `sqlparse`, `PyJWT`, `requests`, and other supporting libraries

To install:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

## Quickstart (development)

1. Create a `.env` or set environment variables for sensitive settings (recommended):

   - `SECRET_KEY` (Django secret key)
   - `DEBUG=True/False`
   - `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` for payments
   - OAuth keys for social auth if used

2. Apply migrations:

```bash
python manage.py migrate
```

3. (Optional) Create a superuser:

```bash
python manage.py createsuperuser
```

4. Run the development server:

```bash
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/` in your browser.

## Project Structure (high level)

- `manage.py` — Django management entrypoint
- `db.sqlite3` — development database (SQLite)
- `requirements.txt` — Python dependencies
- `templates/` — HTML templates used by the app and custom admin
- `media/` — uploaded media (product images)

Apps:

- `accounts/` — user registration, login, membership views and forms
- `custom_admin/` — custom admin pages and templates (dashboard, order lists, product/category management)
- `orders/` — order models, views, cart, checkout and order processing
- `payments/` — payment integration (Stripe-related views/templates)
- `products/` — product models and related code
- `store/` — main site views (home, product detail, search, category pages)
- `user_dashboard/` — user-facing dashboard (my orders, account info)

Look at these files to find the main behavior and templates for each area.

## Configuration notes

- The project appears to use `django-allauth` for social authentication — configure providers and site settings in `settings.py` and admin.
- Payments: Replace placeholder Stripe keys with real keys. For testing use Stripe test keys.
- Media files: Configure `MEDIA_ROOT` and `MEDIA_URL` in `settings.py` and ensure the `media/` folder is writable in development.

## Running tests

Run Django tests:

```bash
python manage.py test
```

## Common commands

- Run local server: `python manage.py runserver`
- Apply migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Run tests: `python manage.py test`

## Notes & Next Steps

- This repository is configured for local development with SQLite. For production, switch to a proper RDBMS, configure allowed hosts, secure secret keys, and set DEBUG to `False`.
- Consider adding a `.env.example` and instructions for setting environment variables.
- Add a short developer CONTRIBUTING or MAINTAINERS section if the project will accept contributions.

---

If you'd like, I can:

- Run a quick code scan to produce a mapping of where models, views and templates live.
- Add a `.env.example` and a `docker-compose.yml` for local development.
