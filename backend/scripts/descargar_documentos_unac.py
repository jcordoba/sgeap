"""
Script para descargar documentos de UNAC desde Google Drive y subirlos al RAG.
Requiere:
1. PostgreSQL RAG en puerto 5434 (ya configurado en docker-compose.rag.yml)
2. gdown: pip install gdown
3. docx: pip install python-docx
4. sentence-transformers ya instalados en venv

Uso:
    python scripts/descargar_documentos_unac.py
"""
import os
import re
import requests
from pathlib import Path

# Configuration
DOCS_DIR = Path("E:/Projects/appsgeap/Docs/UNAC")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Documentos relevantes para el SGEAP (ID de Google Drive)
DOCUMENTOS_UNAC = {
    # Institucional
    "Estatutos_Generales": {
        "url": "https://drive.google.com/uc?export=download&id=1JGb5ZDmhm9c3aeNEASz02HmEehYuwoT4",
        "tipo": "Estatuto",
        "categoria": "Institucional",
    },
    "Estructura_Organica": {
        "url": "https://drive.google.com/uc?export=download&id=1RHjCMbepGA7kc7xEGhL9MXtYOu-yU9xW",
        "tipo": "Organigrama",
        "categoria": "Institucional",
    },
    "Modelo_Educativo": {
        "url": "https://drive.google.com/uc?export=download&id=1c36rWfDPe2WNdYrzkFyE6E-fehhg_1EW",
        "tipo": "Modelo",
        "categoria": "Curricular",
    },
    "Proyecto_Educativo_Institucional": {
        "url": "https://drive.google.com/uc?export=download&id=1b3Psg7y5dFO0ZwQFR2b-h1Gxr-_Zibj2",
        "tipo": "Proyecto",
        "categoria": "Institucional",
    },
    "Politicas_Calidad": {
        "url": "https://drive.google.com/uc?export=download&id=1vhnKyxq2z6ixZG6fVBhbYso0EYtQo2BE",
        "tipo": "Politica",
        "categoria": "Calidad",
    },
    "Plan_Desarrollo_Institucional": {
        "url": "https://drive.google.com/uc?export=download&id=1GX9F0-I53V0mqCR4VlK2l69LO6Etmdtw",
        "tipo": "Plan",
        "categoria": "Institucional",
    },
    "Codigo_Etica": {
        "url": "https://drive.google.com/uc?export=download&id=1qqvFyPhDP8zIzQepeLdRSLcuJHSnOfju",
        "tipo": "Codigo",
        "categoria": "Institucional",
    },

    # Curriculares
    "Politicas_Diseno_Curricular": {
        "url": "https://drive.google.com/uc?export=download&id=1vKszXRtm-YO_aOWXrnjHr-08qmzXJDRs",
        "tipo": "Politica",
        "categoria": "Curricular",
    },
    "Modelo_Resultados_Aprendizaje": {
        "url": "https://drive.google.com/uc?export=download&id=1bhNa9vs2IIoALEfG__fOKGb-1yHm8g_P",
        "tipo": "Modelo",
        "categoria": "Curricular",
    },
    "Comite_Curricular_Funciones": {
        "url": "https://drive.google.com/uc?export=download&id=14LUu-etE9AAfQ4gqnQ3I-AaK8Fgj5CQs",
        "tipo": "Funcion",
        "categoria": "Curricular",
    },
    "Reglamento_Practica_Pedagogica": {
        "url": "https://drive.google.com/uc?export=download&id=1g1pgwomzjh74scOnzdLMs-aOmQBnOZ5b",
        "tipo": "Reglamento",
        "categoria": "Curricular",
    },

    # Académicos
    "Reglamento_Estudiantil": {
        "url": "https://drive.google.com/uc?export=download&id=1M-gsawEeyFIjO6cFI2-tdUlCpEjIi9KA",
        "tipo": "Reglamento",
        "categoria": "Academico",
    },
    "Estatuto_Profesoral": {
        "url": "https://drive.google.com/uc?export=download&id=1Ds5_Sqbm_1Vw5yF4vYCJPT5ijEE_DsQi",
        "tipo": "Estatuto",
        "categoria": "Academico",
    },

    # Calidad
    "Politicas_Inclusion": {
        "url": "https://drive.google.com/uc?export=download&id=12wlBYB3z3XuRf4gAYZ7dDDb8GIz1JiRa",
        "tipo": "Politica",
        "categoria": "Calidad",
    },
    "Politicas_Internacionalizacion": {
        "url": "https://drive.google.com/uc?export=download&id=18XopyflNAYMZuFDVB4bkpdJkyIFi84it",
        "tipo": "Politica",
        "categoria": "Calidad",
    },
    "Sistema_Investigacion": {
        "url": "https://drive.google.com/uc?export=download&id=1vCxR7-AScItKRzr7yi6f-vWGj0GsJSsQ",
        "tipo": "Sistema",
        "categoria": "Investigacion",
    },

    # Bienestar
    "Modelo_Bienestar_Universitario": {
        "url": "https://drive.google.com/uc?export=download&id=1awQIc_ejgAbeX9mmylCUXPPtFgCwv2wz",
        "tipo": "Modelo",
        "categoria": "Bienestar",
    },
    "Manual_Convivencia": {
        "url": "https://drive.google.com/uc?export=download&id=1M-gsawEeyFIjO6cFI2-tdUlCpEjIi9KA",
        "tipo": "Manual",
        "categoria": "Bienestar",
    },
}


def descargar_documento(nombre: str, info: dict) -> tuple[bool, str]:
    """Descarga un documento de Google Drive."""
    filepath = DOCS_DIR / f"{nombre}.pdf"

    if filepath.exists():
        print(f"  [ya existe] {filepath.name}")
        return True, str(filepath)

    print(f"  Descargando: {nombre}...")

    try:
        # Intentar con gdown
        import gdown

        output = str(filepath)
        gdown.download(info["url"], output, quiet=True)
        return True, output

    except Exception as e:
        print(f"  [WARNING] Error con gdown: {e}")
        # Fallback con requests
        try:
            session = requests.Session()
            response = session.get(info["url"], stream=True, timeout=60)

            # Google Drive confirmation
            if "confirm=" in response.url or response.status_code == 302:
                token = re.search(r'download_id=([^&]+)', response.text)
                if token:
                    confirm_url = f"{info['url']}&confirm={token.group(1)}"
                    response = session.get(confirm_url, stream=True, timeout=60)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True, str(filepath)
        except Exception as e2:
            print(f"  [ERROR fallback] {e2}")
            return False, ""


def main():
    """Descarga todos los documentos y genera reporte."""
    print("=" * 60)
    print("DESCARGANDO DOCUMENTOS UNAC")
    print("=" * 60)

    descargados = []
    errores = []

    for nombre, info in DOCUMENTOS_UNAC.items():
        print(f"\n{nombre}:")
        ok, filepath = descargar_documento(nombre, info)
        if ok:
            size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            print(f"  [OK] ({size // 1024} KB)")
            descargados.append((nombre, info, filepath))
        else:
            errores.append((nombre, info))

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Descargados: {len(descargados)}/{len(DOCUMENTOS_UNAC)}")
    print(f"Errores: {len(errores)}")

    if errores:
        print("\nDocumentos no descargados:")
        for nombre, info in errores:
            print(f"  - {nombre}")

    # Generar lista para subir al RAG
    print("\n" + "=" * 60)
    print("LISTA PARA SUBIR AL RAG")
    print("=" * 60)

    for nombre, info, filepath in descargados:
        print(f"  {nombre} -> {filepath} | Tipo: {info['tipo']} | Cat: {info['categoria']}")

    return descargados, errores


if __name__ == "__main__":
    main()