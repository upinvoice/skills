# Integrating UpInvoice output into another system

## Recommended flow

1. `GET /check` once at start-up: validates the key and returns `features.document_types`. Skip document types not listed there.
2. For each file: pick `document_type`, build the data URI, generate an Idempotency-Key and keep it with the file until the result is stored.
3. `POST /process-document`. On a network error or 5xx, retry with the same key (exponential backoff: 2 s, 5 s, 15 s).
4. Validate the result (checklist below). Anything that fails goes to a human review queue instead of being created automatically.
5. Find or create the third party, map the lines, create the document in the target system as a draft.
6. Store the original file next to the created document.

## Validation checklist before creating anything

- `warnings` (orders) is empty.
- Required references are present: `ref_supplier` (invoices) or `ref_document` (orders), and a date.
- The third party has a name or a tax ID.
- Sum of line `total_ht` equals the document `total_ht` within 0.02 (lines flagged `extra` are added after taxes and are excluded from this check). Orders without prices have all amounts at 0.
- `total_ht + total_tva (+ localtax2 if present, usually negative) ≈ total_ttc`.
- The invoice number is not already in the target system for the same supplier (duplicate check).
- If `company_role` is `unknown` on an order, confirm the direction (purchase or sale) with a human.

## Field mapping

| UpInvoice | Generic meaning | Dolibarr | Typical ERP field |
|-----------|-----------------|----------|-------------------|
| `supplier.name` / `thirdparty.name` | Legal name | `societe.nom` | partner name |
| `name_alias` | Trade name | `name_alias` | display name |
| `idprof1` | Tax ID | `idprof1` | tax ID / VAT |
| `tva_intra` | EU VAT number | `tva_intra` | VAT number |
| `country_code` | ISO 3166-1 alpha-2 | `country_code` | country |
| `ref_supplier` | Supplier's invoice number | `ref_supplier` | vendor reference |
| `ref_document` | Order number on the document | `ref_supplier` (supplier order) / `ref_client` (customer order) | external reference |
| `date` / `date_order` | Document date | `datef` / `date_commande` | document date |
| `date_delivery` | Requested delivery | `delivery_date` | delivery date |
| `notes` | Free text | `note_public` | notes |
| line `subprice` | Unit price excl. tax, before discount | `subprice` | unit price |
| line `remise_percent` | Line discount % | `remise_percent` | discount |
| line `tva_tx` | VAT % | `tva_tx` | tax rate (map to the tax code) |
| line `product_type` | 0 product, 1 service | `product_type` | item type |
| line `accounting_code` | Spanish PGC account (3 digits) | accounting account | expense account |

## Matching

- Third parties: compare tax IDs using digits only (`ESB12345678`, `B-12345678` and `12345678` all match), then normalised names (uppercase, no accents or punctuation, without legal forms like SL, SA, GmbH, SARL, Ltd).
- Products: try `product_ref`, then each entry of `product_refs`, against supplier codes, internal references and barcodes; fall back to description search; otherwise create a free-text line.
- Customer orders without prices: use the target system's selling price for that customer and product.

## Credit notes

Supplier credit notes come with negative `total_*` and negative `qty`. If the target system wants positive amounts with a "credit note" flag, invert the signs and set the flag.

## Volume and cost

- One credit per successful document; check `credits.remaining` and `credits.low` from `/check` to warn the user before running out.
- Keep concurrency at 5 or fewer parallel requests.
