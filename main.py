from __future__ import annotations   # ← ahora en la primera línea
"""
Constantes y utilidades comunes.
"""
import os, re, json
from datetime import date, timedelta
from typing import Any, Dict
import requests

from openai import OpenAI
from tools import TOOLS, FUNC_MAP

client = OpenAI(api_key="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")  # ← pon tu clave

def chat_loop() -> None:
    conversation: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Eres el asistente del Taller de Motos: identifica al cliente por teléfono, "
                "muestra la fecha de hoy cuando la pidan, consulta disponibilidad y reserva."
            ),
        }
    ]

    print("Agente activo. Escribe 'salir' para terminar.")
    while True:
        user = input("Usuario: ").strip()
        if user.lower() in {"salir", "exit"}:
            break
        conversation.append({"role": "user", "content": user})

        while True:
            rsp = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=conversation,
                tools=TOOLS,
                tool_choice="auto",
            )
            msg = rsp.choices[0].message
            print("[DEBUG] AI message:", msg)

            # registra la respuesta del modelo
            assistant_rec: Dict[str, Any] = {"role": "assistant"}
            if msg.content is not None:
                assistant_rec["content"] = msg.content
            if msg.tool_calls:
                assistant_rec["tool_calls"] = [
                    {
                        "id": c.id,
                        "type": c.type,
                        "function": {
                            "name": c.function.name,
                            "arguments": c.function.arguments,
                        },
                    }
                    for c in msg.tool_calls
                ]
            conversation.append(assistant_rec)

            # ejecuta tools si las hay
            if msg.tool_calls:
                for call in msg.tool_calls:
                    name = call.function.name
                    args = json.loads(call.function.arguments or "{}")
                    print(f"[DEBUG] ejecutando {name} {args}")
                    try:
                        result = FUNC_MAP[name](**args)
                    except Exception as e:
                        result = {"error": str(e)}
                    conversation.append(
                        {"role": "tool", "tool_call_id": call.id,
                         "content": json.dumps(result, ensure_ascii=False)}
                    )
                continue  # vuelve al modelo con los resultados

            # respuesta final al usuario
            print("Agente:", msg.content or "", "\n")
            break

if __name__ == "__main__":
    chat_loop()
