# UpInvoice plugin for Claude

This plugin adds the `upinvoice-api` skill. It teaches Claude how to extract structured data (supplier, customer, references, dates, totals, VAT and product lines) from supplier invoices, purchase orders and customer orders in PDF or image format with the UpInvoice REST API, and how to build integrations that load that data into an ERP, accounting tool, database or spreadsheet.

## Install

In Claude Code:

```
claude plugin marketplace add upinvoice/skills
claude plugin install upinvoice-api@upinvoice
```

In Claude.ai, add it from the plugin directory.

## Requirements

- An UpInvoice account and API key: https://upinvoice.eu/api/tokens (free sign-up, 10 free documents, no credit card).
- Network access to `upinvoice.eu`.

## What it covers

- Calling `POST /process-document` and `GET /check`, with idempotency and retries.
- Reading the JSON response and mapping it to suppliers, products and document lines.
- The UpInvoice MCP server (`https://upinvoice.eu/mcp`) and the free Dolibarr module.

## Pricing

One credit per processed document. Plans and credit packs: https://upinvoice.eu/prices

## Links

- API documentation: https://upinvoice.eu/developers
- OpenAPI 3.1 reference: https://upinvoice.eu/openapi.yaml
- MCP server: https://upinvoice.eu/developers/mcp
- Source and other install options: https://github.com/upinvoice/skills

## License

MIT
