---
name: update-mcp-token-usage
description: Update MCP token usage statistics from /context output
---

Check if the `/context` command has been run in this conversation by looking for context usage statistics in the conversation history.

If context usage statistics are present (showing MCP tools token counts):

1. **Parse the /context output** to extract token counts for each MCP and their tools
2. **Read the existing file** using: `Read("~/.claude/mcp-token-usage.json")`
3. **Update the data** by merging new measurements:
   - Update total_tokens for each MCP
   - Update individual tool token counts
   - Add any new MCPs that weren't previously tracked
4. **Write the updated data** using: `Write("~/.claude/mcp-token-usage.json", updated_json)`
5. **Verify the update** by running: `~/bin/manage-mcps stats`
6. Confirm to user: "✅ Updated token usage for X MCPs in ~/.claude/mcp-token-usage.json"

If context usage statistics are NOT present:
- Tell the user: "Please run `/context` first to display current token usage, then say 'continue' to update the MCP token usage file."
- Wait for the user to run `/context` and say continue before proceeding with the update

**Important**: This command will ACTUALLY UPDATE the JSON file at ~/.claude/mcp-token-usage.json with real token measurements from the /context output.