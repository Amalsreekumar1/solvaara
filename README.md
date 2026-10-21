

# Solvaara

A jewellery catalogue website built with Django. Visitors browse products and enquire through WhatsApp or a contact form. The shop owner manages everything through the Django Admin.

Solvaara is a **fictional** Indian-inspired jewellery brand, built as a portfolio project. It is a **catalogue, not an online store**: there is no cart, checkout, payment or customer login.

---

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Pages and URLs](#pages-and-urls)
- [Data model](#data-model)
- [Using the admin](#using-the-admin)
- [Customer enquiries](#customer-enquiries)
- [Design](#design)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Limitations](#limitations)
- [Content notes](#content-notes)

---

## Features

- Categories and products stored in a database.
- Optional prices and sale prices. Products with no price show "Price on Enquiry".
- Separate **publication status** (draft or published) and **availability** (available, sold out, made to order).
- Multiple photos per product, each with alternative text and display order.
- Validated image uploads: JPG, PNG or WebP, 5 MB maximum.
- Django Admin set up for the owner: search, filters, grouped form sections, a photo gallery editor, bulk publish and unpublish, and an enquiries inbox.
- Public pages: homepage, catalogue, product detail, Our Story, Contact, four policy pages and a custom 404.
- Catalogue search by name or product code, category and price filters, sorting and pagination.
- WhatsApp enquiry link on every product, with a prefilled message naming the product, its code and its page address.
- Contact form that saves every enquiry to the database. The visitor sees a success message only after the save succeeds.
- Business details (WhatsApp number, email, phone, address, hours, social links) come from environment variables and appear only when set.
- Search engine indexing is blocked unless explicitly enabled.
- Smooth scrolling, scroll reveals and hover effects, all switched off for visitors who prefer reduced motion.

---

## Tech stack

| Layer            | Choice                                                                     |
| ---------------- | -------------------------------------------------------------------------- |
| Language         | Python 3.12 or newer                                                       |
| Framework        | Django (monolith)                                                          |
| Front end        | Django Templates, HTML, Tailwind CSS (Play CDN script), vanilla JavaScript |
| Smooth scrolling | Lenis, from a CDN                                                          |
| Fonts and icons  | Bodoni Moda, Manrope and Material Symbols, from Google Fonts               |
| Database         | SQLite                                                                     |
| Images           | Django `ImageField` with Pillow                                          |
| Admin            | Django Admin                                                               |
| Packages         | [uv](https://docs.astral.sh/uv/)                                            |

There is no Node.js, React, separate API or headless CMS.

---

## Project structure

```
solvaara/
├── config/                     # Project settings and root URLs
├── catalogue/                  # The catalogue app
│   ├── models.py               # Category, Product, ProductImage, Enquiry
│   ├── views.py
│   ├── forms.py                # Enquiry form
│   ├── validators.py           # Image size check
│   ├── admin.py
│   ├── context_processors.py   # Menu categories, contact links, currency
│   ├── middleware.py           # Indexing control
│   ├── urls.py
│   ├── templates/catalogue/    # Page templates and product card
│   └── tests.py
├── templates/                  # base.html, 404.html, _whatsapp_icon.html
├── static/img/                 # Logo and page photos you supply
├── media/                      # Uploaded images (not in Git)
├── staticfiles/                # collectstatic output (not in Git)
├── manage.py
├── pyproject.toml
├── uv.lock
├── requirements.txt            # Generated from uv.lock
└── .env                        # Secrets and settings (not in Git)
```

### How a page is served

1. A request arrives and Django matches the URL.
2. The view queries the database. Public views always start from `Product.objects.published()`.
3. A template turns the data into HTML.

### Design decisions

- **Draft visibility is decided in one place.** `Product.objects.published()` is the only filter that decides what the public sees.
- **Publication status and availability are separate.** A product can be live and sold out, or hidden and in stock.
- **Validation has two layers.** Model `clean()` gives friendly messages in the admin. Database constraints back up the price and image rules.
- **Categories cannot be deleted while products use them.** Owners deactivate a category instead.
- **Enquiries are saved before the visitor is told they were received.**
- **Brand details live in configuration, not templates.**
- **Indexing is off unless enabled.**

---

## Getting started

### Prerequisites

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.12 or newer (uv can install it)

### Setup

```bash
git clone https://github.com/YOUR-USERNAME/solvaara.git
cd solvaara
uv sync
```

Create a `.env` file (see [Environment variables](#environment-variables)) and generate a secret key:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Then:

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin is at the path set in `DJANGO_ADMIN_URL`, or `/admin/` if it is not set.

### Images you supply

These files are not in the repository. If one is missing, that image simply does not appear.

| File                                                      | Used for                     |
| --------------------------------------------------------- | ---------------------------- |
| `static/img/logo.png`                                   | Header, menu and footer      |
| `static/img/hero-main.jpg`                              | Homepage hero portrait (3:4) |
| `static/img/hero-1.jpg`, `hero-2.jpg`, `hero-3.jpg` | Homepage hero side photos    |
| `static/img/about.jpg`                                  | Our Story page               |

Product and category photos are uploaded through the admin.

### Useful commands

```bash
uv run python manage.py check
uv run python manage.py test catalogue
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py shell
```

---

## Environment variables

Settings are read from the environment, and from `.env` in development. **Never commit `.env`.**

| Variable                                                                  | Purpose                                                                                      |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `DJANGO_SECRET_KEY`                                                     | Django's secret key. The project will not start without it.                                  |
| `DJANGO_DEBUG`                                                          | `True` for local development. Anything else, or missing, means off.                        |
| `DJANGO_ALLOWED_HOSTS`                                                  | Comma-separated host names the site may serve.                                               |
| `DJANGO_CSRF_TRUSTED_ORIGINS`                                           | Comma-separated origins, with `https://`, allowed to submit forms in production.           |
| `DJANGO_ADMIN_URL`                                                      | Admin path ending in `/`. Default `admin/`. Use a long, unguessable value in production. |
| `DJANGO_SITE_URL`                                                       | The public address, with no trailing slash. Used to build absolute links.                    |
| `DJANGO_ALLOW_INDEXING`                                                 | `True` lets search engines index the site. Anything else, or missing, blocks indexing.     |
| `DJANGO_WHATSAPP_NUMBER`                                                | Business WhatsApp number, digits only, with country code.                                    |
| `DJANGO_CONTACT_EMAIL`                                                  | Public contact email. Hidden when empty.                                                     |
| `DJANGO_CONTACT_PHONE`                                                  | Public phone number. Hidden when empty.                                                      |
| `DJANGO_CONTACT_ADDRESS`                                                | Shop address. Leave empty for an online-only or fictional brand.                             |
| `DJANGO_OPENING_HOURS`                                                  | Opening hours text.                                                                          |
| `DJANGO_INSTAGRAM_URL`, `DJANGO_FACEBOOK_URL`, `DJANGO_YOUTUBE_URL` | Social links. Each icon appears only when set.                                               |

Example local `.env`:

```
DJANGO_SECRET_KEY='replace-with-a-generated-key'
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_ADMIN_URL=studio-7f3k/
```

`DEBUG` and indexing both default to off, so a forgotten setting fails safe. Only put real details in the contact variables.

---

## Pages and URLs

| URL                   | Page                                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------- |
| `/`                 | Homepage                                                                                             |
| `/shop/`            | Catalogue. Accepts `?q=`, `?category=`, `?min_price=`, `?max_price=`, `?sort=`, `?page=` |
| `/products/<slug>/` | Product detail                                                                                       |
| `/our-story/`       | About page                                                                                           |
| `/contact/`         | Contact page and enquiry form                                                                        |
| `/policies/<page>/` | `shipping`, `returns`, `privacy` or `terms`                                                  |

Unknown products and policy pages return a 404. Draft products and inactive categories are never reachable by the public.

---

## Data model

```
Category ──< Product ──< ProductImage

Enquiry (standalone)
```

### Category

| Field              | Notes                                                                           |
| ------------------ | ------------------------------------------------------------------------------- |
| `name`, `slug` | The slug is unique.                                                             |
| `description`    | Optional. Shown on homepage tiles.                                              |
| `display_order`  | Lower numbers come first. The first active category is the large homepage tile. |
| `image`          | Optional. Used on the homepage tile.                                            |
| `is_active`      | Inactive categories and their products are hidden from the public.              |

### Product

| Field                                                                      | Notes                                                          |
| -------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `name`, `slug`                                                         | The slug is unique.                                            |
| `sku`                                                                    | Product code. Optional, unique when present, stored uppercase. |
| `category`                                                               | Required.                                                      |
| `short_description`, `description`                                     | Optional.                                                      |
| `price`, `sale_price`                                                  | Optional. The sale price must be below the price.              |
| `material`, `plating`, `colour`, `dimensions`, `available_sizes` | Optional. Enter only verified facts.                           |
| `availability_status`                                                    | `available`, `sold_out` or `made_to_order`.              |
| `publication_status`                                                     | `draft` (default) or `published`.                          |
| `main_image`, `main_image_alt`                                         | Both required to publish.                                      |
| `is_featured`                                                            | Shows the product in the homepage "Selected for You" section.  |
| `published_at`                                                           | Set the first time a product is published.                     |

### ProductImage

Extra gallery photos for a product, with `alt_text` and `display_order`. Deleted with the product.

### Enquiry

Messages from the contact form: name, email, optional phone, message, status (`new`, `in_progress`, `closed`) and date.

### Rules enforced

| Rule                                    | Enforced by                                            |
| --------------------------------------- | ------------------------------------------------------ |
| Slugs are unique                        | Database                                               |
| Product codes are unique when provided  | Database                                               |
| Prices are not negative                 | Validators and a database constraint                   |
| Sale price is below the regular price   | `clean()` and a database constraint                  |
| Published products have a main image    | `clean()`, the bulk action and a database constraint |
| Published products have image alt text  | `clean()` and the bulk action                        |
| Drafts never appear publicly            | `Product.objects.published()`                        |
| Uploads are JPG, PNG or WebP under 5 MB | Field validators                                       |

---

## Using the admin

Only staff accounts can sign in.

**Categories.** Add categories such as Earrings or Necklaces. Set the display order, upload an image for the homepage tile, and untick "is active" to hide one without deleting it. The slug fills in from the name.

**Products.** Products start as drafts. Fill in the sections, add extra photos in the table at the bottom, and always describe the main photo in "main image alt". Leave the price empty to show "Price on Enquiry". Use the filters and search box (name or code) to find products.

**Bulk actions.** On the product list, tick products and choose *Publish selected* or *Unpublish selected*. Products with no main image or no image description are skipped, and the message says how many. The original publication date is kept if a product is unpublished and republished.

**Enquiries.** The Enquiries list shows each message. Search by name, email or text, filter by status, and change the status. The message details are read-only.

---

## Customer enquiries

There are two routes, and they behave differently:

1. **WhatsApp.** The product page button opens WhatsApp with a message naming the product, its code and its page address. This is only a link. **Nothing is saved on the website.**
2. **Contact form.** The message is saved to the database and appears in the admin. It has CSRF protection, a hidden spam field, server-side validation and a limit of five enquiries per hour per connection.

No email is sent. The owner has to check the admin for new enquiries.

---

## Design

Colours, fonts and spacing are set in the Tailwind configuration inside `templates/base.html`.

| Token                        | Value       | Use                              |
| ---------------------------- | ----------- | -------------------------------- |
| `surface`                  | `#fcf9f3` | Main background                  |
| `surface-container-low`    | `#f6f3ed` | Alternate sections               |
| `surface-container-lowest` | `#ffffff` | Cards and photo mats             |
| `primary`                  | `#130e0a` | Text and primary buttons         |
| `on-surface-variant`       | `#4d4540` | Secondary text                   |
| `secondary`                | `#795924` | Antique gold, for text and links |
| `tertiary-container`       | `#44141b` | Maroon hover and accents         |
| `outline-variant`          | `#d0c4bd` | Borders                          |

- **Fonts:** Bodoni Moda for headings, Manrope for body text and labels.
- **Style:** light, warm and editorial, with sharp corners and no heavy gold or dark backgrounds.
- **Wording:** the site never says "Buy" or "Shop now". Actions read "Enquire on WhatsApp" or "Explore the Collection".
- **Motion:** smooth scrolling, scroll reveals and hover effects switch off for visitors who prefer reduced motion. Hover lifts are also off on touch screens.

---

## Testing

### Automated

`catalogue/tests.py` covers the model rules and the public queryset:

- The sale price must be below the price.
- Publishing requires a main image and its description.
- The database rejects a published product without an image.
- Drafts and products in inactive categories are excluded by `published()`.

```bash
uv run python manage.py test catalogue
```

### Checked by hand

- The sale price rule, in the Django shell.
- Rejection of publishing without a main image.
- Creating categories and products in the admin.
- Bulk publish and unpublish, including skipped products and the kept `published_at` date.

### Not verified

- Public pages, search, filters, sorting and pagination.
- The contact form, spam field and rate limit.
- The WhatsApp link content.
- Rejection of invalid uploads.
- Admin access for anonymous users.
- Keyboard navigation and layouts at common screen widths.
- Persistence of data and images after a host restart, and restoring from a backup.
- The deployment steps below, end to end.

---

## Deployment

The documented setup is a free demo on **PythonAnywhere's free plan**, with SQLite and local image storage. It needs no payment card. Free-plan limits (CPU time, disk space, how often the app must be renewed, available Python versions) change, so **check PythonAnywhere's current free-account page first.**

Replace `YOURUSERNAME` with your PythonAnywhere username.

### Before deploying

1. Generate `requirements.txt`: `uv export --no-dev --no-hashes --no-emit-project -o requirements.txt`
2. Push the project to a public GitHub repository. Check that `git ls-files .env` prints nothing.
3. Check that your PythonAnywhere system image supports Python 3.12 or newer.

### In a PythonAnywhere Bash console

```bash
cd ~
git clone https://github.com/YOUR-USERNAME/solvaara.git
cd solvaara
mkvirtualenv solvaara-venv --python=python3.12
pip install -r requirements.txt
mkdir -p media
```

Generate a secret key and a hidden admin path:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
python -c "import secrets; print(secrets.token_urlsafe(8) + '/')"
```

Create `.env` with `nano .env`:

```
DJANGO_SECRET_KEY='paste-the-key-here'
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOURUSERNAME.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://YOURUSERNAME.pythonanywhere.com
DJANGO_SITE_URL=https://YOURUSERNAME.pythonanywhere.com
DJANGO_ALLOW_INDEXING=False
DJANGO_ADMIN_URL=paste-the-admin-path-here/
```

Add the WhatsApp number and contact email only if they are real. Then:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py check
```

### Web tab

1. Add a new web app: **Manual configuration**, Python 3.12 or 3.13.
2. **Virtualenv:** `/home/YOURUSERNAME/.virtualenvs/solvaara-venv`
3. **Source code:** `/home/YOURUSERNAME/solvaara`
4. Replace the contents of the WSGI configuration file with:

```python
import os
import sys

path = "/home/YOURUSERNAME/solvaara"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

5. **Static files:**

| URL          | Directory                                   |
| ------------ | ------------------------------------------- |
| `/static/` | `/home/YOURUSERNAME/solvaara/staticfiles` |
| `/media/`  | `/home/YOURUSERNAME/solvaara/media`       |

6. Turn on **Force HTTPS**, then click **Reload**.

HTTPS is enforced by the host's Force HTTPS switch. The settings do not include a redirect or proxy-header setting.

### Checking the live site

1. The homepage loads styled, with the logo.
2. Sign in at your admin path, add a category and a published product with a photo, and confirm it appears on the homepage, `/shop/` and its own page.
3. The WhatsApp link's message contains an `https://` address.
4. A test enquiry at `/contact/` appears in the admin.
5. `/does-not-exist/` shows the custom 404 page.
6. After a **Reload**, the product and its photo are still there.

### Updating

```bash
cd ~/solvaara
git pull
workon solvaara-venv
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload**.

### Renewing

Free web apps stop running if they are not renewed. Log in and click the extend button on the Web tab when the host emails you.

### Backups

```bash
cd ~/solvaara
python manage.py dumpdata --indent 2 -e contenttypes -e auth.permission > ~/backup.json
tar czf ~/media-backup.tar.gz media
```

Download both from the **Files** tab. To test a restore, use a scratch copy of the project: run `migrate`, then `python manage.py loaddata backup.json`, and unpack the media archive into `media/`.

### Troubleshooting

Open the **Error log** link on the Web tab first.

| Symptom                           | Likely cause                                                         |
| --------------------------------- | -------------------------------------------------------------------- |
| `DisallowedHost`                | `DJANGO_ALLOWED_HOSTS` does not match the address exactly.         |
| "CSRF verification failed"        | `DJANGO_CSRF_TRUSTED_ORIGINS` is missing or lacks `https://`.    |
| Unstyled admin or missing logo    | The `/static/` mapping is wrong, or `collectstatic` was not run. |
| `KeyError: 'DJANGO_SECRET_KEY'` | `.env` is missing or not inside the project folder.                |
| `No module named config`        | The path in the WSGI file is wrong.                                  |
| Uploaded images give 404          | The `/media/` mapping is wrong, or `media/` does not exist.      |
| Python version error during setup | The account's system image is too old.                               |

---

## Security

- Secrets live in `.env`, which is excluded from Git. If a secret is ever committed or shared, rotate it. Deleting it is not enough.
- Authentication and permissions use Django's built-in system. Give staff accounts only the permissions they need.
- CSRF protection is on for all forms. Session and CSRF cookies are marked secure when `DEBUG` is off.
- Image uploads are limited by extension and size.
- Database access goes through the ORM.
- The admin path is configurable. A hidden path is a small extra barrier, not a replacement for a strong password.
- Every response carries a `noindex, nofollow` header unless `DJANGO_ALLOW_INDEXING=True`. The admin always does.
- The enquiry rate limit counts per connection address in the server's memory.

---

## Limitations

**Search engine optimisation.** Only the indexing switch exists. Pages have no meta descriptions, canonical URLs, sitemap, `robots.txt` or structured data. Category pages use `?category=` query links, not their own URLs. Because indexing is off, the site is not suitable for a public launch yet.

**Hosting.**

- SQLite and local image storage suit a demo, not a busy shop.
- Uploaded photos count against the host's disk allowance, so keep them small.
- The free web app must be renewed periodically.
- There is no automated backup. Backups are manual and must be test-restored.

**Enquiries.**

- No email is sent. The owner must check the admin.
- WhatsApp enquiries are not saved anywhere on the site.
- The rate limit is approximate. It resets on restart and is unreliable behind a proxy or with several workers.

**Content.**

- Policy pages, About text and contact details are placeholders to be replaced by the owner.
- The homepage craftsmanship section links two images hosted elsewhere. They can break and are not licensed for production. Replace them with your own.
- If you do not supply the hero and About photos, those areas show empty frames.

**Performance and images.**

- Tailwind runs from its CDN script. It works, but it is not recommended for production and slows the first render.
- Photos are served at full size, with no resized or WebP versions.
- Core Web Vitals have not been measured.

**Accessibility and front end.**

- Accessibility has not been tested against WCAG 2.2 AA.
- The menu drawer stays keyboard-focusable while closed.
- Product gallery switching and the menu need JavaScript.
- `site.css` and `site.js` are not loaded by the current layout.

**Testing.** Automated tests cover only the model rules. See [Not verified](#not-verified).

---

## Content notes

- Policy pages must contain owner-approved text before the site goes live.
- Do not state gold purity, gemstone, hallmark, durability, origin or authenticity claims unless they are verified for the product.
- Do not invent a shop address, opening hours, ratings or reviews for a fictional brand.
- Photographs from other brands in design references are mood-board material only. Do not use them on the site.


