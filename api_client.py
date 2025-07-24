from __future__ import annotations    # ⇒ primera línea

"""
Wrappers HTTP para todas las rutas REST del backend y
fallback de disponibilidad cuando el endpoint /bot/disponibilidad falla.
"""

from typing import Any, Dict, List, Optional
import requests

from utils import (
    BASE_URL,
    HEADERS,
    JORNADA,
    normalize_date,
    safe_json,
    get_today,
)

# ──────────────────────────────── HELPERS HTTP ────────────────────────────────
def _get(path: str, params: Dict[str, Any] | None = None, *, ctx: str) -> Dict[str, Any]:
    url = BASE_URL + path
    print("[DEBUG] GET", url, params)
    return safe_json(requests.get(url, params=params, headers=HEADERS), ctx)


def _post(path: str, data: Dict[str, Any], *, ctx: str) -> Dict[str, Any]:
    url = BASE_URL + path
    print("[DEBUG] POST", url, data)
    return safe_json(requests.post(url, json=data, headers=HEADERS), ctx)


# ──────────────────────────────── CLIENTES API ────────────────────────────────
def clientes_search(q: str) -> List[Dict[str, Any]]:
    """Busca clientes por nombre o teléfono (solo activos)."""
    return _get("/clientes/search", {"q": q}, ctx="clientes_search")


def clientes_create(**data) -> Dict[str, Any]:
    """Crea un cliente rápido (al menos nombre y teléfono)."""
    return _post("/clientes", data, ctx="clientes_create")


# ──────────────────────────────── TURNOS / PUESTOS ────────────────────────────
def puestos_activos() -> List[Dict[str, Any]]:
    return _get("/puestos/activos", ctx="puestos_activos")


def turnos_by_puesto(puesto_id: int, fecha: str) -> List[Dict[str, Any]]:
    return _get(
        f"/turnos/puesto/{puesto_id}",
        {"fecha": normalize_date(fecha)},
        ctx="turnos_by_puesto",
    )


# ─────────────────────────── BOT: DISPONIBILIDAD & RESERVA ────────────────────
def bot_disponibilidad(fecha: str, puestoId: Optional[int] = None) -> Dict[str, Any]:
    """Intenta /bot/disponibilidad y, si falla, calcula disponibilidad manualmente."""
    fecha_norm = normalize_date(fecha)

    # 1) Llamada al endpoint oficial
    try:
        data = _get(f"/bot/disponibilidad/{fecha_norm}", ctx="bot_disponibilidad")
        if data.get("error"):
            raise RuntimeError(data["error"])
        if puestoId is not None:
            data["puestos"] = [
                p for p in data.get("puestos", []) if p["puestoId"] == puestoId
            ]
        return data
    except Exception as exc:
        print(f"[DEBUG] bot_disponibilidad fallback -> {exc}")

    # 2) Fallback manual (sin cache)
    puestos = puestos_activos()
    if puestoId is not None:
        puestos = [p for p in puestos if p["id"] == puestoId]

    resultado = {"fecha": fecha_norm, "from_fallback": True, "puestos": []}

    for p in puestos:
        reservas = turnos_by_puesto(p["id"], fecha_norm)
        ocupadas = {t["horaInicio"][:5] for t in reservas}  # formatear HH:MM
        libres = [h for h in JORNADA if h not in ocupadas]

        resultado["puestos"].append(
            {
                "puestoId": p["id"],
                "nombre": p.get("nombre", f"Puesto {p['id']}"),
                "horariosDisponibles": libres,
            }
        )

    return resultado


def bot_reservar(**data) -> Dict[str, Any]:
    """
    Crea una reserva rápida vía Bot API.
    Requiere que la hora esté libre (comprobar antes).
    """
    data["fecha"] = normalize_date(data["fecha"])
    return _post("/bot/reservar", data, ctx="bot_reservar")
