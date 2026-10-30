"""
AI-Powered Restaurant Management System
Beginner-friendly Streamlit application using SQLite and Google Gemini.
Run: streamlit run app.py
"""

import os
import re
import hmac
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(os.getenv("RESTAURANT_DB_PATH", "restaurant.db"))
CURRENCY = "PKR"
DEFAULT_MODEL = "gemini-2.5-flash"

st.set_page_config(
    page_title="TasteHub | Restaurant Management",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- DATABASE ---------------------------------

def get_connection():
    """Open a SQLite connection and enable foreign-key checks."""
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database():
    """Create all database tables and insert starter menu data once."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS food_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                image_url TEXT DEFAULT '',
                ingredients TEXT DEFAULT '',
                is_available INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Received',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                food_id INTEGER,
                food_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY(food_id) REFERENCES food_items(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                review TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
