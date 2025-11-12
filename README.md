# Tournament Management System

This is a Python-based tournament management system designed for three types of users — **Admin**, **Organizer**, and **Player**.  
It makes it easy for organizers to create events and for players to browse and sign up for active ones (along with their teams), while admins can manage everything from the backend.

---

## Overview

The project was built to simulate how real-world event platforms work. It focuses on role-based access and database-driven operations using Python and MySQL.  
Each user type has different permissions: admins oversee all users and events, organizers manage their own events, and players can register for the ones they’re interested in.

> **Note:** The project uses a MySQL database.  
> Some setup is required to run locally, but this repository is meant to showcase backend structure and logic.

---

## Features

- Separate login and dashboard for Admin, Organizer, and Player  
- Organizers can create, edit, and view events  
- Players can register for events and view active ones  
- Admins can manage users and monitor events 
- PDF Generation to create fixtures for each tournament  
- All data is stored securely in a MySQL database  
- Clean and modular Python code for each user type  

---

## Tech Stack

- **Language:** Python 3.12  
- **Framework:** Flask (for the web interface)  
- **Frontend:** HTML, CSS (Flask templates for user dashboards)  
- **Database:** MySQL  
- **Libraries:** mysql-connector-python, reportlab (for PDF generation)  
- **Tools:** VS Code / PyCharm, Git, GitHub 

---

## Folder Structure

CriterionC/

│

├── main.py # Main entry point

├── database.py # Handles database connection

├── admin.py # Admin-related functions

├── organizer.py # Organizer functions

├── player.py # Player functions

└── README.md

