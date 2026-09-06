import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Разрешаем запросы с вашего фронтенда на Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.post("/api/save")
def save_data(payload: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем таблицу, если ее нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Сохраняем полученные данные
    import json
    cursor.execute("INSERT INTO user_data (data) VALUES (%s)", (json.dumps(payload),))
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"status": "success", "message": "Data saved successfully"}

@app.get("/api/load")
def load_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT data FROM user_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
@app.post("/api/car-data")
def save_car_data(payload: dict):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_data (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("INSERT INTO car_data (data) VALUES (%s)", (json.dumps(payload),))
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "message": "Car data saved successfully"}

@app.get("/api/car-data")
def load_car_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT data FROM car_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return row[0]
    return {}
