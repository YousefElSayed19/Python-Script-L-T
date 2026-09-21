
f = open("/home/kali/Desktop/500-worst-passwords.txt", "r")
# url for list https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/500-worst-passwords.txt
passwords = f.readlines()

for x in passwords:
    password = x.strip()
    print(password)

