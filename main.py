#!/usr/bin/env python3
"""
foil-automator -- NYS FOIL request tracker & appeal generator
MIT License -- 518 Labs (github.com/5mil)
"""
import argparse
import json
import datetime
import sqlite3
import pathlib
import sys
import textwrap

DB = pathlib.Path(__file__).with_name("foil.db")


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id            INTEGER PRIMARY KEY,
                agency        TEXT,
                submitted     DATE,
                ack_deadline  DATE,
                prod_deadline DATE,
                appeal_by     DATE,
                status        TEXT DEFAULT 'pending',
                portal_url    TEXT,
                notes         TEXT
            )
        """)


def _add_business_days(start: datetime.date, n: int) -> datetime.date:
    d = start
    added = 0
    while added < n:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d


def add_request(agency: str, submitted: str, portal_url: str = "", notes: str = ""):
    sub = datetime.date.fromisoformat(submitted)
    ack = _add_business_days(sub, 5)
    prod = _add_business_days(sub, 20)
    appeal = prod + datetime.timedelta(days=30)
    with sqlite3.connect(DB) as con:
        cur = con.execute(
            "INSERT INTO requests (agency, submitted, ack_deadline, prod_deadline, appeal_by, portal_url, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (agency, sub.isoformat(), ack.isoformat(), prod.isoformat(), appeal.isoformat(), portal_url, notes)
        )
    print(f"Added #{cur.lastrowid}: {agency}")
    print(f"  Submitted:        {sub}")
    print(f"  Ack deadline:     {ack}  (5 business days)")
    print(f"  Production by:    {prod} (20 business days)")
    print(f"  Appeal window:    {appeal} (30 days after prod deadline)")


def list_requests():
    today = datetime.date.today()
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT * FROM requests ORDER BY submitted DESC").fetchall()
    if not rows:
        print("No requests tracked.")
        return
    header = f"{'ID':>3}  {'Agency':<30}  {'Submitted':<12}  {'Ack By':<12}  {'Prod By':<12}  {'Status':<12}"
    print(header)
    print("-" * len(header))
    for r in rows:
        rid, agency, sub, ack, prod, appeal, status, portal, notes = r
        print(f"{rid:>3}  {agency:<30}  {sub:<12}  {ack:<12}  {prod:<12}  {status:<12}")


def overdue_requests():
    today = datetime.date.today().isoformat()
    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT * FROM requests WHERE prod_deadline < ? AND status NOT IN ('produced', 'appealed', 'closed')",
            (today,)
        ).fetchall()
    if not rows:
        print("No overdue requests.")
        return
    print(f"{len(rows)} overdue request(s):")
    for r in rows:
        rid, agency, sub, ack, prod, appeal, status, portal, notes = r
        print(f"  #{rid} {agency} -- prod due {prod} -- appeal by {appeal}")


def generate_appeal(request_id: int):
    with sqlite3.connect(DB) as con:
        row = con.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
    if not row:
        print(f"No request with id {request_id}")
        return
    rid, agency, sub, ack, prod, appeal, status, portal, notes = row
    today = datetime.date.today().strftime("%B %d, %Y")
    letter = textwrap.dedent(f"""\
        TO: FOIL Appeals Officer
        {agency}

        DATE: {today}
        FROM: 0x518 / 518 Labs
        EMAIL: 0x518@protonmail.com
        MAILING: 518 Labs, PO Box [XXXX], Albany, NY 12201
        RE: Appeal of Failure to Respond -- FOIL Request Submitted {sub}

        Pursuant to Public Officers Law Section 89(4)(a) and 21 NYCRR Section 1401.7,
        I hereby appeal the {agency}'s failure to respond to my FOIL request
        submitted on {sub}.

        The agency was required to:
          - Acknowledge receipt within 5 business days (by {ack}) -- POL Section 89(3)
          - Produce records within 20 business days (by {prod}) -- POL Section 89(3)

        Neither deadline was met. This constitutes a constructive denial subject to appeal.

        I respectfully request:
        1. Immediate production of the requested records
        2. Written explanation for the delay
        3. A specific date by which production will be completed

        If this appeal is not resolved within 10 business days, I will seek
        judicial review pursuant to Article 78 of the CPLR and will seek
        attorneys' fees under POL Section 89(4)(c) and CPLR Article 86.

        Respectfully,
        0x518 / 518 Labs
        0x518@protonmail.com
        keybase.io/0x518
        github.com/5mil
    """)
    print(letter)


def main():
    init_db()
    ap = argparse.ArgumentParser(description="NYS FOIL request tracker")
    sub = ap.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="Track a new FOIL request")
    p_add.add_argument("--agency", required=True)
    p_add.add_argument("--submitted", required=True, help="YYYY-MM-DD")
    p_add.add_argument("--portal", default="")
    p_add.add_argument("--notes", default="")

    sub.add_parser("list", help="List all tracked requests")
    sub.add_parser("overdue", help="Show overdue requests")

    p_appeal = sub.add_parser("appeal", help="Generate appeal letter")
    p_appeal.add_argument("--id", type=int, required=True)

    args = ap.parse_args()
    if args.cmd == "add":
        add_request(args.agency, args.submitted, args.portal, args.notes)
    elif args.cmd == "list":
        list_requests()
    elif args.cmd == "overdue":
        overdue_requests()
    elif args.cmd == "appeal":
        generate_appeal(args.id)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
