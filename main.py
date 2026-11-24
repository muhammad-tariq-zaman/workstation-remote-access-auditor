"""Audit remote access (RDP) on workstations.

Usage: python3 main.py remote.csv
CSV columns: workstation,rdp_enabled,allowed_users,
last_remote_login_days. allowed_users is a semicolon-separated
list and may be empty; last_remote_login_days is how many days
ago the last remote login was. Verdicts:
- OPEN RDP: RDP is enabled and no allowed users are listed,
  so anyone on the network can try to log in.
- STALE ACCESS: RDP is enabled with users listed, but nobody
  has logged in remotely for over 60 days.
- RDP OK: RDP is enabled, users are listed, and someone logged
  in remotely within the last 60 days.
- RDP OFF: RDP is disabled.
OPEN RDP first, then STALE ACCESS, then RDP OK, then RDP OFF.
Rows with a non-numeric last_remote_login_days or an
rdp_enabled value other than yes/no are reported as skipped,
not silently dropped.
"""
import argparse, csv, sys

VERDICT_ORDER = {"OPEN RDP": 0, "STALE ACCESS": 1, "RDP OK": 2, "RDP OFF": 3}
STALE_DAYS = 60

def audit(rows):
    out = []
    skipped = 0
    for row in rows:
        try:
            workstation = row["workstation"].strip()
            rdp = row["rdp_enabled"].strip().lower()
            users = [u.strip() for u in row["allowed_users"].split(";") if u.strip()]
            days = int(row["last_remote_login_days"])
            if not workstation or rdp not in ("yes", "no"):
                raise ValueError("bad value")
        except (KeyError, AttributeError, ValueError, TypeError):
            skipped += 1
            continue
        if rdp == "no":
            verdict, detail = "RDP OFF", "remote access disabled"
        elif not users:
            verdict = "OPEN RDP"
            detail = "RDP enabled, no allowed users listed"
        elif days > STALE_DAYS:
            verdict = "STALE ACCESS"
            detail = (f"RDP enabled for {', '.join(users)}, "
                      f"no remote login for {days} day(s)")
        else:
            verdict = "RDP OK"
            detail = (f"RDP enabled for {', '.join(users)}, "
                      f"last remote login {days} day(s) ago")
        out.append((workstation, verdict, detail))
    out.sort(key=lambda r: (VERDICT_ORDER[r[1]], r[0]))
    return out, skipped

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args(argv)
    with open(args.path, newline="", encoding="utf-8") as f:
        results, skipped = audit(list(csv.DictReader(f)))
    for workstation, verdict, detail in results:
        print(f"{workstation}: {verdict} - {detail}")
    counts = {v: sum(1 for _, verdict, _ in results if verdict == v)
              for v in VERDICT_ORDER}
    print(f"{counts['OPEN RDP']} open RDP, {counts['STALE ACCESS']} stale access, "
          f"{counts['RDP OK']} ok, {counts['RDP OFF']} off out of "
          f"{len(results)} workstation(s).")
    if skipped:
        print(f"Skipped {skipped} invalid row(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
