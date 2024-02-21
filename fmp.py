import json
import urllib.request
import urllib.request
from typing import Optional, Union, Dict

import certifi
from fastapi import HTTPException
from starlette.exceptions import HTTPException

from database import API_KEY


def get_stock_prices(symbol: str) -> dict:
    base_url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={API_KEY}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/91.0.4472.124 Safari/537.36'}
        request = urllib.request.Request(base_url, headers=headers)
        with urllib.request.urlopen(request, cafile=certifi.where()) as response:
            data = response.read().decode("utf-8")
        return json.loads(data)[0]
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=e.code, detail=f"Error al obtener datos de la API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de la API: {str(e)}")



def get_company_rating(symbol: str) -> Optional[Dict[str, Union[str, int, float]]]:
    base_url = f"https://financialmodelingprep.com/api/v3/rating/{symbol}?apikey={API_KEY}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/91.0.4472.124 Safari/537.36'}
        request = urllib.request.Request(base_url, headers=headers)
        with urllib.request.urlopen(request, cafile=certifi.where()) as response:
            data = response.read().decode("utf-8")
        return json.loads(data)
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=e.code, detail=f"Error al obtener datos de la API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de la API: {str(e)}")




if __name__ == '__main__':
    from pprint import pprint

    rating = get_company_rating("NIO")

    prices = get_stock_prices("AAPL")

    pprint(rating)
