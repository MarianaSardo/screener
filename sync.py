import requests


api_url = "https://screener-sw78.onrender.com"
stock_prices_endpoint = "/stock_prices"
company_rating_endpoint = "/company_rating"


response = requests.get(f"{api_url}/instruments")
instrumentos = response.json()


for instrumento in instrumentos:
    symbol = instrumento.get("foreign_symbol")

    if symbol:

        #Update stock prices
        stock_data = {"symbol": symbol}
        requests.put(f"{api_url}{stock_prices_endpoint}/{symbol}", json=stock_data)
        print(f"Stock price actualizado para el símbolo {symbol}")

        # Update company rating
        company_rating_data = {"symbol": symbol}  # Puedes agregar más datos según sea necesario
        requests.put(f"{api_url}{company_rating_endpoint}/{symbol}", json=company_rating_data)
        print(f"Company rating actualizado para el símbolo {symbol}")
    else:
        print("Error: No se pudo obtener el instrumento.")

