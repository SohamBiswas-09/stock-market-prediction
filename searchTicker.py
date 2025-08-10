import yfinance as yf
import requests

# Static fallback dictionary
company_to_ticker_map = {
    "TCS": "TCS.NS",
    "INFOSYS": "INFY.NS",
    "WIPRO": "WIPRO.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "RELIANCE": "RELIANCE.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS",
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "AMAZON": "AMZN",
    "GOOGLE": "GOOG",
    "META": "META",
    "TESLA": "TSLA",
    "BERKSHIRE HATHAWAY": "BRK-A",
    "VISA": "V",
    "JPMORGAN CHASE": "JPM",
    "JOHNSON & JOHNSON": "JNJ",
    "WALMART": "WMT",
    "PROCTER & GAMBLE": "PG",
    "MASTERCARD": "MA",
    "BANK OF AMERICA": "BAC",
    "NVIDIA": "NVDA",
    "HOME DEPOT": "HD",
    "ADOBE": "ADBE",
    "CISCO": "CSCO",
    "NETFLIX": "NFLX",
    "PEPSICO": "PEP",
    "LARSEN & TOUBRO": "LT.NS",
    "AXIS BANK": "AXISBANK.NS",
    "KOTAK MAHINDRA BANK": "KOTAKBANK.NS",
    "ULTRATECH CEMENT": "ULTRACEMCO.NS",
    "HCL TECHNOLOGIES": "HCLTECH.NS",
    "MARUTI SUZUKI": "MARUTI.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "TATA STEEL": "TATASTEEL.NS",
    "MAHINDRA & MAHINDRA": "M&M.NS",
    "ASIAN PAINTS": "ASIANPAINT.NS",
    "SUN PHARMACEUTICAL": "SUNPHARMA.NS",
    "DIVI'S LABORATORIES": "DIVISLAB.NS",
    "BRITANNIA INDUSTRIES": "BRITANNIA.NS",
    "NESTLE INDIA": "NESTLEIND.NS",
    "ADANI PORTS": "ADANIPORTS.NS",
    "STATE BANK OF INDIA": "SBIN.NS",
    "POWER GRID": "POWERGRID.NS",
    "SHREE CEMENT": "SHREECEM.NS",
    "INDUSIND BANK": "INDUSINDBK.NS",
    "BAJAJ FINANCE": "BAJFINANCE.NS"
}


def resolve_company_to_ticker(company_name):
    # Input validation
    company_name = company_name.upper()
    if not company_name or not isinstance(company_name, str):
        return None

    # Normalize company name for lookup
    company_name = company_name.strip().upper()

    # Try using static map first
    if company_name in company_to_ticker_map:
        return company_to_ticker_map[company_name]
    else:
        # Try yfinance's search API
            try:
                url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0)"
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an error for bad status codes
                data = response.json()
                if data.get("quotes"):
                    return data["quotes"][0]["symbol"]
            except requests.RequestException as e:
                print(f"Error during API request: {str(e)}")
            except (KeyError, IndexError) as e:
                print(f"Error processing API response: {str(e)}")
    return None

if __name__ == "__main__":
    # Example usage
    company_name = "TCS"  # Replace with the company name you want to search for
    ticker = resolve_company_to_ticker(company_name)
    if ticker:
        print(f"The ticker for {company_name} is {ticker}.")
    else:
        print(f"Could not find a ticker for {company_name}. Please check the company name and try again.")