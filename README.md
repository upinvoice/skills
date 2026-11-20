# UpInvoice skills

Agent skills for [UpInvoice](https://upinvoice.eu), the AI extraction service that turns a PDF, scan or phone photo of an invoice or order into structured JSON: supplier or customer, references, dates, totals, VAT and product lines. Lines are checked against the document totals before the response is returned.

| Skill | What it does |
|-------|--------------|
| [`upinvoice-api`](skills/upinvoice-api/SKILL.md) | Teaches an agent to call the UpInvoice REST API for supplier invoices, supplier orders and customer orders, handle errors and idempotency, and map the result into an ERP, accounting tool, database or spreadsheet. Includes a standard-library Python helper script. |

The skill follows the open [Agent Skills](https://agentskills.io) format, so it works in any agent that supports `SKILL.md`.

## Install

### Claude Code

```bash
claude plugin marketplace add upinvoice/skills
claude plugin install upinvoice-api@upinvoice
```

Inside a Claude Code session you can also run `/plugin marketplace add upinvoice/skills` and pick `upinvoice-api` from `/plugin`.

### Claude.ai and Claude Desktop

1. Download this repository as a ZIP and extract it.
2. Zip the `skills/upinvoice-api` folder on its own.
3. Upload it in **Settings > Capabilities > Skills**.

### Other agents (Cursor, Codex, Copilot, Windsurf and more)

```bash
npx skills add upinvoice/skills
```

Or copy `skills/upinvoice-api/` into the skills folder your agent reads.

## MCP server

If you want an assistant to extract documents directly instead of writing integration code, connect it to the remote MCP server `https://upinvoice.eu/mcp` (streamable HTTP, header `Authorization: Bearer <key>`). Tools: `process_document` (1 credit per document) and `check_account` (free).

**Claude Code**

```bash
claude mcp add --transport http upinvoice https://upinvoice.eu/mcp   --header "Authorization: Bearer YOUR_API_KEY"
```

**Cursor** (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "upinvoice": {
      "url": "https://upinvoice.eu/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`)

```json
{
  "servers": {
    "upinvoice": {
      "type": "http",
      "url": "https://upinvoice.eu/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

**Claude Desktop** (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "upinvoice": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://upinvoice.eu/mcp",
               "--header", "Authorization: Bearer ${UPINVOICE_API_KEY}"],
      "env": { "UPINVOICE_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

More clients: https://upinvoice.eu/developers/mcp

## Requirements

- An UpInvoice API key. Create one at https://upinvoice.eu/api/tokens (sign-up is free) and expose it as `UPINVOICE_API_KEY`. Never commit it.
- Network access to `upinvoice.eu`.
- Python 3 for the optional helper script.

## Pricing

Each processed document costs one credit. Credits come with a monthly or yearly plan, or as extra credit packs, and every new account gets 10 free documents. Errors and idempotent replays are not charged. See https://upinvoice.eu/prices.

## Documentation

- Developer docs: https://upinvoice.eu/developers
- MCP setup: https://upinvoice.eu/developers/mcp
- OpenAPI 3.1 reference: https://upinvoice.eu/openapi.yaml
- Dolibarr users: the free [UpInvoice module for Dolibarr](https://github.com/upinvoice/module_upinvoice) already calls this API and creates the documents, no custom code needed.

## Contributing

The skill content is maintained by the UpInvoice team. Issues and suggestions are welcome; please open an issue before sending a pull request.

## License

[MIT](LICENSE)
