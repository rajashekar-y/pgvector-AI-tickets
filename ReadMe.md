# AI-Powered Support Ticket System

![Dashboard Screenshot](assets/dashboard_screenshot.png) ## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Project Setup](#project-setup)
    - [Database Setup](#database-setup)
    - [Running the Application](#running-the-application)
    - [Running Tests and Demonstrating AI](#running-tests-and-demonstrating-ai)
    - [Accessing the Dashboard](#accessing-the-dashboard)
- [Database Schema](#database-schema)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

This project implements an **AI-powered Support Ticket System** designed to automate and enhance customer support operations. It leverages Large Language Models (LLMs) for intelligent ticket classification and response generation, combined with PostgreSQL and the `pgvector` extension for efficient semantic search on historical support data.

The system aims to streamline the support process by providing:
* Automated categorization, prioritization, and sentiment analysis of incoming tickets.
* AI-suggested responses to accelerate agent workflows.
* The ability to find similar, previously resolved tickets using vector similarity search.
* A real-time analytics dashboard for operational insights.

---

## Key Features

* **Intelligent Ticket Triage:** Automatically classifies tickets by category (e.g., Technical, Billing), assigns priority (Critical, High, Medium, Low), and determines customer sentiment (Positive, Neutral, Frustrated).
* **AI-Suggested Responses:** Generates context-aware draft responses for new tickets using an LLM, leveraging historical solutions.
* **Semantic Search with `pgvector`:** Stores AI embeddings of tickets in PostgreSQL, enabling efficient search for semantically similar resolved tickets to assist agents.
* **Real-time Analytics Dashboard:** A web-based dashboard visualizes key support metrics, ticket trends, and performance indicators.
* **Scalable Backend:** Flask API serves as the core logic, handling AI interactions and database operations.
* **Modular Design:** Separates frontend, backend, and utility scripts for better maintainability and scalability.

---

## Technologies Used

* **Backend:**
    * Python 3.8+
    * Flask (Web Framework)
    * `psycopg2` (PostgreSQL adapter)
    * `python-dotenv` (Environment variable management)
    * `requests` (for API calls in `test_support.py`)
    * `OpenAI` (for LLM interactions and embeddings) - *Can be replaced with your custom LLM*
    * `Flask-CORS` (for Cross-Origin Resource Sharing)
* **Database:**
    * PostgreSQL
    * `pgvector` Extension (for vector storage and similarity search)
* **Frontend:**
    * HTML5, CSS3, JavaScript
    * `Chart.js` (for data visualization)
* **Development Tools:**
    * Git & GitHub
    * Virtual Environments (`venv`)

---

## Architecture

The project follows a client-server architecture:
