import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from main import audit

def row(workstation, rdp, users, days):
    return {"workstation": workstation, "rdp_enabled": rdp,
            "allowed_users": users, "last_remote_login_days": str(days)}

class TestRemoteAccessAuditor(unittest.TestCase):
    def test_open_rdp(self):
        r, _ = audit([row("WS-01", "yes", "", 5)])
        self.assertEqual(r[0][1], "OPEN RDP")

    def test_rdp_off(self):
        r, _ = audit([row("WS-02", "no", "", 999)])
        self.assertEqual(r[0][1], "RDP OFF")

    def test_stale_access(self):
        r, _ = audit([row("WS-03", "yes", "ayesha", 90)])
        self.assertEqual(r[0][1], "STALE ACCESS")
        self.assertIn("ayesha", r[0][2])

    def test_exactly_60_days_is_ok(self):
        r, _ = audit([row("WS-03", "yes", "ayesha", 60)])
        self.assertEqual(r[0][1], "RDP OK")

    def test_rdp_ok(self):
        r, _ = audit([row("WS-04", "yes", "bilal; sara", 2)])
        self.assertEqual(r[0][1], "RDP OK")
        self.assertIn("bilal, sara", r[0][2])

    def test_open_rdp_comes_first(self):
        r, _ = audit([row("WS-02", "no", "", 999),
                      row("WS-01", "yes", "", 5)])
        self.assertEqual(r[0][0], "WS-01")

    def test_invalid_row_is_skipped(self):
        r, skipped = audit([row("WS-01", "yes", "ayesha", "recent"),
                            row("WS-02", "no", "", 999)])
        self.assertEqual((len(r), skipped), (1, 1))

    def test_empty_input(self):
        self.assertEqual(audit([]), ([], 0))
