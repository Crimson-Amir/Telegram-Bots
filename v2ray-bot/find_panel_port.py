import requests

for port in range(0, 65536):
	a = requests.get(f'http://core.silencevpn.online:{port}')
	print(port, a)
	if a.status_code == 200:
		break
