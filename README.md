# JPA — Jair's Personal AI Assistant

A reliable, transparent personal AI assistant built with LangGraph, Claude, and PostgreSQL. Chat via Telegram, manage emails, store facts, and set reminders.

## Features

- **Chat on Telegram**: Direct messaging interface with intelligent responses
- **Email Integration**: Search, summarize, and manage emails from Gmail
- **Memory System**: Store and recall personal facts and information
- **Reminders**: Create tasks and receive notifications at scheduled times
- **Daily Briefing**: Automatic morning summary of tasks, emails, and facts
- **Production Ready**: Runs 24/7 on VPS with systemd, full logging

## Architecture

- **Framework**: LangGraph + LangChain for agentic orchestration
- **LLM**: Claude 3.5 Sonnet (via Anthropic API)
- **Chat**: Telegram bot with webhook
- **Storage**: PostgreSQL for conversations, memories, tasks
- **Scheduling**: APScheduler for reminders and daily briefing
- **Server**: FastAPI + Uvicorn for HTTP API
- **Deployment**: Systemd service on Ubuntu VPS

## Quick Start

### Prerequisites

- Ubuntu 24.04 LTS VPS
- Python 3.12+
- PostgreSQL 16
- Telegram bot token (from @BotFather)
- Claude API key (from console.anthropic.com)
- Gmail OAuth credentials

### Installation

```bash
# Clone repository
git clone https://github.com/jairbakhuis/jpa_v_2.git
cd jpa_v_2

# Copy environment template
cp .env.example ~/.jpa/.env

# Edit with your credentials
nano ~/.jpa/.env

# Run setup script (one time)
bash deploy/setup-vps.sh

# Start service
systemctl start jpa

# Check logs
journalctl -u jpa -f
```

### Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run locally
python src/main.py
```

## Configuration

Environment variables (in `~/.jpa/.env`):

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Telegram
TELEGRAM_TOKEN=123456:ABC...
TELEGRAM_USER_ID=123456789
TELEGRAM_WEBHOOK_URL=https://your-vps-ip/webhook

# Gmail
GMAIL_CREDENTIALS_PATH=/home/jpa/.jpa/gmail_credentials.json
GMAIL_TOKEN_PATH=/home/jpa/.jpa/gmail_token.json

# Database
DATABASE_URL=postgresql://jpa_user:password@localhost/jpa_db

# VPS
VPS_HOST=0.0.0.0
VPS_PORT=8000
TIMEZONE=America/Curacao
```

## Usage

### Chat
Just send messages on Telegram. JPA understands context and can use tools.

### Search Emails
- "What are my latest emails from school?"
- "Show me emails from mom about the kids"
- "Summarize my important emails"

### Manage Memories
- "Remember that Anke is my wife"
- "Who is my wife?"
- "What do you know about me?"

### Create Reminders
- "Remind me to call the doctor at 3 PM"
- "Task: Pick up kids from school at 4 PM"
- "What's on my to-do list?"

## Deployment

### One-Command Deploy

```bash
ssh jpa@your-vps.com
cd ~/jpa_v_2 && git pull && systemctl restart jpa
journalctl -u jpa -f
```

### Manual Monitoring

```bash
# Check service status
systemctl status jpa

# View live logs
journalctl -u jpa -f

# View last 100 lines
journalctl -u jpa -n 100

# Restart service
systemctl restart jpa

# Stop service
systemctl stop jpa

# Test database
psql -h localhost -U jpa_user -d jpa_db -c "SELECT 1;"
```

## Development

### File Structure

```
jpa_v_2/
├── src/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuration
│   ├── agent/
│   │   ├── chatbot_graph.py       # LangGraph chatbot
│   │   ├── tools.py               # Tool definitions
│   ├── integrations/
│   │   ├── telegram_bot.py        # Telegram webhook
│   │   ├── gmail_service.py       # Gmail API
│   │   ├── scheduler.py           # APScheduler
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── connection.py          # Database connection
│   ├── memory/
│   │   └── extraction.py          # Memory extraction
├── deploy/
│   ├── setup-vps.sh               # VPS setup
│   ├── jpa.service                # Systemd service
├── tests/
│   └── test_chatbot.py            # Tests
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                       # This file
```

### Adding Features

1. Add tool to `src/agent/tools.py`
2. Register in tools dict
3. Test with `python -m pytest`
4. Commit and push
5. Deploy: `git pull && systemctl restart jpa`

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_chatbot.py::test_simple_message

# Run with output
python -m pytest tests/ -v -s
```

## Troubleshooting

### Service won't start

```bash
journalctl -u jpa -n 50
systemctl status jpa
```

### Database connection error

```bash
# Test connection
psql -h localhost -U jpa_user -d jpa_db -c "SELECT 1;"

# Check DATABASE_URL in ~/.jpa/.env
nano ~/.jpa/.env
```

### Telegram not responding

```bash
# Check logs for webhook errors
journalctl -u jpa -f

# Verify webhook URL is correct
# It should be: https://your-vps-ip/api/webhook
```

### Gmail not working

```bash
# Check credentials path
ls -la ~/.jpa/gmail_*.json

# If missing, set up OAuth again
# Copy gmail_credentials.json and gmail_token.json from local machine
```

## Security

- `.env` file never committed to Git
- Credentials stored in `/home/jpa/.jpa/` with 700 permissions
- PostgreSQL user is unprivileged
- Systemd service runs as unprivileged jpa user
- TLS recommended for production (use nginx reverse proxy)

## License

Proprietary - Personal use only

## Support

Issues? Check logs: `journalctl -u jpa -f`

For questions about configuration or features, refer to the documentation in `/docs/`.
