# Pokémon TCG Deck Efficiency Analyzer

A lightweight Flask web app for analysing Pokémon TCG decklists and estimating how efficiently each card contributes to the deck's game plan.

This is an early MVP designed to be **PythonAnywhere-friendly**:

- small dependency footprint
- no database required
- no large card image/cache downloads
- works from pasted decklists

## Current features

- Paste a Pokémon TCG decklist
- Parses common lines like `4 Nest Ball`, `2x Iono`, or `3 Professor's Research`
- Deck composition summary: Pokémon / Trainers / Energy
- Role breakdown: search, draw, gust, switch, energy acceleration, recovery, attacker, evolution support, etc.
- Card-by-card efficiency estimates
- Simple consistency notes and suggested improvements

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: <http://127.0.0.1:5000>

## Test

```bash
python -m pytest -q
```

## PythonAnywhere notes

This app should deploy cleanly on a free-tier PythonAnywhere account:

1. Clone the repo.
2. Create a virtualenv.
3. Install `requirements.txt`.
4. Point the WSGI file at `app:app`.
5. Avoid downloading card images or large API caches unless a later version explicitly adds storage controls.

## Roadmap

- Better card database/tagging
- Format legality support
- Probability math for opening hands and turn-by-turn consistency
- LimitlessTCG deck import/export helpers
- Archetype detection
- Suggested cuts/additions
