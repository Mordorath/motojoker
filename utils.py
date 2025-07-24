from __future__ import annotations   # ⇒ debe ir siempre en la 1.ª línea

"""
Constantes y utilidades compartidas por todo el agente.
"""

import os, re
from datetime import date, timedelta
from typing import Any, Dict

import requests

# ───────────────────────────────── CONFIG ─────────────────────────────────────
BASE_URL: str = os.getenv("TALLER_API_URL", "https://botgestor.replit.app/api")
HEADERS: Dict[str, str] = {"Accept": "application/json"}

# Jornada laboral fija del taller (09:00‑16:00, inclusive)
JORNADA: list[str] = [f"{h:02}:00" for h in range(9, 17)]

# ──────────────────────────────── HELPERS ─────────────────────────────────────
def get_today() -> str:
    """Devuelve la fecha actual en formato ISO (YYYY‑MM‑DD)."""
    return date.today().isoformat()


def normalize_date(s: str) -> str:
    """
    Acepta:
      • 'hoy'/'today' ➜ fecha de hoy
      • 'mañana'/'tomorrow' ➜ hoy +1
      • Cadena ISO 'YYYY‑MM‑DD'
    Devuelve siempre 'YYYY‑MM‑DD'. Lanza ValueError si el formato no es válido.
    """
    s = s.lower().strip()
    today = date.today()

    if s in {"hoy", "today"}:
        return today.isoformat()
    if s in {"mañana", "tomorrow"}:
        return (today + timedelta(days=1)).isoformat()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s

    raise ValueError("Fecha inválida (usa YYYY‑MM‑DD o hoy/mañana).")


def safe_json(resp: requests.Response, ctx: str) -> Dict[str, Any]:
    """Convierte la respuesta a JSON o lanza un error con contexto claro."""
    if "application/json" not in resp.headers.get("content-type", "").lower():
        raise RuntimeError(
            f"{ctx}: esperaba JSON, status={resp.status_code}, "
            f"content‑type={resp.headers.get('content-type')}"
        )
    return resp.json()
