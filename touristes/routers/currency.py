from fastapi import APIRouter, HTTPException
import requests
import os
from cachetools import TTLCache

router = APIRouter(
    prefix="/api/currency",
    tags=["currency"],
)

currency_cache = TTLCache(maxsize=10, ttl=3600)

@router.get("/rates")
async def get_currency_rates():
    cache_key = "currency_rates_USD"
    if cache_key in currency_cache:
        return currency_cache[cache_key]

    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        raise HTTPException(status_code=500, detail="API key for currency conversion is not configured.")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            currency_cache[cache_key] = data
            return data
        else:
            raise HTTPException(status_code=502, detail="Failed to fetch valid data from currency API.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error communicating with currency API: {e}")

@router.get("/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    cache_key = "currency_rates_USD"

    if cache_key not in currency_cache:
        await get_currency_rates()

    rates_data = currency_cache.get(cache_key)
    if not rates_data or "conversion_rates" not in rates_data:
        raise HTTPException(status_code=500, detail="Currency rates are not available in cache.")

    rates = rates_data["conversion_rates"]

    if from_currency not in rates or to_currency not in rates:
        raise HTTPException(status_code=404, detail=f"Currency code not found. Cannot convert from {from_currency} to {to_currency}.")

    amount_in_usd = amount / rates[from_currency]
    converted_amount = amount_in_usd * rates[to_currency]

    return {
        "result": "success",
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "conversion_result": converted_amount
    }
