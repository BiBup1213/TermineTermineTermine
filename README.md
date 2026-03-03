# Siblings Meetup Scheduler

Minimaler Web-Planer ohne Accounts, Werbung oder Tracking.

## Features
- Poll erstellen mit Titel, Beschreibung, Zeitzone und Datumsbereich.
- Share-Link pro Poll (`/p/<pollId>`).
- Admin-Token wird nur einmal angezeigt, serverseitig nur als Hash gespeichert.
- Admin kann Candidate Days setzen und Poll sperren/entsperren.
- Teilnehmende stimmen ohne Login ab (`No -> Maybe -> Yes`), editierbar mit lokalem `participant_token` in `localStorage`.
- Ergebnisse mit Scoring (`yes*2 + maybe*1`), Sortierung, Top-Tage und Matrixansicht.

## Setup lokal (ohne Docker)

### Voraussetzungen
- Python 3.12+
- Node.js 20+

### Backend starten
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows Git Bash: source .venv/Scripts/activate
pip install -e .[dev]
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend starten
In einem zweiten Terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend läuft auf `http://localhost:5173`, Backend auf `http://localhost:8000`.

## Docker starten
```bash
docker compose up --build
```

Danach:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

## Tests (Backend)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Nutzung
1. Auf `/` Poll erstellen.
2. Nach Erstellen Weiterleitung zu `/p/<pollId>`, Share-Link kopieren und teilen.
3. Admin-Token (einmalig sichtbar) kopieren.
4. Auf Poll-Seite im Admin-Bereich Token einfügen, Candidate Days setzen und speichern.
5. Teilnehmende geben Namen ein und markieren pro Candidate Day Verfügbarkeit.
6. Ergebnisse unter `/p/<pollId>/results` ansehen.
7. Optional: Poll per Admin-Token sperren/entsperren.

## API Endpoints
- `POST /api/polls`
- `GET /api/polls/{pollId}`
- `PATCH /api/polls/{pollId}` (Header `x-admin-token`)
- `POST /api/polls/{pollId}/votes`
- `GET /api/polls/{pollId}/results`
