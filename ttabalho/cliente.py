#!/usr/bin/env python3
"""
client.py
Envia N requisições HTTP GET para um servidor e mede RTT por requisição.
Uso:
    python3 client.py --host 54.99.0.2 --port 80 --path /index.html --requests 100
"""

import socket
import time
import argparse

def compute_x_custom_id(matricula, nome):
    import hashlib
    s = f"{matricula} {nome}".encode('utf-8')
    return hashlib.md5(s).hexdigest()

def single_request(host, port, path, x_custom_id, timeout=5.0):
    sock = socket.create_connection((host, port), timeout=timeout)
    # Monta requisição HTTP/1.1 com Host e X-Custom-ID
    req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nX-Custom-ID: {x_custom_id}\r\nConnection: close\r\n\r\n"
    start = time.time()
    sock.sendall(req.encode('utf-8'))
    resp = b''
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk
    end = time.time()
    sock.close()
    return end - start, resp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--path', default='/')
    parser.add_argument('--requests', type=int, default=10)
    parser.add_argument('--matricula', default='20229036045') 
    parser.add_argument('--nome', default='Walison')       
    parser.add_argument('--out', default='results_client.csv')
    args = parser.parse_args()

    x_custom = compute_x_custom_id(args.matricula, args.nome)
    results = []
    for i in range(args.requests):
        try:
            latency, resp = single_request(args.host, args.port, args.path, x_custom)
            print(f"[{i+1}/{args.requests}] {latency:.6f}s, resposta {len(resp)} bytes")
            results.append(latency)
        except Exception as e:
            print(f"[{i+1}/{args.requests}] ERRO: {e}")
            results.append(None)

    # Escreve CSV simples: run_index,latency_seconds
    with open(args.out, 'w') as f:
        f.write("idx,latency\n")
        for i, v in enumerate(results):
            f.write(f"{i},{v if v is not None else ''}\n")
    print(f"[INFO] Resultados salvos em {args.out}")

if __name__ == '__main__':
    main()
