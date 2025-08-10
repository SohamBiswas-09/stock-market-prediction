import pymysql as mysql
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
def get_db_connection():
    try:
        connection = mysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT","12564")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except Exception as e:
        st.error(f"Connection error: {e}")
        st.stop()

def authenticate_user(username, password):
    username = username.strip().lower()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM userlogin WHERE userName=%s AND userPassword=%s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result and result[0] == 1
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False
    finally:
        conn.close()

def register_user(username, password):
    username = username.strip().lower()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM userlogin WHERE userName=%s", (username,))
        if cursor.fetchone()[0] > 0:
            st.warning("Username already exists.")
            return False
        cursor.execute("INSERT INTO userlogin (userName, userPassword) VALUES (%s, %s)", (username, password))
        conn.commit()
        st.success("Account created! Please log in.")
        return True
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False
    finally:
        conn.close()
def insert_history(username, company_name, company_ticker, investment_amount, final_value, total_profit):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO history (username, company_name, company_ticker, investment_amount, final_value, total_profit)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (username, company_name, company_ticker, investment_amount, final_value, total_profit))
            connection.commit()
            st.success("Transaction history saved successfully.")
        except mysql.MySQLError as err:
            st.error(f"Error saving transaction: {err}")
        finally:
            cursor.close()
            connection.close()

def seek_history(username):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "SELECT username, company_name, company_ticker, investment_amount, final_value, total_profit,timestamp FROM history WHERE username = %s order by Id desc"
            cursor.execute(query, (username,))
            history_data = cursor.fetchall()
            if history_data:
                # Adjust the column names to match the actual table schema
                df_history = pd.DataFrame(history_data, 
                    columns=["Username", "Company Name", "Company Ticker", "Investment Amount", "Final Value", "Total Profit", "Transaction Date"])
                st.dataframe(df_history)
            else:
                st.warning("No history found.")
        except mysql.connector.Error as err:
            st.error(f"Error fetching transaction history: {err}")
        finally:
            cursor.close()
            connection.close()