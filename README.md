# workstation-remote-access-auditor

Audit remote access (RDP) on workstations: the input CSV lists workstation, rdp_enabled (yes/no), allowed_users (a semicolon-separated list, may be empty) and last_remote_login_days — OPEN RDP when RDP is enabled and no allowed users are listed, so anyone on the network can try to log in, STALE ACCESS when RDP is enabled with users listed but nobody has logged in remotely for over 60 days, RDP OK when RDP is enabled, users are listed, and someone logged in remotely within the last 60 days, RDP OFF when RDP is disabled — OPEN RDP first, then STALE ACCESS, then RDP OK, then RDP OFF. Rows with a non-numeric last_remote_login_days or an rdp_enabled value other than yes/no are reported as skipped, not silently dropped.

Sample input is included (sample.csv with six workstations, one invalid row).

## How to run

```sh
python3 main.py sample.csv
```

## Example output

```
WS-01: OPEN RDP - RDP enabled, no allowed users listed
WS-03: STALE ACCESS - RDP enabled for ayesha, no remote login for 90 day(s)
WS-05: STALE ACCESS - RDP enabled for omar, no remote login for 75 day(s)
WS-04: RDP OK - RDP enabled for bilal, sara, last remote login 2 day(s) ago
WS-02: RDP OFF - remote access disabled
1 open RDP, 2 stale access, 1 ok, 1 off out of 5 workstation(s).
Skipped 1 invalid row(s).
```

Standard library only. Run the tests with `python3 -m unittest discover`.
