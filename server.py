# server.py
import os
import socket
import ssl
import threading
import json
from dotenv import load_dotenv
from fetcher import get_headlines, get_sources
from utils import send_json, recv_line

load_dotenv()

HOST = os.getenv("SERVER_HOST", "0.0.0.0")
PORT = int(os.getenv("SERVER_PORT", "5000"))
GROUP_ID = os.getenv("GROUP_ID", "groupX")
USE_SSL = os.getenv("USE_SSL", "false").lower() == "true"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

clients = {}
clients_lock = threading.Lock()

def save_json(client_name, option, data):
    filename = f"{client_name}_{option}_{GROUP_ID}.json"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def extract_headline_items(data):
    arts = data.get("articles", [])[:15]
    items = [{
        "index": i+1,
        "title": a.get("title"),
        "source": (a.get("source") or {}).get("name"),
        "author": a.get("author")
    } for i, a in enumerate(arts)]
    return items, arts

def extract_source_items(data):
    src = data.get("sources", [])[:15]
    items = [{"index": i+1, "name": s.get("name")} for i, s in enumerate(src)]
    return items, src

def handle_client(conn, addr):
    reader = conn.makefile("r", encoding="utf-8", newline="\n")
    client_name = None
    print(f"[+] Client connected: {addr}")

    try:
        while True:
            line = recv_line(reader)
            if line is None:
                break

            msg = json.loads(line)
            mtype = msg.get("type")

            # HELLO
            if mtype == "hello":
                client_name = msg["client_name"]
                with clients_lock:
                    clients[client_name] = {"last": None}
                send_json(conn, {"type":"ack","message":f"hello {client_name}"})
                continue

            if mtype == "quit":
                send_json(conn, {"type":"ack","message":"goodbye"})
                break

            # REQUEST
            if mtype == "request":
                menu = msg["menu"]
                action = msg["action"]
                params = msg["params"]

                try:
                    if menu == "headlines":
                        api_json = get_headlines(**params)
                        save_json(client_name, "headlines", api_json)
                        items, full = extract_headline_items(api_json)

                        with clients_lock:
                            clients[client_name]["last"] = {"type": "headlines", "raw": full}

                        send_json(conn, {"type":"results","result_type":"headlines","items":items})

                    elif menu == "sources":
                        api_json = get_sources(**params)
                        save_json(client_name, "sources", api_json)
                        items, full = extract_source_items(api_json)

                        with clients_lock:
                            clients[client_name]["last"] = {"type":"sources","raw":full}

                        send_json(conn, {"type":"results","result_type":"sources","items":items})

                except Exception as e:
                    send_json(conn, {"type":"error","message":str(e)})
                    continue

            # SELECT
            elif mtype == "select":
                idx = msg["index"]
                rtype = msg["result_type"]

                with clients_lock:
                    last = clients[client_name]["last"]

                if not last or last["type"] != rtype:
                    send_json(conn, {"type":"error","message":"No results to select from."})
                    continue

                raw = last["raw"]
                if idx < 1 or idx > len(raw):
                    send_json(conn, {"type":"error","message":"Invalid index"})
                    continue

                item = raw[idx-1]

                if rtype == "headlines":
                    detail = {
                        "source": item["source"]["name"],
                        "author": item.get("author"),
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "description": item.get("description"),
                        "publishedAt": item.get("publishedAt")
                    }
                else:
                    detail = {
                        "name": item.get("name"),
                        "country": item.get("country"),
                        "description": item.get("description"),
                        "url": item.get("url"),
                        "category": item.get("category"),
                        "language": item.get("language")
                    }

                send_json(conn, {"type":"details","item":detail})

    finally:
        print(f"[-] Client disconnected: {client_name}")
        conn.close()

def main():
    base = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    base.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if USE_SSL:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain("cert.pem", "key.pem")
        server = context.wrap_socket(base, server_side=True)
    else:
        server = base

    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server running on {HOST}:{PORT}")

    while True:
        c, a = server.accept()
        threading.Thread(target=handle_client, args=(c, a), daemon=True).start()

if __name__ == "__main__":
    main()

