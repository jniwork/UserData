import requests

from requests.auth import HTTPBasicAuth


def get_exchange_rates():
    rates = {}

    rate_urls = {
        "usd_rub": "https://xecdapi.xe.com/v1/convert_from?from=USD&to=RUB&amount=1",
        "eur_rub": "https://xecdapi.xe.com/v1/convert_from?from=EUR&to=RUB&amount=1",
        "rub_usd": "https://xecdapi.xe.com/v1/convert_from?from=RUB&to=USD&amount=1",
        "rub_eur": "https://xecdapi.xe.com/v1/convert_from?from=RUB&to=EUR&amount=1",
        "usd_eur": "https://xecdapi.xe.com/v1/convert_from?from=USD&to=EUR&amount=1",
        "eur_usd": "https://xecdapi.xe.com/v1/convert_from?from=EUR&to=USD&amount=1"
    }

    api_id = 'test488234521'
    api_key = 's688uioijgp8v4u6qfvivpvquc'

    for key, url in rate_urls.items():
        rate_data = requests.get(url, auth=HTTPBasicAuth(api_id, api_key)).json()
        mid_value = rate_data.get('to', [{}])[0].get('mid')
        rates[key] = mid_value

    return rates


get_exchange_rates()
