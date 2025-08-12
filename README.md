# STREAMLIT SQL LIBRARY APP

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Features](#2-features)
- [3. Getting Started](#3-getting-started)
    - [3.1. Prerequisites](#31-prerequisites)
    - [3.2. Installation](#32-installation)
- [4. Project Workflow](#4-project-workflow)
  - [4.1. Database Design And Implementation](#41-database-design-and-implementation)
  - [4.2. Connecting SQL And Python](#42-connecting-sql-and-python)
  - [4.3. Streamlit Application And Deployment](#43-streamlit-application-and-deployment)
- [5. Project Components](#5-project-components)
- [6. Contributors](#6-contributors)

---

## 1. Introduction

This repository holds a group project that demonstrates my ability to build a full-stack data solution from scratch. In this case study, we helped our friend Liane, an avid reader who needed a way to track her borrowed books.

The challenge was to create a user-friendly library management system that was both functional and easy to use. Our solution combines database design and implementation with a intuitive user interface that fully supports CRUD (Create, Read, Update, Delete) operations. This project showcases my skills in applying database theory (normalization, ERDs), connecting SQL and Python with libraries like SQLAlchemy, and building a cloud-ready application using Streamlit. You can explore the app's pages and layout directly in your browser with my live demo, while the local version provides the full, working functionality.

---

## 2. Features

- **Full CRUD Operations**: The application fully supports the creation, reading, updating, and deleting of data, demonstrating full database management.
- **End-to-End Development**: Documents a complete project workflow from initial idea to a deployed, interactive application.
- **Strong Database Fundamentals**: Demonstrates my understanding of database design principles, including entities, relationships, normalization, and constraints.
- **SQL & Python Integration**: Highlights my ability to connect a SQL database with a Python application for seamless data management.
- **User-Friendly Interface**: Features a front-end built with Streamlit, making the complex database system easy for a non-technical user to manage.
- **Live Demo App**: A browser-accessible version of the app is available for a quick look at the layout and functionality. It was reworked with SQLite specifically to make this demo possible.
- **Comprehensive Documentation**: The project's design, schema, and app workflow are fully documented on a Miro board.

---

## 3. Getting Started

To access and review this project, you can explore the documentation and the final app.

### 3.1. Prerequisites
- A web browser
- A running local MySQL instance: This is the database service that hosts the lianes_library schema.
- Python 3.x: To run the Streamlit app.
- Required Python Libraries: You'll need to install the following packages:
  - streamlit
  - sqlalchemy
  - mysql-connector-python

### 3.2. Installation
You can clone this repository and install the required Python libraries to get started.

```bash
# Clone this repository
git clone https://github.com/Cebulva/streamlit_sql_library_app.git

# Navigate into the project directory
cd streamlit_sql_library_app

# Install the required Python packages
pip install -r requirements.txt
```

---

## 4. Project Workflow

My work on this project was a comprehensive process, beginning with a strong database foundation and ending with a user interface.

### 4.1. Database Design And Implementation

This phase was focused on the theory and practice of database design. We defined the necessary entities (books, borrowers) and their relationships, followed normalization principles, and applied MySQL data types and constraints. Finally, I used DDL and DML commands to create and populate the database with the Lianes_Library.sql script.

### 4.2. Connecting SQL And Python

To build the application's functionality, I established a connection between my local MySQL instance and my Python code using SQLAlchemy. This step, managed by the library_connection.py file, allows our Streamlit app to perform CRUD operations on the database using the root user and a password provided at login.

### 4.3. Streamlit Application And Deployment

I used Streamlit to build a user-friendly GUI with simple buttons and forms, allowing Liane to add books, record loans, and track returns without needing to know any code. The app, which starts with Login.py, requires a MySQL password to connect to the local database. As a personal project, I later converted the MySQL database to SQLite to create a self-contained, cloud-deployable version of the app, which is available as a live demo.

---

## 5. Project Components

<details>
<summary>Miro Board Documentation</summary>
<br>
This board documents the full project journey, including the design for the database schema, table entities and attributes, how we used CRUD operations, and the design of the pages for the Streamlit app.
<br>
<a href="https://miro.com/app/board/uXjVIGWwBlk=/?moveToWidget=3458764635099633770&cot=10">View Miro Board</a>
</details>

<details>
<summary>SQL Database Schema And Data</summary>
<br>
This SQL file contains the full schema for the lianes_library database, including the table definitions, constraints, and sample data.
<br>
<a href="https://github.com/Cebulva/streamlit_sql_library_app/blob/main/Data/SQL/Lianes_Library.sql">View SQL File</a>
</details>

<details>
<summary>Streamlit Application Code</summary>
<br>
This folder contains all the Python files for the Streamlit application, including the main login page, the connection logic, and the various pages for managing books, friends, and loans.
<br>
<a href="https://github.com/Cebulva/streamlit_sql_library_app/tree/main/Data/Streamlit">View Streamlit Files</a>
</details>

<details>
<summary>Live Demo App (Streamlit Community Cloud)</summary>
<br>
This demo app is a read-only version of the project, available to view in your browser without any local setup. It uses a SQLite database populated from the repository's Data_SQLite folder. Please note that the write functions (adding, updating, and deleting) are not active in this demo.
<br>
<a href="https://lianes-library-demo.streamlit.app/">View Live Demo App</a>
</details>

---

## 5. Usage

This project is designed to be run locally for the full, interactive experience. Follow these steps to set up the database and launch the application.

1. Set up the Database:
  - Make sure your local MySQL instance is running.
  - Open your MySQL client (e.g., MySQL Workbench or a terminal).
  - Open the Lianes_Library.sql file and run all the commands to create the lianes_library schema and populate it with data.

2. Run the Streamlit App:
  - Open your terminal in the Data/Streamlit directory of this repository.
  - Run the following command to start the application:
  ```bash
  streamlit run Login.py
  ```
  - A web browser window will open, prompting you for your MySQL password to connect to the database.

---

## 6. Contributors

This project was a collaborative effort. I would like to thank the following individuals for their valuable contributions:

- [@camontefusco](https://github.com/camontefusco/): Carlos Montefusco
- [@victoria-vasilieva](https://github.com/victoria-vasilieva): Victoria Vasilieva
- [@azumimuhammed](https://github.com/AzumiMuhammed):Azumi Muhammed
