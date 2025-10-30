import csv
import argparse
import os
import matplotlib.pyplot as plt

def read_summary(fpath):
    rows = []
    with open(fpath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', default='results/summary.csv')
    parser.add_argument('--outdir', default='results/plots')
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    rows = read_summary(args.summary)
    
    groups = {}
    for r in rows:
        host = r['host']
        groups.setdefault(host, []).append(r)
    
    for host, recs in groups.items():
        means = [float(r['mean']) if r['mean'] else 0 for r in recs]
        stdevs = [float(r['stdev']) if r['stdev'] else 0 for r in recs]
        idx = list(range(1, len(recs)+1))
        plt.figure()
        plt.errorbar(idx, means, yerr=stdevs, fmt='o-', elinewidth=1, capsize=3)
        plt.title(f'Comparativo: {host}')
        plt.xlabel('Run')
        plt.ylabel('Latencnia (s)')
        plt.grid(True)
        outpng = os.path.join(args.outdir, f"{host.replace('.','_')}_summary.png")
        plt.savefig(outpng)
        plt.close()
        print(f"[PLOT] {outpng}")

if __name__ == '__main__':
    main()
