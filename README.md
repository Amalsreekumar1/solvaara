# Solvaara

A premium, enquiry-based jewellery catalogue built with Django.

Solvaara is a **fictional** Indian-inspired jewellery brand. The project is a portfolio piece and a reusable catalogue solution for small jewellery shops, boutiques and handmade brands. The shop owner manages products through the Django Admin without editing code. Visitors browse the catalogue and enquire about pieces through WhatsApp.

This is a **product catalogue, not an online store**. There is no cart, checkout, payment processing or customer login.

> **Project status: in development.** The data models and the admin are built and manually tested. The public pages, SEO features, automated tests and deployment are not built yet. See [Project status](#project-status) for exactly what exists.

---

## Contents

- [Features](#features)
- [Project status](#project-status)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Data model](#data-model)
- [Using the admin](#using-the-admin)
- [Design system](#design-system)
- [Testing](#testing)
- [Deployment](#deployment)
- [SEO plan](#seo-plan)
- [Security notes](#security-notes)
- [Known limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Features

### Built

- Categories and products stored in a database.
- Product records with optional prices, sale prices, material, plating, colour, dimensions and sizes.
- Separate **publication status** (draft or published) and **availability** (available, sold out, made to order).
- Multiple images per product, with alternative text and display order.
- Validated image uploads (JPG, PNG or WebP, 5 MB maximum).
- Django Admin set up for the owner: search, filters, grouped form sections, a gallery editor and bulk publish and unpublish actions.
- A single queryset method, `Product.objects.published()`, that decides what the public may see.

### Planned

- Public catalogue with search, category and price filters, sorting and pagination.
- Product detail pages with breadcrumbs and related products.
- WhatsApp enquiry links with a prefilled, correctly encoded message.
- Homepage with a scroll-driven 3D bangle hero (Three.js), with a static fallback.
- Category drawer, search overlay, contact page, policy pages and a custom 404.
- SEO: metadata, canonical URLs, sitemap, robots.txt and structured data.
- Accessibility to a WCAG 2.2 AA target, tested rather than assumed.

---

## Project status

| Area                                                 | Status                                       |
| ---------------------------------------------------- | -------------------------------------------- |
| Django project setup                                 | Done                                         |
| Models (`Category`, `Product`, `ProductImage`) | Done, checked in the Django shell            |
| Admin configuration                                  | Done, checked manually                       |
| Public pages                                         | Not started (the shop page is the next step) |
| Design (Figma)                                       | In progress                                  |
| 3D hero                                              | Not started                                  |
| SEO                                                  | Not started                                  |
| Automated tests                                      | Not written yet                              |
| Deployment                                           | Not started                                  |

"Checked" means tried by hand. No automated test suite exists yet.

---

## Tech stack

| Layer                   | Choice                                                          |
| ----------------------- | --------------------------------------------------------------- |
| Language                | Python 3.12                                                     |
| Framework               | Django (monolith)                                               |
| Templates and front end | Django Templates, HTML5, CSS3, vanilla JavaScript               |
| Database                | SQLite locally, PostgreSQL planned for production               |
| Images                  | Django `ImageField` with Pillow                               |
| Admin                   | Django Admin                                                    |
| Packages                | [uv](https://docs.astral.sh/uv/)                                 |
| 3D hero (planned)       | Three.js, loaded as a static script, with no Node.js build step |
| Design                  | Figma                                                           |

React, Node.js, a headless CMS, microservices and a separate API are deliberately not used.

---

## Architecture

```
solvaara/
├── config/                 # Project-wide configuration
│   ├── settings.py         # Settings, read from environment variables
│   ├── urls.py             # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── catalogue/              # The catalogue app
│   ├── models.py           # Category, Product, ProductImage
│   ├── validators.py       # Image size validation
│   ├── admin.py            # Admin configuration and bulk actions
│   ├── migrations/
│   └── ...
├── static/                 # Project-level static files (CSS, JS, fonts)
├── templates/              # Shared templates (planned)
├── media/                  # Uploaded images, local development only (not in Git)
├── manage.py
├── pyproject.toml          # Dependencies
├── uv.lock                 # Locked dependency versions
└── .env                    # Secrets and local settings (not in Git)
```

### How a page is served

1. A visitor requests a URL.
2. Django matches it against the URL configuration.
3. The matching view asks the database for data. Public views always start from `Product.objects.published()`.
4. A template turns the data into HTML.

### Key design decisions

- **Brand details live in configuration, not in templates**, so the site can be re-skinned for a real shop.
- **Draft visibility is decided in one place**, the `published()` queryset method, so a single forgotten filter cannot leak a draft.
- **Publication status and availability are separate fields.** A product can be live and sold out, or hidden and in stock.
- **Validation works in two layers.** Model `clean()` gives friendly messages in forms and the admin. Database constraints are the backstop for the price rules.
- **Categories cannot be deleted while products use them** (`on_delete=PROTECT`). Owners deactivate a category instead.

---

## Getting started

### Prerequisites

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.12 (uv can install it for you)

### Setup

```bash
git clone https://github.com/YOUR-USERNAME/solvaara.git
cd solvaara

# Install dependencies into .venv (created automatically)
uv sync
```

Create a `.env` file in the project root (see [Environment variables](#environment-variables)), then generate a secret key:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Paste the output into `.env` as `DJANGO_SECRET_KEY`. Then:

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` and sign in with the superuser you created.

### Useful commands

```bash
uv run python manage.py check                 # Check the project for problems
uv run python manage.py makemigrations        # Create migrations after changing models
uv run python manage.py migrate               # Apply migrations
uv run python manage.py shell                 # Open a Python shell with the project loaded
uv add <package>                              # Add a dependency
```

---

## Environment variables

Settings are read from the environment, loaded from `.env` in development. **Never commit `.env`.**

| Variable                 | Purpose                                                               | Example                 |
| ------------------------ | --------------------------------------------------------------------- | ----------------------- |
| `DJANGO_SECRET_KEY`    | Django's secret key. The project refuses to start without it.         | a long random string    |
| `DJANGO_DEBUG`         | `True` for local development. Anything else, or missing, means off. | `True`                |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names the site may serve.                        | `127.0.0.1,localhost` |

Example `.env` for local development:

```
DJANGO_SECRET_KEY=replace-with-a-generated-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

`DEBUG` defaults to off when the variable is missing, so a forgotten setting fails safe.

Further variables will be added for production, such as the database URL, media storage credentials and the business WhatsApp number.

---

## Data model

```
Category ──< Product ──< ProductImage
```

### Category

| Field                          | Notes                                                  |
| ------------------------------ | ------------------------------------------------------ |
| `name`, `slug`             | The slug is unique and used in URLs.                   |
| `description`                | Optional.                                              |
| `display_order`              | Lower numbers appear first in navigation.              |
| `is_active`                  | Inactive categories are hidden from public navigation. |
| `created_at`, `updated_at` | Set automatically.                                     |

### Product

| Field                                                                      | Notes                                                          |
| -------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `name`, `slug`                                                         | The slug is unique.                                            |
| `sku`                                                                    | Product code. Optional, unique when present, stored uppercase. |
| `category`                                                               | Required. Deleting a category with products is blocked.        |
| `short_description`, `description`                                     | Optional.                                                      |
| `price`, `sale_price`                                                  | Optional decimals. The sale price must be below the price.     |
| `material`, `plating`, `colour`, `dimensions`, `available_sizes` | Optional. Enter only verified facts.                           |
| `availability_status`                                                    | `available`, `sold_out` or `made_to_order`.              |
| `publication_status`                                                     | `draft` (default) or `published`.                          |
| `main_image`, `main_image_alt`                                         | A published product requires a main image.                     |
| `is_featured`                                                            | Marks products for the homepage.                               |
| `published_at`                                                           | Set automatically the first time a product is published.       |

### ProductImage

Additional gallery images for a product, with `alt_text` and `display_order`. They are deleted along with the product.

### Rules enforced

| Rule                                    | Enforced by                                |
| --------------------------------------- | ------------------------------------------ |
| Slugs are unique                        | Database                                   |
| Product codes are unique when provided  | Database                                   |
| Prices are not negative                 | Field validators and a database constraint |
| Sale price is below the regular price   | `clean()` and a database constraint      |
| Published products have a main image    | `clean()` and the bulk publish action    |
| Drafts never appear publicly            | `Product.objects.published()`            |
| Uploads are JPG, PNG or WebP under 5 MB | Field validators                           |

---

## Using the admin

The admin lives at `/admin/`. Only staff accounts can sign in.

### Categories

- Add categories such as Earrings, Necklaces, Bangles, Rings and Pendants.
- Set the **display order** to control menu order.
- Untick **is active** to hide a category without deleting it.
- The slug fills in automatically from the name.

### Products

- Fill in the sections: Basics, Pricing, Product details, Images, Status and Dates.
- Products start as **Draft**. They are not visible to the public until published.
- Add extra photos in the **Product images** table at the bottom of the page.
- Always fill in the **main image alt** text. Describe what is visible in the photo.
- Use the sidebar filters and the search box (name or product code) to find products.

### Bulk actions

From the product list, tick products and choose:

- **Publish selected products.** Products without a main image are skipped, and the message says how many.
- **Unpublish selected products.** Moves them back to draft.

Publishing keeps the original publication date even if a product is unpublished and published again.

---

## Design system

The design lives in Figma. Core tokens, which will become CSS custom properties:

| Token        | Value       | Use                                  |
| ------------ | ----------- | ------------------------------------ |
| Ivory        | `#F8F4EB` | Main background                      |
| Sand         | `#E9DFCF` | Alternate sections                   |
| Antique gold | `#A18153` | Lines, ornaments, large accents only |
| Deep gold    | `#7A5E34` | Gold text and links                  |
| Maroon       | `#743D3A` | Heritage section and accents         |
| Brown        | `#493728` | Body text and primary buttons        |

- **Fonts:** Cormorant Garamond (display) and DM Sans (body).
- **Spacing:** 8px base scale. **Breakpoints:** 360, 768, 1024 and 1280.
- **Direction:** light, warm and editorial, with sparing Indian-inspired line art. No heavy gold, glow effects or dark backgrounds.
- **Actions:** the site never says "Buy" or "Shop now". Enquiry actions read "Enquire on WhatsApp", and navigation reads "Explore the collection".
- **Contrast:** antique gold on ivory is too low in contrast for text. Use deep gold or brown for any gold text.

---

## Testing

### Done by hand

- Validation of the sale price rule in the Django shell.
- Rejection of publishing without a main image.
- Draft products excluded by `published()`.
- Admin creation of categories and products.
- Bulk publish and unpublish, including skipping products without images and preserving `published_at`.

### Not yet done

Automated tests, and these scenarios from the project plan:

- Editing a price or description and seeing it on a public page.
- Search and filter behaviour on the public catalogue.
- Unknown product URLs returning 404.
- Correct WhatsApp enquiry content.
- Rejection of invalid uploads in the admin.
- Anonymous users being kept out of the admin.
- Responsive behaviour at common widths.
- Sitemap, canonical URLs and structured data.
- Persistence of data and images after a deployment restart, and restoring from a backup.

Planned tooling: Django's test framework for model, view and admin tests, plus Lighthouse and PageSpeed Insights for performance.

---

## Deployment

Not deployed yet. The requirements for a production setup:

- A host that retains the database and uploaded files across restarts and redeploys. Many free tiers sleep, limit storage, expire databases or use ephemeral disks, so verify a provider's current limits before committing.
- **PostgreSQL** for the database.
- **Persistent object storage or a managed media service** for uploaded images. Local `media/` is for development only.
- `DEBUG=False`, correct `ALLOWED_HOSTS`, HTTPS, and secrets in environment variables.
- A changed admin URL.
- Backups, with a restore that has been tested.
- Some hosts expect `requirements.txt`. It can be generated with `uv export --no-dev -o requirements.txt`.

Deployment instructions will be added here once a host is chosen and the process has been tested.

---

## SEO plan

SEO is built in from the start, not added at the end. The planned work:

- Unique titles and meta descriptions per page.
- Canonical URLs, with deliberate handling of filter and sort URLs.
- `sitemap.xml` containing only published, indexable pages, and a `robots.txt` that references it.
- JSON-LD for `Organization`, `WebSite`, `BreadcrumbList` and `Product`. Prices and availability appear only when real and shown on the page.
- Descriptive image filenames, meaningful alt text, explicit image dimensions, and lazy loading only below the fold.
- Crawlable category links (real `<a href>` elements), even though the drawer menu is hidden until opened.
- Custom 404 page, correct status codes, and redirects when a published product slug changes.
- No indexing of drafts, admin pages or non-production environments.
- Core Web Vitals targets: LCP 2.5 s or less, INP 200 ms or less, CLS 0.1 or less.

No ratings, reviews, stock levels or addresses will be invented. Search Console setup requires the actual site owner, and instructions will be documented here.

---

## Security notes

- Secrets are kept in `.env`, which is excluded from Git. If a secret is ever committed, rotate it, because deleting the file is not enough.
- Authentication and permissions use Django's built-in system. Staff accounts should have only the permissions they need.
- CSRF protection is on for all state-changing forms.
- Image uploads are limited by type and size.
- Database access goes through the ORM.
- Still to do before production: change the admin URL, add rate limiting or anti-spam for any public form, and review the production security settings.

## Roadmap

1. **Public pages:** serve media in development, then URLs, views, the base template, the shop page and the product page.
2. **Catalogue features:** search, filters, sorting, pagination, category pages and the WhatsApp enquiry link.
3. **Site chrome:** header and drawer, search overlay, contact page, policy pages (placeholder text clearly marked for the owner) and a custom 404.
4. **Homepage:** category collection, featured products, new arrivals and the craftsmanship interlude.
5. **3D hero:** an isolated Three.js script with a static fallback and reduced-motion support.
6. **SEO, accessibility and security** work from the plan above.
7. **Automated tests**, then **deployment** with persistent media and backups.

---

## Content notes

- Policy pages (shipping, returns, privacy, terms) must contain owner-approved content. Placeholder text will be clearly marked and must be replaced before the site goes live.
- Do not state gold purity, gemstone, durability or authenticity claims unless they are verified for the product.
- Photographs from other brands that appear in design references are mood-board material only. They must not be used on the site.

## Licence

Not yet chosen. Add a licence file before sharing the code publicly with an intention to reuse.
