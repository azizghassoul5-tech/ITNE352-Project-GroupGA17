# utils.py
import json
from datetime import datetime

def send_json(sock, obj):
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    sock.sendall(data)

def recv_line(reader):
    line = reader.readline()
    if line == "":
        return None
    return line.rstrip("\n")

def format_published_at(iso_ts):
    if not iso_ts:
        return "", ""
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    except:
        return iso_ts, ""

