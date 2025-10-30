import subprocess
import statistics
import argparse
import csv
import os
from datetime import datetime

def run_client(host, port, path, requests, matricula, nome, outfile):
    cmd = [
        "python3", "cliente.py",
        "--host", host,
        "--port", str(port),
        "--path", path,
        "--requests", str(requests),
        "--matricula", matricula,
        "--nome", nome,
        "--out", outfile
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res

def parse_csv(file):
    lat = []
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            v = row['latency'].strip()
            if v == '':
                lat.append(None)
            else:
                lat.append(float(v))
    return lat

def summary(latencies):
    valid = [x for x in latencies if x is not None]
    if not valid:
        return {'n': len(latencies), 'mean': None, 'stdev': None, 'min': None, 'max': None}
    return {'n': len(latencies), 'mean': statistics.mean(valid), 'stdev': statistics.pstdev(valid), 'min': min(valid), 'max': max(valid)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', default=80, type=int)
    parser.add_argument('--path', default='/')
    parser.add_argument('--runs', type=int, default=10, help='Executions per scenario (>=10)')
    parser.add_argument('--requests', type=int, default=50, help='Requests per run')
    parser.add_argument('--matricula', default='20229036045')
    parser.add_argument('--nome', default='Walison')
    parser.add_argument('--outdir', default='results')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    summary_file = os.path.join(args.outdir, 'summary.csv')
    with open(summary_file, 'w', newline='') as sf:
        writer = csv.writer(sf)
        writer.writerow(['timestamp','host','port','path','runs','requests','run_idx','n','mean','stdev','min','max','csv_file'])
        for r in range(args.runs):
            out_csv = os.path.join(args.outdir, f"{args.host.replace('.','_')}_{r}.csv")
            print(f"[RUN] host={args.host} run {r+1}/{args.runs} -> {out_csv}")
            res = run_client(args.host, args.port, args.path, args.requests, args.matricula, args.nome, out_csv)
            if res.returncode != 0:
                print("[ERROR] cliente.py retornou código != 0")
                print(res.stdout)
                print(res.stderr)
            lat = parse_csv(out_csv)
            s = summary(lat)
            writer.writerow([datetime.utcnow().isoformat(), args.host, args.port, args.path, args.runs, args.requests, r, s['n'], s['mean'], s['stdev'], s['min'], s['max'], out_csv])
    print(f"[INFO] Sumário salvo em {summary_file}")

if __name__ == '__main__':
    main()
