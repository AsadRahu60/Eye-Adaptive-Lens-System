import csv

def log_row(path: str, row: dict):
    write_header = True
    try:
        with open(path, "r"):
            write_header = False
    except FileNotFoundError:
        write_header = True

    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            w.writeheader()
        w.writerow(row)
