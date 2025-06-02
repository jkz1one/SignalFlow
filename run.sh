#!/bin/bash

SESSION="screener-dev"

# Step 1: Start tmux session
tmux new-session -d -s $SESSION

# Step 2: Activate virtualenv and run scheduler
tmux rename-window -t $SESSION "Scheduler"
tmux send-keys -t $SESSION "source backend/screener-venv/bin/activate && python3 backend/scheduler.py" C-m

# Step 3: New window for sector websocket
tmux new-window -t $SESSION -n "SectorWS"
tmux send-keys -t $SESSION "source backend/screener-venv/bin/activate && python3 backend/signals/sector_signals.py" C-m

# Step 4: New window for FastAPI
tmux new-window -t $SESSION -n "Backend"
tmux send-keys -t $SESSION "source backend/screener-venv/bin/activate && uvicorn backend.main:app --reload --port 8000" C-m

# Step 5: New window for frontend (Next.js — runs from root)
tmux new-window -t $SESSION -n "Frontend"
tmux send-keys -t $SESSION "npm run dev" C-m

# Attach to the session
tmux attach-session -t $SESSION
