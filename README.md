# foil-automator

Automated FOIL request tracking, deadline enforcement, and appeal generation for NYS agencies.

Built by [518 Labs](https://github.com/5mil) — open-source government transparency tooling for the 518.

## Purpose

Eliminate the manual burden of tracking FOIL responses across dozens of NYS agencies. Built for journalists, researchers, and civic technologists in New York State.

## Features

- Auto-tracks FOIL requests by agency
- Enforces 5-day acknowledgment / 20-day production deadlines (POL § 89(3))
- Generates appeal letters at 30-day mark (POL § 89(4))
- Exports CSV/JSON for public dashboards
- SQLite backend — zero infrastructure
- Docker-ready
- MIT licensed — free for any use

## Install

```bash
git clone https://github.com/5mil/foil-automator
cd foil-automator
pip install -r requirements.txt
```

## Usage

```bash
# Add a new FOIL request
python main.py add --agency "NYS DMV" --submitted 2026-06-10 --portal https://foil.dmv.ny.gov

# List all tracked requests
python main.py list

# Check overdue requests
python main.py overdue

# Generate appeal letter
python main.py appeal --id 1
```

## Docker

```bash
docker build -t foil-automator .
docker run -v $(pwd)/foil.db:/app/foil.db foil-automator python main.py list
```

## License

MIT — see [LICENSE](LICENSE)
