import requests
from datetime import datetime, timedelta

# Базовый URL и параметры для каждой биржи
base_url_okex = "https://www.okex.com"
endpoint_okex_history = "/api/v5/public/funding-rate-history"

base_url_binance = "https://fapi.binance.com"
endpoint_binance = "/fapi/v1/fundingRate"

base_url_bybit = "https://api.bybit.com"
endpoint_bybit = "/v5/market/funding/history"

# Задаем пары для каждой биржи
symbol_okex = "TRB"
symbol_binance_bybit = symbol_okex+"USDT"

instId = symbol_okex + "-USDT-SWAP"  # Формат для SWAP на OKEX

# Даты начала и конца
start_date_str = "2023-09-01"
end_date_str = "2023-09-30"
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

# Проверка на дату из будущего
current_date = datetime.now()
if end_date > current_date:
    end_date = current_date

days_passed = (end_date - start_date).days

# OKEX
params_okex = {
    "instId": instId,
    "limit": "100"
}
response_okex = requests.get(base_url_okex + endpoint_okex_history, params=params_okex)
data_okex = response_okex.json()["data"]
sorted_data_okex = sorted(data_okex, key=lambda x: x["fundingTime"], reverse=True)
filtered_data_okex = [item for item in sorted_data_okex if int(item["fundingTime"]) / 1000 >= start_date.timestamp() and int(item["fundingTime"]) / 1000 <= end_date.timestamp()]
total_funding_rate_okex = sum([float(item["fundingRate"]) for item in filtered_data_okex])
corrected_apr_okex = (total_funding_rate_okex / days_passed) * 365
print(f"OKEX - Fundings {symbol_okex} from {start_date_str} to {end_date.strftime('%Y-%m-%d')} ({days_passed} days with {len(filtered_data_okex)} fundings): {total_funding_rate_okex * 100:.4f}%")
print(f"APR: {corrected_apr_okex * 100:.4f}%")
print()

# Binance
params_binance = {
    "symbol": symbol_binance_bybit,
    "startTime": int(start_date.timestamp() * 1000),
    "endTime": int(end_date.timestamp() * 1000),
    "limit": 1000
}
response_binance = requests.get(base_url_binance + endpoint_binance, params=params_binance)
data_binance = response_binance.json()
total_funding_rate_binance = sum([float(item["fundingRate"]) for item in data_binance])
average_daily_funding_rate_binance = total_funding_rate_binance / days_passed
apr_binance = average_daily_funding_rate_binance * 365
print(f"Binance - Fundings {symbol_binance_bybit} from {start_date_str} to {end_date.strftime('%Y-%m-%d')} ({days_passed} days with {len(data_binance)} fundings): {total_funding_rate_binance * 100:.4f}%")
print(f"APR: {apr_binance * 100:.4f}%")
print()

# Bybit
category_bybit = "linear"
all_data_bybit = []
while start_date < end_date:
    end_time_temp = start_date + timedelta(days=1)
    params_bybit = {
        "category": category_bybit,
        "symbol": symbol_binance_bybit,
        "startTime": int(start_date.timestamp() * 1000),
        "endTime": int(end_time_temp.timestamp() * 1000),
        "limit": 200
    }
    response_bybit = requests.get(base_url_bybit + endpoint_bybit, params=params_bybit)
    json_data_bybit = response_bybit.json()
    data_bybit = json_data_bybit["result"]["list"]
    if not data_bybit:
        break
    all_data_bybit.extend(data_bybit)
    start_date = end_time_temp + timedelta(seconds=1)
total_funding_rate_bybit = sum([float(item["fundingRate"]) for item in all_data_bybit])
corrected_apr_bybit = (total_funding_rate_bybit / days_passed) * 365
print(f"Bybit - Fundings {symbol_binance_bybit} from {start_date_str} to {end_date.strftime('%Y-%m-%d')} ({days_passed} days with {len(all_data_bybit)} fundings): {total_funding_rate_bybit * 100:.4f}%")
print(f"APR: {corrected_apr_bybit * 100:.4f}%")
