#!/usr/bin/env python3
"""Extract one invoice or order with the UpInvoice API and print the JSON result.

Usage:
  UPINVOICE_API_KEY=... python3 upinvoice_extract.py FILE [--type supplier_invoice]
      [--company-name NAME] [--company-tax-id ID] [--idempotency-key KEY]

Standard library only. Exit code 0 on success, 1 on API error, 2 on usage error.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

API_URL = os.environ.get("UPINVOICE_API_URL", "https://upinvoice.eu/api")
TYPES = ("supplier_invoice", "supplier_order", "customer_order")
MIMES = {"application/pdf", "image/jpeg", "image/png"}


def request(method, path, key, body=None, headers=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API_URL + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for name, value in (headers or {}).items():
        req.add_header(name, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as err:
        try:
            payload = json.loads(err.read() or b"{}")
        except ValueError:
            payload = {"success": False, "error": err.reason}
        return err.code, dict(err.headers), payload


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("--type", default="supplier_invoice", choices=TYPES)
    parser.add_argument("--company-name")
    parser.add_argument("--company-tax-id")
    parser.add_argument("--idempotency-key", help="defaults to a new UUID")
    args = parser.parse_args()

    key = os.environ.get("UPINVOICE_API_KEY")
    if not key:
        print("Set UPINVOICE_API_KEY (create one at https://upinvoice.eu/api/tokens)", file=sys.stderr)
        return 2

    mime = mimetypes.guess_type(args.file)[0] or ""
    if mime == "image/jpg":
        mime = "image/jpeg"
    if mime not in MIMES:
        print(f"Unsupported file type {mime or '?'}: convert it to PDF, JPEG or PNG", file=sys.stderr)
        return 2

    with open(args.file, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode()

    body = {"document_type": args.type, "invoice_file": f"data:{mime};base64,{encoded}"}
    if args.company_name:
        body["company_name"] = args.company_name
    if args.company_tax_id:
        body["company_tax_id"] = args.company_tax_id
    idem = args.idempotency_key or str(uuid.uuid4())

    for attempt, wait in enumerate((0, 2, 5, 15)):
        time.sleep(wait)
        try:
            status, headers, payload = request("POST", "/process-document", key, body, {"Idempotency-Key": idem})
        except (urllib.error.URLError, TimeoutError) as err:
            print(f"Network error ({err}), retrying with the same Idempotency-Key", file=sys.stderr)
            continue
        if status == 409:
            time.sleep(int(headers.get("Retry-After", "30")))
            continue
        if status >= 500:
            continue
        break
    else:
        print("Gave up after several retries", file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if status != 200:
        if status == 400:
            _, _, account = request("GET", "/check", key)
            credits = (account.get("data") or {}).get("credits") or {}
            if account.get("success") is False or credits.get("remaining", 1) <= 0:
                print("No credits left: " + str((account.get("links") or (account.get("data") or {}).get("links") or {}).get("add_credits", "")), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
