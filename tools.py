"""
Mapea las funciones HTTP => tools para function‑calling.
"""
from __future__ import annotations
from typing import Dict, Any, List
import api_client as api

FUNC_MAP = {
    "clientes_search":    api.clientes_search,
    "clientes_create":    api.clientes_create,
    "bot_disponibilidad": api.bot_disponibilidad,
    "bot_reservar":       api.bot_reservar,
    "get_today":          api.get_today,
}

def _schema(name: str, description: str, params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": params},
    }

TOOLS: List[Dict[str, Any]] = [
    _schema(
        "clientes_search",
        "Busca clientes por nombre o teléfono.",
        {"type":"object","properties":{"q":{"type":"string"}},"required":["q"]},
    ),
    _schema(
        "clientes_create",
        "Crea un cliente (nombre y teléfono obligatorios).",
        {
            "type":"object",
            "properties":{
                "nombre":{"type":"string"},
                "telefono":{"type":"string"},
                "email":{"type":"string"},
                "direccion":{"type":"string"},
                "tipoCliente":{"type":"string"},
            },
            "required":["nombre","telefono"],
        },
    ),
    _schema(
        "bot_disponibilidad",
        "Horarios libres para una fecha; opcional filtrar por puestoId.",
        {
            "type":"object",
            "properties":{
                "fecha":{"type":"string"},
                "puestoId":{"type":"integer"}
            },
            "required":["fecha"],
        },
    ),
    _schema(
        "bot_reservar",
        "Crea una reserva rápida (verifica antes la disponibilidad).",
        {
            "type":"object",
            "properties":{
                "clienteNombre":{"type":"string"},
                "clienteTelefono":{"type":"string"},
                "fecha":{"type":"string"},
                "horaInicio":{"type":"string"},
                "puestoId":{"type":"integer"},
                "motoMarca":{"type":"string"},
                "motoModelo":{"type":"string"},
                "descripcionTrabajo":{"type":"string"},
                "canal":{"type":"string","default":"whatsapp"},
            },
            "required":["clienteNombre","clienteTelefono","fecha","horaInicio","puestoId"],
        },
    ),
    _schema(
        "get_today",
        "Devuelve la fecha actual en ISO y en formato legible en español.",
        {"type":"object","properties":{}}
    ),
]
