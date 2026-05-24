"""MiniMax AI service (Anthropic-compatible) for content generation."""
import json
from typing import Optional

import httpx

from app.config import get_settings


settings = get_settings()


async def generar_contenido_fase(
    fase_nombre: str,
    programa_nombre: str = "",
    contexto_adicional: str = ""
) -> dict[str, str]:
    """Generate phase content using MiniMax AI (Anthropic-compatible API)."""

    prompt = f"""Eres un asistente especializado en creación de documentación académica para programas universitarios en Colombia.
Necesito que generes contenido para la fase llamada: "{fase_nombre}".
{f"Programa académico: {programa_nombre}" if programa_nombre else ""}
{f"Contexto adicional: {contexto_adicional}" if contexto_adicional else ""}

Por favor genera contenido estructurado con los siguientes campos:
1. introduccion: Introducción general de esta fase (100-150 palabras)
2. objetivos: Objetivos específicos de esta fase (lista de 3-5 objetivos)
3. requisitos: Requisitos o elementos necesarios para completar esta fase
4. recomendaciones: Recomendaciones basadas en mejores prácticas institucionales

Responde SOLO en formato JSON con estas claves, sin texto adicional."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.minimax_base_url}/messages",
                headers={
                    "x-api-key": settings.minimax_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                },
            )

            if response.status_code == 200:
                data = response.json()
                # Extract text content (skip thinking blocks)
                contenido = ""
                for item in data.get("content", []):
                    if item.get("type") == "text":
                        contenido = item.get("text", "")
                        break

                # Parse JSON response
                if contenido:
                    try:
                        contenido_json = json.loads(contenido)
                        return contenido_json
                    except json.JSONDecodeError:
                        return parse_content_from_text(contenido)

            else:
                print(f"MiniMax API error: {response.status_code} - {response.text}")
                return generar_contenido_fallback(fase_nombre, programa_nombre)

    except Exception as e:
        print(f"MiniMax error: {e}")
        return generar_contenido_fallback(fase_nombre, programa_nombre)


def parse_content_from_text(text: str) -> dict[str, str]:
    """Parse content from non-JSON text response."""
    # Clean markdown formatting
    text = text.replace("#", "").replace("*", "").replace("**", "").strip()

    result = {
        "introduccion": "",
        "objetivos": "",
        "requisitos": "",
        "recomendaciones": ""
    }

    lines = text.split("\n")
    current_section = None

    for line in lines:
        line_lower = line.lower().strip()
        if "introduccion" in line_lower:
            current_section = "introduccion"
        elif "objetivo" in line_lower:
            current_section = "objetivos"
        elif "requisito" in line_lower:
            current_section = "requisitos"
        elif "recomendacion" in line_lower:
            current_section = "recomendaciones"

        if current_section and line.strip() and not any(k in line_lower for k in ["introduccion", "objetivo", "requisito", "recomendacion"]):
            if result[current_section]:
                result[current_section] += "\n" + line.strip()
            else:
                result[current_section] = line.strip()

    for key in result:
        result[key] = result[key].strip()

    return result if any(result.values()) else generar_contenido_fallback("", "")


def generar_contenido_fallback(fase_nombre: str, programa: str) -> dict[str, str]:
    """Fallback content when AI fails."""
    return {
        "introduccion": f"Esta fase corresponde a {fase_nombre}. El contenido debe desarrollarse según los lineamientos institucionales y los requisitos de acreditación.",
        "objetivos": "1. Analizar los aspectos requeridos para esta fase\n2. Documentar los elementos sesuai con los estándares de calidad\n3. Preparar las evidencias necesarias",
        "requisitos": "- Documentación de soporte\n- Cumplimiento de criterios de calidad\n- Validación institucional",
        "recomendaciones": "Consulte los documentos institucionales y formatos de calidad para completar esta fase correctamente."
    }


async def resumir_documento(texto: str, max_palabras: int = 200) -> str:
    """Summarize a document using MiniMax AI."""

    prompt = f"""Resume el siguiente texto en máximo {max_palabras} palabras.
Mantén la información más importante y relevante.

Texto:
{texto[:4000]}"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.minimax_base_url}/messages",
                headers={
                    "x-api-key": settings.minimax_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                },
            )

            if response.status_code == 200:
                data = response.json()
                # Extract text content (skip thinking blocks)
                contenido = ""
                for item in data.get("content", []):
                    if item.get("type") == "text":
                        contenido = item.get("text", "")
                        break

                return contenido if contenido else texto[:max_palabras*5] + "..."
    except Exception as e:
        print(f"MiniMax summarization error: {e}")

    # Clean markdown from input text
    clean_text = texto.replace("#", "").replace("*", "").replace("**", "").strip()
    words = clean_text.split()
    if len(words) > max_palabras:
        return " ".join(words[:max_palabras]) + "..."
    return clean_text


async def mejorar_contenido(contenido: str, contexto: str = "") -> str:
    """Improve/enhance existing content using AI."""

    prompt = f"""{contexto}

Mejora el contenido anterior, haciéndolo más completo, profesional y adecuado para documentación académica institucional.
Mantén el mismo formato y estructura pero con mayor profundidad y calidad.

Contenido actual:
{contenido[:3000]}

Responde únicamente con el contenido mejorado, sin explicaciones adicionales."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.minimax_base_url}/messages",
                headers={
                    "x-api-key": settings.minimax_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                },
            )

            if response.status_code == 200:
                data = response.json()
                # Extract text content (skip thinking blocks)
                contenido = ""
                for item in data.get("content", []):
                    if item.get("type") == "text":
                        contenido = item.get("text", "")
                        break

                # Clean markdown formatting
                if contenido:
                    contenido = contenido.replace("#", "").replace("*", "").replace("**", "").strip()

                return contenido if contenido else contenido

    except Exception as e:
        print(f"MiniMax improvement error: {e}")

    return contenido