import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model 
import streamlit as st
from database import authenticate_user, register_user, insert_history, seek_history
from searchTicker import resolve_company_to_ticker
from time import sleep
import os

# ------------------- Session State Init -------------------

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'predict_clicked' not in st.session_state:
    st.session_state.predict_clicked = False
if 'resolved_ticker' not in st.session_state:
    st.session_state.resolved_ticker = ""

# ------------------- Login Page -------------------
def login_page():
    st.set_page_config(page_title="Login", page_icon="🔑", layout="centered")
    st.title("🔐 Login")
    st.subheader("Please log in to continue")

    if st.session_state.get("authenticated"):
        st.success("You are already logged in.")
        return

    email = st.text_input("📧 User Name", key="login_email")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        elif authenticate_user(email, password):
            st.session_state.username = email
            st.session_state.authenticated = True
            st.session_state.page = "main"
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid UserName or password.")

    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.rerun()
# ------------------- Sign Up Page -------------------
def signup_page():
    st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")
    st.title("📝 Sign Up")
    st.subheader("Create a new account")

    email = st.text_input("📧 User Name", key="signup_email")
    password = st.text_input("🔒 Password", type="password", key="signup_password")
    confirm_password = st.text_input("🔒 Confirm Password", type="password", key="signup_confirm")

    if st.button("Create Account"):
        if not email or not password:
            st.warning("All fields are required.")
        elif password != confirm_password:
            st.warning("Passwords do not match.")
            
        else:
            register_user(email, password)
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()
#-------------------- History Page -------------------
def history_page():
    st.set_page_config(page_title="History", page_icon="📜", layout="wide")
    st.title("📜 History")
    st.subheader("Your Investment History")

    if "username" in st.session_state:
        username = st.session_state.username
        seek_history(username)
    else:
        st.warning("You must be logged in to view your history.")
    if st.button("Back to Main"):
        st.session_state.page = "main"
        st.rerun()
# ------------------- Model Loading -------------------
def load_stock_model():
    """Attempt to load the LSTM model with fallback options and detailed error reporting"""
    import traceback
    model_paths = [
        'best_model.keras'
    ]
    for model_path in model_paths:
        if os.path.exists(model_path):
            # Check if file is not empty
            if os.path.getsize(model_path) == 0:
                st.error(f"Model file {model_path} is empty or corrupted.")
                continue
            try:
                model = load_model(model_path, compile=False)
                model.compile(optimizer='adam', loss='mean_squared_error')
                return model
            except Exception as e1:
                try:
                    model = load_model(model_path, compile=True)
                    model.compile(optimizer='adam', loss='mean_squared_error')
                    return model
                except Exception as e2:
                    st.error(f"Failed to load {model_path}: {str(e1)}\n{traceback.format_exc()}")
                    continue
    st.error("Failed to load any model. Please check model files. If you retrained the model, ensure the architecture matches and the file is not corrupted.")
    return None

# ------------------- Currency Symbol Helper -------------------
def get_currency_symbol(currency_code):
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "CHF": "Fr.",
        "SGD": "S$",
        "HKD": "HK$",
        # Add more as needed
    }
    return symbols.get(currency_code, currency_code + " ")

# ------------------- Main Page -------------------
def main():
    st.set_page_config(page_title="Stock Market Price Prediction", page_icon="📈", layout="wide")
    # Position the Logout button to the right using streamlit columns
    cols = st.columns([10, 1])
    with cols[1]:
        if st.button("Logout", key="logout"):
            st.session_state.authenticated = False
            st.session_state.page = "login"
            st.session_state.predict_clicked = False
            st.session_state.resolved_ticker = ""
            st.session_state.username = ""
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📈 Stock Market Price Prediction")
    if "username" in st.session_state:
        cols = st.columns([15, 2])
        cols[0].subheader(f"Welcome, {st.session_state.username}!")
        with cols[1]:
            if st.button("View History"):
                st.session_state.page = "history"
                st.rerun()

    # Load the model using the new function
    model = load_stock_model()
    if model is None:
        return

    # Rest of the main function
    end = datetime.today().strftime('%Y-%m-%d')
    company_name = st.text_input("Enter Company Name", "TCS")
    sleep(3) 
    try:
        if st.button("Resolve & Predict", key="resolve_button"):
            ticker = resolve_company_to_ticker(company_name)
            if ticker:
                st.session_state.resolved_ticker = ticker
                st.session_state.predict_clicked = True
                st.rerun()
            else:
                st.error("Could not find a valid ticker for the given company name.")
    except Exception as e:
        st.error(f"Error resolving ticker: {str(e)}")

    if st.session_state.predict_clicked and st.session_state.resolved_ticker:
        stock = st.session_state.resolved_ticker
        # Get currency code and symbol
        try:
            ticker_info = yf.Ticker(stock).info
            currency_code = ticker_info.get("currency", "INR")
        except Exception:
            currency_code = "INR"
        currency_symbol = get_currency_symbol(currency_code)
        
        data = yf.download(stock, end=end)
        if data.empty:
            st.error("No stock data found. Please check the company name or ticker.")
            return
    # Fetch and display historical data
        data = yf.download(stock, end=end)
        st.subheader("Historical Data")
        st.write(data[::-1])

    #train data from start to today
        data_train=pd.DataFrame(data.Close[0:int(len(data)*0.80)])
        data_test=pd.DataFrame(data.Close[int(len(data)*0.80):int(len(data))])
    #feature scaling
        from sklearn.preprocessing import MinMaxScaler
        scaler=MinMaxScaler(feature_range=(0,1))
        data_train_array=scaler.fit_transform(data_train)
        x=[]
        y=[]
        for i in range(100,data_train_array.shape[0]):
          x.append(data_train_array[i-100:i])
          y.append(data_train_array[i,0])
        x,y=np.array(x),np.array(y)
    #moving average
        st.subheader("Moving Average 100 and 200 days")
        ma_100_days = data['Close'].rolling(100).mean()
        ma_200_days=data.Close.rolling(200).mean()
        fig1=plt.figure(figsize=(18,10))
        plt.plot(ma_100_days,'r',label="100 Days average")
        plt.plot(ma_200_days,'b',label="200 Days average")
        plt.plot(data.Close,'g',label='closing price')
        plt.legend()
        plt.xlabel('No of Days')
        plt.ylabel('Closing Price')
        plt.title(f'{stock} closing price vs 100 days average vs 200 days closing price')
        st.pyplot(fig1)
    #predicting the stock price
        st.subheader("Prediction vs actual price")
        pas_100_days=data_train.tail(100)
        data_test=pd.concat([pas_100_days,data_test],ignore_index=True)
        data_test_array=scaler.fit_transform(data_test)
        x=[]
        y=[]
        for i in range(100,data_test_array.shape[0]):
          x.append(data_train_array[i-100:i])
          y.append(data_train_array[i,0])
        x,y=np.array(x),np.array(y)
        y_predict=model.predict(x)
        scale=1/scaler.scale_
        y_predict=y_predict*scale
        y=y*scale
    #plotting the graph
        fig2=plt.figure(figsize=(12,6))
        plt.plot(y,'b',label='original price')
        plt.plot(y_predict,'r',label='predicted price')
        plt.xlabel('time')
        plt.ylabel('price')
        plt.title("Test Result of the prediction model using LSTM")
        plt.legend()
        st.pyplot(fig2)


    # ----- Improved Next 30 Days Prediction -----
        st.subheader("Next 30 days prediction")
        # Use last 100 days from test set to seed predictions
        inputs = data_test_array[-100:].flatten()
        future_preds_scaled = []
        for _ in range(30):
            x_input = inputs[-100:].reshape(1, 100, 1)
            pred_scaled = model.predict(x_input, verbose=0)[0, 0]
            future_preds_scaled.append(pred_scaled)
            inputs = np.append(inputs, pred_scaled)

        # Optional: Apply a moving average smoothing to reduce prediction noise
        def smooth_predictions(preds, window=3):
            if len(preds) < window:
                return preds
            smoothed = np.convolve(preds, np.ones(window) / window, mode='valid')
            # Prepend the unsmoothed values to maintain the length
            pad_width = len(preds) - len(smoothed)
            return np.concatenate((preds[:pad_width], smoothed))

        # Adjust the smoothing window size as needed
        future_preds_scaled = smooth_predictions(future_preds_scaled, window=3)

        # Inverse transform to original price scale
        future_prices = scaler.inverse_transform(
            np.array(future_preds_scaled).reshape(-1, 1)
        ).flatten()

        # Generate next 30 business days
        future_dates = []
        current_date = datetime.today()
        days_added = 0
        while days_added < 30:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Mon-Fri
                future_dates.append(current_date.date())
                days_added += 1

        # Create predictions DataFrame
        pred_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Price': future_prices
        })
        st.write(pred_df.set_index('Date'))

        # Prepare historical data with Date as a column
        df_hist = data.reset_index().iloc[-100:]
        # Use the future dates and predictions (future_prices) generated earlier
        plt.figure(figsize=(12, 6))
        plt.plot(df_hist['Date'], df_hist['Close'], label='Historical Data')
        plt.plot(pred_df['Date'], pred_df['Predicted_Price'], label='Future Predictions')
        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.title(f"{stock} Price Prediction")
        plt.legend()
        plt.xticks(rotation=45)
        st.pyplot(plt.gcf())
        plt.clf()

        # ----- Optimal Trading Strategy (Multiple Transactions) -----
        st.subheader("Recommended Transaction Plan")
        transactions = []
        n = len(pred_df)
        i = 0
        while i < n - 1:
            # Find buy point (local minima)
            while i < n - 1 and pred_df['Predicted_Price'].iloc[i+1] <= pred_df['Predicted_Price'].iloc[i]:
                i += 1
            buy_idx = i
            # Find sell point (local maxima)
            j = i + 1
            while j < n and pred_df['Predicted_Price'].iloc[j] >= pred_df['Predicted_Price'].iloc[j-1]:
                j += 1
            sell_idx = j - 1
            # Record profitable trade
            if sell_idx > buy_idx:
                transactions.append({
                    'buy_date': pred_df.at[buy_idx, 'Date'],
                    'buy_price': pred_df.at[buy_idx, 'Predicted_Price'],
                    'sell_date': pred_df.at[sell_idx, 'Date'],
                    'sell_price': pred_df.at[sell_idx, 'Predicted_Price']
                })
            i = j

        # Simulate compounding trades

        # Trading recommendations (Optimized for multiple transactions)
        st.subheader("Optimal Trading Strategy")

        # Ensure the predictions DataFrame is sorted by Date
        pred_df = pred_df.sort_values(by="Date").reset_index(drop=True)
        transactions = []
        n = len(pred_df)

        if n < 2:
          st.warning("Insufficient predicted data for a reliable trading strategy.")
        else:
          i = 0
          # Iterate over the predicted days to identify multiple buy-sell opportunities
          while i < n - 1:
            # Find the local minimum (buy point)
            while i < n - 1 and pred_df['Predicted_Price'].iloc[i + 1] <= pred_df['Predicted_Price'].iloc[i]:
              i += 1
            if i == n - 1:
              break
            buy_date = pred_df['Date'].iloc[i]
            buy_price = pred_df['Predicted_Price'].iloc[i]

            # Find the local maximum (sell point)
            j = i + 1
            while j < n and pred_df['Predicted_Price'].iloc[j] >= pred_df['Predicted_Price'].iloc[j - 1]:
              j += 1
            sell_date = pred_df['Date'].iloc[j - 1]
            sell_price = pred_df['Predicted_Price'].iloc[j - 1]

            if sell_price > buy_price:
              transactions.append({
                'buy_date': buy_date,
                'buy_price': buy_price,
                'sell_date': sell_date,
                'sell_price': sell_price
              })
            # Continue from where we left off
            i = j

        # Get user investment amount
        investment = st.number_input(f"Enter Investment Amount ({currency_symbol})", 
                             min_value=1000, 
                             max_value=10000000, 
                             value=1000, 
                             step=1000)

        if st.button("Calculate Profit", key="calculate_profit"):
            current_capital = investment
            transaction_history = []

            for trade in transactions:
                # Calculate the number of shares bought at the buy price
                shares = current_capital / trade['buy_price']
                # Calculate profit from this trade and update the capital for compounding transactions
                profit = shares * (trade['sell_price'] - trade['buy_price'])
                current_capital = shares * trade['sell_price']

                transaction_history.append({
                    'Buy Date': trade['buy_date'].strftime('%Y-%m-%d'),
                    'Buy Price': f"{currency_symbol}{trade['buy_price']:.2f}",
                    'Sell Date': trade['sell_date'].strftime('%Y-%m-%d'),
                    'Sell Price': f"{currency_symbol}{trade['sell_price']:.2f}",
                    'Shares': shares,
                    'Profit': profit,
                    'Total Value': current_capital
                })

            # Display results
            if transaction_history:
                total_profit = current_capital - investment
                roi = (total_profit / investment) * 100

                st.subheader("Recommended Trading Plan")
                st.dataframe(pd.DataFrame(transaction_history))

                st.subheader("Final Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Initial Investment", f"{currency_symbol}{investment:,.2f}")
                with col2:
                    st.metric("Final Value", f"{currency_symbol}{current_capital:,.2f}")
                with col3:
                    st.metric("Total Profit", f"{currency_symbol}{total_profit:,.2f} ({roi:.1f}%)")
                # save history to database
                insert_history(st.session_state.username, company_name, st.session_state.resolved_ticker, investment, current_capital, total_profit)
            else:
                st.warning("No profitable trading opportunities found in the prediction window")
                st.metric("Recommended Action", "Hold Cash", delta_color="off")
#------------------- Routing Logic -------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "main" and st.session_state.authenticated:
    main()
elif st.session_state.page == "history" and st.session_state.authenticated:
    history_page()
else:
    st.warning("You must be logged in to access this page.")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<hr>
<div style="width:100%; text-align:center; font-family:'Segoe UI', sans-serif; font-size:18px; line-height:1.6; padding:10px 0; color:#E0E0E0;">
    <p style="margin-bottom:8px;">© 2025 <span style="color:#00C853;">Made with ❤️ by</span></p>
    
       Group Mentor:
    Chiranjeet Sarkar
    
       Group Members:
    Shubham Shaw
    Debanjan Mukherjee
    Soham Biswas
    Vivek Mondal
    
    All rights reserved
</div>
""", unsafe_allow_html=True)