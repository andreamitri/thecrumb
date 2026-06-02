# 🍞 Crumb & Hearth - Baking Blog Project

## Project Description

Crumb & Hearth is a baking blog web application built using Python, Flask, SQLite, and Jinja2 templates.

The purpose of this project was to practise full-stack web development concepts covered throughout the course, including object-oriented programming, databases, web routing, templates, testing, and version control.

The application allows users to:

- View blog posts
- Create new posts
- Edit existing posts
- Delete posts
- Add comments
- Search for posts
- Browse posts by tag

The project uses a SQLite database to store posts, comments, and tags.

## Technologies Used

- Python
- Flask
- SQLite
- Jinja2
- HTML
- CSS
- Pytest

## Setup and Installation Instructions

### Prerequisites

Make sure Python 3.10 or newer is installed on your computer.

You can check your version by running:

```bash
python --version
```

### Clone the Repository

```bash
git clone https://github.com/andreamitri/thecrumb
```

Move into the project folder:

```bash
cd crumb-and-hearth/thecrumb
```

### Install Dependencies

Install the required packages:

```bash
pip install flask pytest
```

### Create the Database

Run the migration script to create the SQLite database and populate it with sample data:

```bash
python migrate.py
```

---

## How to Run the Application Locally

Start the Flask application:

```bash
python app.py
```

Once the server is running, open your browser and go to:

```text
http://localhost:5000
```

You should now be able to use the application locally.

---

## Running Tests

To run all automated tests:

```bash
python -m pytest tests/ -v
```

To run a specific test file:

```bash
python -m pytest tests/test_blog.py -v
```

or

```bash
python -m pytest tests/test_database.py -v
```

---

## Features

- Create, read, update, and delete blog posts
- Add comments to posts
- Search posts by keyword
- Filter posts by tag
- Display blog statistics
- SQLite database integration
- Server-side validation
- Automated testing with Pytest

---

## Known Limitations

Some limitations of the current version include:

- No user authentication system
- Anyone can edit or delete posts
- Search functionality uses simple SQL matching and is not very advanced
- Images cannot be uploaded with posts
- Styling is basic and not fully responsive on all screen sizes
- Database must be reset manually using the migration script

---

## Future Improvements

If I continue developing this project, I would like to add:

- User accounts and login functionality
- User roles and permissions
- Image upload support
- Improved search features
- Pagination for large numbers of posts
- Better mobile responsiveness
- REST API endpoints
- Deployment to a cloud hosting service

---

## What I Learned

This project helped me gain practical experience with:

- Python programming
- Object-oriented design
- SQLite databases
- Flask web development
- Jinja templates
- Automated testing
- Git version control
- HTTP and web server concepts

Overall, the project allowed me to combine multiple topics from the course into one complete application and gave me a better understanding of how full-stack web applications work.
