# 📈 Stock Market Prediction using Machine Learning

This repository contains a **Stock Market Prediction** application that leverages machine learning models to forecast market trends.  
The project is composed of multiple modules, including **data preprocessing**, **model training**, **prediction interfaces**, and a **user authentication system**.

---

## 📚 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Database Setup](#database-setup)

---

## 📝 Overview
The **Stock Market Prediction** application uses historical financial data and machine learning algorithms to forecast market movements.  
It includes scripts for **data extraction**, **processing**, **visualization**, and a database for managing **user logins** and **prediction history**.

---

## ✨ Features
- 🔐 **User Authentication** with secure login
- 📜 **Prediction History Tracking**
- 🗄 **MySQL Database Integration** for data persistence
- 🧩 **Modular Code Structure** for easy development and contribution
- 📝 **Well-Documented Code** for maintainability

---

## ⚙️ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ShubhamShaw01/StockMarketPrediction.git
cd StockMarketPrediction
```

### 2️⃣ Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env` file with your database credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1234
DB_NAME=stock_database
```

---

## 🐳 Running with Docker

### 1️⃣ Navigate to your project directory
```bash
cd /path/to/your/project
```

### 2️⃣ Build the Docker image
```bash
docker build -t stockmarketprediction .
```

### 3️⃣ Verify the image
```bash
docker images
```

### 4️⃣ Run the container
```bash
docker run -p 8501:8501 stockmarketprediction
```

---

## ▶️ Usage
After installation, run the application:
```bash
python main.py
```
Logs and instructions will appear in the terminal.

---

## 🗄 Database Setup

The application uses a **MySQL database** to store user credentials and prediction history.

### 1️⃣ Connect to MySQL
Example Python connection:
```python
import pymysql as mysql

connection = mysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="1234",
    database="stock_database"
)
```

### 2️⃣ Create Tables
Run the following SQL:
```sql
CREATE TABLE userlogin (
    userName VARCHAR(20) NOT NULL PRIMARY KEY,
    userPassword VARCHAR(255) NOT NULL
);

CREATE TABLE history (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_ticker VARCHAR(10) NOT NULL,
    investment_amount DECIMAL(15,2) NOT NULL,
    final_value DECIMAL(15,2) NOT NULL,
    total_profit DECIMAL(15,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

