# client.py
import socket
import ssl
import json
import os
import textwrap
from dotenv import load_dotenv
from utils import send_json, recv_line, format_published_at

load_dotenv()

HOST = os.getenv("SERVER_HOST")
PORT = int(os.getenv("SERVER_PORT"))
USE_SSL = os.getenv("USE_SSL", "false").lower() == "true"

def connect():
    base = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if USE_SSL:
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(base, server_hostname=HOST)
    else:
        sock = base
    sock.connect((HOST, PORT))
    return sock, sock.makefile("r", encoding="utf-8", newline="\n")

def wait(reader):
    line = recv_line(reader)
    if not line:
        print("Server closed connection.")
        exit()
    return json.loads(line)

def show_details(item):
    print("\n--- DETAILS ---")
    for k, v in item.items():
        if k == "description":
            print(textwrap.fill(v or "", width=80))
        elif k == "publishedAt":
            d, t = format_published_at(v)
            print(f"Published at: {d}  {t}")
        else:
            print(f"{k}: {v}")
    print()

def headlines_menu(sock, reader):
    while True:
        print("\nHeadlines Menu")
        print("1) Search keywords")
        print("2) Search category")
        print("3) Search country")
        print("4) List all")
        print("5) Back")
        ch = input("> ")

        params = {}
        if ch == "1":
            params["q"] = input("Keyword: ")
            action = "search_keywords"
        elif ch == "2":
            params["category"] = input("Category: ")
            action = "search_category"
        elif ch == "3":
            params["country"] = input("Country code: ")
            action = "search_country"
        elif ch == "4":
            action = "list_all"
        elif ch == "5":
            return
        else:
            continue

        send_json(sock, {"type":"request","menu":"headlines","action":action,"params":params})
        msg = wait(reader)

        if msg["type"] == "error":
            print("Error:", msg["message"])
            continue

        for it in msg["items"]:
            print(f"{it['index']}) [{it.get('source')}] {it.get('author')} - {it.get('title')}")

        while True:
            i = input("Select index or B: ")
            if i.lower() == "b":
                break
            if not i.isdigit(): continue

            send_json(sock, {"type":"select","result_type":"headlines","index":int(i)})
            d = wait(reader)
            if d["type"] == "error":
                print(d["message"])
                continue
            show_details(d["item"])

def sources_menu(sock, reader):
    while True:
        print("\nSources Menu")
        print("1) Category")
        print("2) Country")
        print("3) Language")
        print("4) List all")
        print("5) Back")
        ch = input("> ")

        params = {}
        if ch == "1":
            params["category"] = input("Category: ")
            action = "src_cat"
        elif ch == "2":
            params["country"] = input("Country: ")
            action = "src_country"
        elif ch == "3":
            params["language"] = input("Language: ")
            action = "src_lang"
        elif ch == "4":
            action = "list_all"
        elif ch == "5":
            return
        else:
            continue

        send_json(sock, {"type":"request","menu":"sources","action":action,"params":params})
        msg = wait(reader)

        if msg["type"] == "error":
            print("Error:", msg["message"])
            continue

        for it in msg["items"]:
            print(f"{it['index']}) {it['name']}")

        while True:
            i = input("Select index or B: ")
            if i.lower() == "b":
                break
            if not i.isdigit(): continue

            send_json(sock, {"type":"select","result_type":"sources","index":int(i)})
            d = wait(reader)
            if d["type"] == "error":
                print(d["message"])
                continue
            show_details(d["item"])

def main():
    sock, reader = connect()

    username = input("Enter username: ").strip()
    if not username: username = "guest"

    send_json(sock, {"type":"hello","client_name":username})
    print(wait(reader)["message"])

    while True:
        print("\nMain Menu")
        print("1) Headlines")
        print("2) Sources")
        print("3) Quit")
        ch = input("> ")

        if ch == "1":
            headlines_menu(sock, reader)
        elif ch == "2":
            sources_menu(sock, reader)
        elif ch == "3":
            send_json(sock, {"type":"quit"})
            print(wait(reader)["message"])
            break

    sock.close()

if __name__ == "__main__":
    main()

