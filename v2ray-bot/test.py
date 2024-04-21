import requests

api_key = 'FAQPKPC9GPUJNK84'
api_pass = 'DozkjalXanJStE2bcli2Q6wvjAEIT1Fa'

url = "https://185.215.231.72:4083/index.php"

params = {
    'act': 'listvs',
    'api': 'json',
    'apikey': api_key,
    'apipass': api_pass
}

response = requests.get(url, params=params, verify=False)

print(response.status_code)
print(response.json())  # If the response is JSON
