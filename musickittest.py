import requests

developer_token = ('eyJhbGciOiJFUzI1NiIsImtpZCI6IjZIODhNNVA0VlEiLCJ0eXAiOiJKV1QifQ.eyJpc'
                   '3MiOiJDVzdTWDZQSEJTIiwiaWF0IjoxNzUzMjk2NDM2LCJleHAiOjE3NTMzODI4MzZ9.'
                   'hK5QlaLnGWhrp'
                   'JFYaHB5pkHM2y2LiLfeXcvo8ufo-HQb0_DX8YmQ35zKKGsfSZyEJeVXpB5B8wZxWCSVu3Yuyw')

user_token = ('AnUK2GaYpkyoUE2tsEsdIipqrfvKYnvXjWV6bt5lH62v1ihzme'
              'JNeZdZwxZjvZZxpN5lQMJgWabt9Q6mjBL0qB20wp8k0dDsKWroAnQZP2i4'
              'HUsZd2kr+o2ZkYabMIv91RG3I4RXHd9OPUELZYRItWn4KdY1i1j0Gd73j0A'
              'a1iFO5qnVAWNQ11QfNWXp13sjuofMBjXoHxSqhbz5ZB2H4AfKRMjsQdZOoICoWspi740+6Ftm0Q==')

headers = {
    'Authorization': f'Bearer {developer_token}',
    'Music-User-Token': user_token
}

url = 'https://api.music.apple.com/v1/me/library/playlists'

response = requests.get(url, headers=headers)


if response.status_code == 200:
    print("✅ Success! Playlists retrieved:\n")
    data = response.json()
    for playlist in data.get("data", []):
        print("-", playlist["attributes"]["name"])
else:
    print(f"❌ Failed with status code {response.status_code}")
    print(response.text)