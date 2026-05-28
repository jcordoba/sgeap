"""
Script para extraer texto de PDFs de UNAC y subir al RAG.
Requiere:
    - sentence-transformers
    - pdfplumber
    - Base de datos RAG en puerto 5434
"""
import os
import sys
from pathlib import Path
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.services.embedding import generate_embedding, vector_to_sql

DOCS_DIR = Path("E:/Projects/appsgeap/Docs/UNAC")
RAG_DB_URL = "postgresql+pg8000://rag_user:rag_pass_2026@localhost:5434/sgeap_rag"

# Mapeo de archivos a metadata
DOCUMENTOS = {
    "Estatutos_Generales.pdf": {"titulo": "Estatutos Generales UNAC", "tipo": "Estatuto", "categoria": "Institucional"},
    "Estructura_Organica.pdf": {"titulo": "Estructura Organica UNAC", "tipo": "Organigrama", "categoria": "Institucional"},
    "Modelo_Educativo.pdf": {"titulo": "Modelo Educativo para la UNAC", "tipo": "Modelo", "categoria": "Curricular"},
    "Proyecto_Educativo_Institucional.pdf": {"titulo": "Proyecto Educativo Institucional", "tipo": "Proyecto", "categoria": "Institucional"},
    "Politicas_Calidad.pdf": {"titulo": "Politicas de Calidad Institucional", "tipo": "Politica", "categoria": "Calidad"},
    "Plan_Desarrollo_Institucional.pdf": {"titulo": "Plan de Desarrollo Institucional 2026-2030", "tipo": "Plan", "categoria": "Institucional"},
    "Codigo_Etica.pdf": {"titulo": "Codigo de Etica y Buen Gobierno", "tipo": "Codigo", "categoria": "Institucional"},
    "Politicas_Diseno_Curricular.pdf": {"titulo": "Politicas sobre Diseno Curricular", "tipo": "Politica", "categoria": "Curricular"},
    "Modelo_Resultados_Aprendizaje.pdf": {"titulo": "Modelo de Resultados de Aprendizaje", "tipo": "Modelo", "categoria": "Curricular"},
    "Comite_Curricular_Funciones.pdf": {"titulo": "Comite Curricular del Programa - Funciones", "tipo": "Funcion", "categoria": "Curricular"},
    "Reglamento_Practica_Pedagogica.pdf": {"titulo": "Reglamento de Practica Pedagogica", "tipo": "Reglamento", "categoria": "Curricular"},
    "Reglamento_Estudiantil.pdf": {"titulo": "Reglamento Estudiantil UNAC", "tipo": "Reglamento", "categoria": "Academico"},
    "Estatuto_Profesoral.pdf": {"titulo": "Estatuto Profesoral", "tipo": "Estatuto", "categoria": "Academico"},
    "Politicas_Inclusion.pdf": {"titulo": "Politicas de Inclusion", "tipo": "Politica", "categoria": "Calidad"},
    "Politicas_Internacionalizacion.pdf": {"titulo": "Politicas de Internacionalizacion", "tipo": "Politica", "categoria": "Calidad"},
    "Sistema_Investigacion.pdf": {"titulo": "Sistema de Investigacion - Guia y Reglamentos", "tipo": "Sistema", "categoria": "Investigacion"},
    "Modelo_Bienestar_Universitario.pdf": {"titulo": "Modelo de Bienestar Universitario", "tipo": "Modelo", "categoria": "Bienestar"},
    "Manual_Convivencia.pdf": {"titulo": "Manual de Convivencia", "tipo": "Manual", "categoria": "Bienestar"},
}


def extract_text_from_pdf(filepath: Path) -> str:
    """Extrae texto de un PDF."""
    import pdfplumber

    text_parts = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"  Error extrayendo {filepath.name}: {e}")
        return ""


def subir_al_rag(doc_id: str, titulo: str, tipo: str, categoria: str, contenido: str, fuente: str):
    """Sube un documento al RAG con embeddings."""
    rag_engine = create_engine(RAG_DB_URL)

    # Generar embedding
    embedding = generate_embedding(contenido[:8000])
    vector_str = vector_to_sql(embedding)

    # Contenido resumido (primeros 500 chars)
    resumen = contenido[:500] + "..." if len(contenido) > 500 else contenido

    try:
        with rag_engine.connect() as conn:
            # Verificar si ya existe
            check = conn.execute(
                text("SELECT id FROM documentos_rag_embeddings WHERE id = :id"),
                {"id": doc_id}
            )
            if check.fetchone():
                print(f"  [ya existe] {titulo}")
                return False

            # Insertar
            conn.execute(text("""
                INSERT INTO documentos_rag_embeddings
                (id, titulo, tipo_documento, categoria, fuente, contenido, contenido_resumido, embedding)
                VALUES (:id, :titulo, :tipo, :categoria, :fuente, :contenido, :resumen, CAST(:embedding AS vector))
            """), {
                "id": doc_id,
                "titulo": titulo,
                "tipo": tipo,
                "categoria": categoria,
                "fuente": fuente,
                "contenido": contenido,
                "resumen": resumen,
                "embedding": vector_str,
            })
            conn.commit()
            return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    print("=" * 60)
    print("SUBIENDO DOCUMENTOS UNAC AL RAG")
    print("=" * 60)

    uploaded = 0
    skipped = 0
    errors = 0

    for filename, metadata in DOCUMENTOS.items():
        filepath = DOCS_DIR / filename

        if not filepath.exists():
            print(f"\n{filename}: [NO ENCONTRADO]")
            errors += 1
            continue

        print(f"\n{metadata['titulo']}:")
        print(f"  Archivo: {filepath.name} ({filepath.stat().st_size // 1024} KB)")

        # Extraer texto
        print("  Extrayendo texto...")
        contenido = extract_text_from_pdf(filepath)

        if not contenido or len(contenido) < 100:
            print(f"  [ERROR] No se pudo extraer texto suficiente")
            errors += 1
            continue

        print(f"  Texto extraido: {len(contenido)} caracteres")

        # Generar ID
        doc_id = str(uuid4())

        # Subir al RAG
        print("  Subiendo al RAG...")
        ok = subir_al_rag(
            doc_id=doc_id,
            titulo=metadata["titulo"],
            tipo=metadata["tipo"],
            categoria=metadata["categoria"],
            contenido=contenido,
            fuente=filename
        )

        if ok:
            print("  [OK] Subido con embedding")
            uploaded += 1
        elif ok is None:  # None means skipped
            skipped += 1
        else:
            errors += 1

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Subidos: {uploaded}")
    print(f"Omitidos: {skipped}")
    print(f"Errores: {errors}")
    print(f"Total documentos RAG: {uploaded + skipped}")


if __name__ == "__main__":
    main()