# E-Commerce Platform

A medium-complexity e-commerce platform built with Flask and MySQL.

## Features

- User Authentication & Authorization
- Product Catalog with Categories
- Advanced Search & Filtering
- Shopping Cart
- Order Management
- Payment Simulation
- Admin Dashboard
- Product Reviews & Ratings

## Tech Stack

- **Backend:** Python/Flask
- **Database:** MySQL/MariaDB
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login + JWT
- **Payment:** Custom simulation service

## Project Structure

```
ecommerce-project/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Helper functions
│   ├── static/          # CSS, JS, images
│   └── templates/       # HTML templates
├── migrations/          # Database migrations
├── config.py            # Configuration
├── run.py              # Application entry point
└── seed_data.py        # Database seeding script
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL/MariaDB installed and running

### 2. Clone Repository

```bash
git clone <repository-url>
cd amazon-ecommerce
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` and set your MySQL credentials:
```
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ecommerce_db
```

### 6. Create Database

```bash
mysql -u root -p
CREATE DATABASE ecommerce_db;
exit;
```

### 7. Run Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 8. Seed Database (Optional)

```bash
python seed_data.py
```

This will create sample data including:
- Categories and products
- Test users (admin and customers)
- Sample reviews

### 9. Run Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Sample Credentials

After seeding the database:

- **Admin:** admin@example.com / admin123
- **Customer 1:** john.doe@example.com / password123
- **Customer 2:** jane.smith@example.com / password123

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Products
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get product details
- `GET /api/products/search` - Search products

### Cart
- `GET /api/cart` - Get user's cart
- `POST /api/cart/add` - Add item to cart
- `PUT /api/cart/update` - Update cart item
- `DELETE /api/cart/remove` - Remove item from cart

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user's orders
- `GET /api/orders/<id>` - Get order details

### Admin
- `POST /api/admin/products` - Create product
- `PUT /api/admin/products/<id>` - Update product
- `DELETE /api/admin/products/<id>` - Delete product
- `GET /api/admin/orders` - Get all orders

## Development Progress

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed development phases and progress tracking.

## Database Schema

The application uses the following main tables:
- users
- addresses
- categories
- products
- reviews
- carts
- cart_items
- orders
- order_items
- payments

## License

MIT
