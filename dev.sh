#!/usr/bin/env bash
# ==============================================================================
# SetuAI - Stack Runner (Frontend + Backend + AI Research)
# ==============================================================================

echo "=========================================================="
echo "  Starting SetuAI Linked Stack"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend App: http://localhost:3000"
echo "  - AI Research Engine: Connected via Backend Services"
echo "=========================================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start Backend
(cd "$SCRIPT_DIR/backend" && [ -f ".venv/bin/activate" ] && source .venv/bin/activate; uvicorn main:app --reload --port 8000) &
BACKEND_PID=$!

# Start Frontend
(cd "$SCRIPT_DIR/frontend/gamifiedsetu" && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
