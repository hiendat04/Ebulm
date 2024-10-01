
# Ebulm: An E-commerce Website for Albums

## Video Demo
[Here](https://www.youtube.com/watch?v=K28nVW7_2gY)

## Project Overview
Ebulm is a Flask-based e-commerce website that allows users to browse, purchase, and manage their albums. The website offers a user-friendly experience for album enthusiasts who want to add albums to their carts, view details, and complete purchases. This project serves as the final submission for CS50x and demonstrates CRUD operations with the integration of an SQLite database, dynamic templating with Jinja, and a Bootstrap-powered frontend for responsiveness.

The project implements common e-commerce functionalities such as user registration, login, profile management, album browsing, and cart handling. Data is stored in an SQLite database (`albums.db`), and Flask is used to manage the backend operations such as user authentication, session management, and database interactions.

## Features
### User Authentication
The application allows users to register, log in, and log out securely. User credentials are stored in a secure manner, ensuring password encryption with industry-standard hashing techniques (Flask’s Werkzeug is likely used here). This feature provides users with a personalized shopping experience, as they can access their account details, view their order history, and make secure transactions.

### Album Browsing
Users can browse through a collection of albums, displayed dynamically from the `albums.db` database. The homepage features a carousel showcasing featured albums, while the shop page displays albums in a paginated format. Each album card includes the album cover, title, artist, and price, giving users an aesthetically pleasing shopping interface.

### Add to Cart & Checkout
The core functionality of the site revolves around the ability to add albums to a shopping cart and proceed to checkout. Users can view their cart, modify quantities, and remove items before finalizing their purchase. The interaction with the database ensures that cart information is saved and updated in real-time. The checkout process is streamlined to ensure a smooth and simple transaction.

### Order History
The website tracks each user’s previous orders, displaying them in an organized table format. This page lists all past orders with essential information such as the album titles, order date, price, and status. This functionality enhances the user experience by providing transparency and accessibility to purchase history.

### Responsive Design
The website is built with Bootstrap, ensuring that the layout is mobile-friendly and adjusts gracefully across devices of different screen sizes. The carousel, navigation bar, and card layout enhance the overall user experience by maintaining a clean and intuitive design.

### Flask & SQLAlchemy
Flask is the core web framework used in the project, while SQLAlchemy is employed to handle database interactions. Using SQLAlchemy provides an Object-Relational Mapping (ORM) solution, allowing efficient management of SQL queries and data retrieval. This design choice improves scalability and flexibility in managing the database.

## File Descriptions

### `app.py`
This is the main Python file that runs the entire application. It handles routes, form submissions, session management, and database interactions. Key routes include:
- `/register`: Handles user registration.
- `/login`: Manages user authentication.
- `/shop`: Displays the available albums with pagination and album details.
- `/add_to_cart`: Processes requests to add albums to the user's shopping cart.
- `/cart`: Displays the items currently in the user’s cart.
- `/checkout`: Handles the purchase and payment processing.
- `/history`: Displays the user's past orders.

Each route connects to different templates and performs necessary CRUD operations on the `albums.db` database. The decision to centralize functionality in `app.py` simplifies project structure while keeping the logic in one place.

### `albums.db`
This SQLite database stores all of the album information, user data, and orders. The database consists of tables like `albums`, `users`, and `orders`. The `albums` table contains details such as `id`, `title`, `artist`, `price`, and `cover`, which are used to dynamically populate the album cards on the frontend. CRUD operations are used extensively to create, read, update, and delete records in response to user actions such as adding to the cart, making a purchase, or registering a new account.

### Templates
All HTML files are stored in the `templates` directory and utilize Jinja for dynamic templating. The key templates include:
- **`layout.html`**: The base template that contains the main structure of the website, such as the header, footer, and navigation bar. Other templates extend from this file to ensure consistency across pages.
- **`register.html`**: The registration form where new users sign up.
- **`login.html`**: The login form for returning users.
- **`shop.html`**: Displays a paginated list of albums available for purchase.
- **`cart.html`**: Displays the items currently in the user's shopping cart.
- **`history.html`**: Shows the user's past orders and relevant details.

### Static Files
All static files (such as images and CSS) are stored in the `static` directory. This includes the album cover images, custom CSS files, and Bootstrap assets that are used for styling.

## Design Decisions
### Pagination for Shop Page
The decision to paginate the shop page was made to improve performance and user experience, especially when dealing with a large number of albums. Displaying all the albums on one page could slow down the site and overwhelm users, so pagination ensures a smooth browsing experience while reducing server load.

### Using SQLAlchemy for Database Management
Although SQLite could be managed directly, SQLAlchemy was chosen for its ORM capabilities, which make it easier to handle relationships between tables and reduce the complexity of raw SQL queries. This design choice also adds flexibility in case the project needs to be scaled up to a more robust database system like PostgreSQL or MySQL in the future.

### Carousel for Featured Albums
The homepage includes a carousel that showcases featured albums. This design choice was made to highlight special albums in a visually appealing and interactive manner, drawing users' attention to new or popular items. JavaScript ensures the carousel functions smoothly with next and previous controls.

### Bootstrap for Responsiveness
The decision to use Bootstrap for CSS and layout structuring was made to ensure that the website remains fully responsive across different devices. This choice provides users with a consistent experience whether they access the site from a desktop, tablet, or mobile device.
