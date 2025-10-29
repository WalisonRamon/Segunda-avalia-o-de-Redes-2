#!/usr/bin/env python3
"""
server_concurrent.py
Servidor HTTP concorrente usando threads. Usa sockets baixos e trata cada conexão
em uma thread separada.
"""

import socket
import hashlib
import threading
import os
from datetime import datetime

HOST = '0.0.0.0'
PORT = 80
WWW_ROOT = os.path.join(os.path.dirname(__file__), 'www')

MATRICULA = "20229036045"   
NOME = "Walison"           

def compute_x_custom_id(matricula, nome):
    import hashlib
    s = f"{matricula} {nome}".encode('utf-8')
    return hashlib.md5(s).hexdigest()

X_CUSTOM_ID = compute_x_custom_id(MATRICULA, NOME)

def http_response(body: bytes, status_code=200, content_type='text/html; charset=utf-8'):
    status_text = {200: 'OK', 400: 'Bad Request', 404: 'Not Found', 405: 'Method Not Allowed'}.get(status_code, 'OK')
    headers = [
        f"HTTP/1.1 {status_code} {status_text}",
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        f"Server: SimpleConcurrent/1.0",
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        f"X-Custom-ID: {X_CUSTOM_ID}",
        "Connection: close",
        "",
        ""
    ]
    header_bytes = ("\r\n".join(headers)).encode('utf-8')
    return header_bytes + body

def handle_connection(conn, addr):
    try:
        data = conn.recv(8192)
        if not data:
            return
        text = data.decode('utf-8', errors='ignore')
        first_line = text.splitlines()[0] if text.splitlines() else ''
        parts = first_line.split()
        if len(parts) < 3:
            conn.sendall(http_response(b"Bad Request", 400))
            return
        method, path, version = parts[0], parts[1], parts[2]
        if method != 'GET':
            conn.sendall(http_response(b"Method Not Allowed", 405))
            return
        if path == '/':
            path = '/index.html'
        file_path = os.path.join(WWW_ROOT, path.lstrip('/'))
        if not os.path.commonprefix((os.path.realpath(file_path), os.path.realpath(WWW_ROOT))) == os.path.realpath(WWW_ROOT):
            conn.sendall(http_response(b"Not Found", 404))
            return
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            conn.sendall(http_response(b"Not Found", 404))
            return
        with open(file_path, 'rb') as f:
            body = f.read()
        content_type = 'text/html; charset=utf-8' if file_path.endswith('.html') else 'application/octet-stream'
        conn.sendall(http_response(body, 200, content_type))
    except Exception as e:
        try:
            conn.sendall(http_response(b"Internal Server Error", 400))
        except:
            pass
    finally:
        conn.close()

def main():
    os.makedirs(WWW_ROOT, exist_ok=True)
    index_path = os.path.join(WWW_ROOT, 'index.html')
    if not os.path.exists(index_path):
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>Servidor Concorrente</h1><p>Substitua por seu conteúdo.</p></body></html>")

    print(f"[INFO] X-Custom-ID: {X_CUSTOM_ID}")
    print(f"[INFO] Iniciando servidor concorrente em {HOST}:{PORT} ... (serve {WWW_ROOT})")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(256)
        while True:
            conn, addr = s.accept()
            # cria thread para tratar a conexão
            t = threading.Thread(target=handle_connection, args=(conn, addr), daemon=True)
            t.start()
