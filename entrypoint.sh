#!/bin/bash
# Entry point script for ATLAS container
# This script starts both the Python agent and Node.js Calendar MCP server

set -e

cd /app/ATLAS

# Export environment variables from .env if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo "Starting ATLAS services..."
echo "================================"

# Start Calendar MCP server in the background
echo "Starting Google Calendar MCP server..."
node google-calendar-mcp/build/index.js &
CALENDAR_PID=$!

# Give it time to start
sleep 2

# Start Python agent
echo "Starting ATLAS agent..."
python -c "from agent import root_agent; root_agent.run()"

# If Python agent exits, kill the Calendar server
kill $CALENDAR_PID 2>/dev/null || true

echo "ATLAS services stopped"
