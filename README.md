# Restream for Cursor

Control your Restream account from Cursor through Restream's official remote MCP server.

## What you can do

- Manage streaming events and destinations.
- Review connected channels and event details.
- Work with recordings, storage, clips, live chat, and analytics.
- Authenticate securely with Restream through OAuth 2.1—no API key is required.

## Install

Install **Restream** from the Cursor Marketplace. Cursor connects to:

```text
https://mcp.restream.io/mcp
```

The first tool call opens Restream in your browser so you can sign in and authorize access.

## Verify

Ask Cursor:

> List my connected Restream channels.

Cursor should request permission to call the Restream tools and then return your connected channels.

## Security

The MCP server acts with the permissions of the Restream account you authorize. Keep human confirmation enabled and review write actions before approving them. Only connect to the official endpoint shown above.

Learn more in the [Restream MCP documentation](https://developers.restream.io/mcp-server).

## License

[MIT](LICENSE)
