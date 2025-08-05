# Hunguryy - Full-Stack Restaurant Ordering System

This project is a full-stack restaurant ordering system with a frontend built using HTML, CSS, and JavaScript, and a backend powered by Flask and PostgreSQL.

## Features

* **Menu Display:** Dynamically loads the menu from the backend.
* **Shopping Cart:** Allows users to add and remove items from their cart.
* **Order Placement:** Customers can place orders, which are then stored in the database.
* **Table Booking:** Users can book a table for a specific date and time.
* **Online Payments:** Integrated with Razorpay for seamless online payments.
* **Admin Panel:** A simple interface for staff to view and manage orders and bookings.

## Project Structure

hungury/├── backend/│   ├── app.py│   ├── models.py│   ├── Dockerfile│   └── .env.sample├── frontend/│   ├── admin.html│   ├── index.html│   ├── menu.html│   ├── menu_management.html│   ├── order.html│   ├── report.html│   └── Dockerfile└── README.md
## Local Development Setup

### Prerequisites

* Python 3.8+
* PostgreSQL
* Docker (optional, for containerized deployment)

### Backend Setup

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Cors psycopg2-binary python-dotenv razorpay
    ```

4.  **Set up the PostgreSQL database:**
    * Create a new PostgreSQL database.
    * Copy the `.env.sample` file to a new file named `.env`.
    * Update the `.env` file with your PostgreSQL database credentials and a `SECRET_KEY`.

5.  **Initialize the database:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6.  **Run the Flask application:**
    ```bash
    flask run
    ```
    The backend will be running at `http://127.0.0.1:5000`.

### Frontend Setup

1.  **Navigate to the `frontend` directory.**
2.  Open the `.html` files in your browser to view the website. The JavaScript is configured to communicate with the backend running on port 5000.

## Deployment

### Using Docker

1.  **Build the Docker images:**
    ```bash
    # Build the backend image
    docker build -t hungury-backend ./backend

    # Build the frontend image
    docker build -t hungury-frontend ./frontend
    ```

2.  **Run the Docker containers:**
    ```bash
    # Run the backend container
    docker run -d -p 5000:5000 --name hungury-backend-container hungury-backend

    # Run the frontend container
    docker run -d -p 80:80 --name hungury-frontend-container hungury-frontend
    ```

The application will be accessible at `http://localhost`.

---
*This README provides a basic setup guide. For production environments, consider using a production-ready WSGI server like Gunicorn for the Flask application and a more robust database setup.*
