"""Script para migrar documentos existentes a pgvector y generar embeddings."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import DocumentoRAG
from app.services.embedding import generate_embedding, vector_to_sql
from sqlalchemy import create_engine, text

RAG_DB_URL = "postgresql://rag_user:rag_pass_2026@localhost:5434/sgeap_rag"
rag_engine = create_engine(RAG_DB_URL)


def migrate_documents():
    """Migrate existing documents to pgvector with embeddings."""
    db = next(get_db())

    # Get all documents without embeddings
    documentos = db.query(DocumentoRAG).filter(DocumentoRAG.vigente == True).all()

    print(f"Migrating {len(documentos)} documents...")

    with rag_engine.connect() as conn:
        for i, doc in enumerate(documentos):
            try:
                # Generate embedding
                print(f"  Processing {i+1}/{len(documentos)}: {doc.titulo[:50]}...")
                embedding = generate_embedding(doc.contenido[:8000])
                vector_str = vector_to_sql(embedding)

                # Check if document already exists in rag table
                existing = conn.execute(text(
                    "SELECT id FROM documentos_rag_embeddings WHERE id = :id"
                ), {"id": str(doc.id)}).fetchone()

                if existing:
                    print(f"    Already exists, skipping")
                    continue

                # Insert into pgvector database (using raw SQL with explicit casting)
                insert_sql = f"""
                    INSERT INTO documentos_rag_embeddings
                    (id, titulo, tipo_documento, categoria, fuente, contenido, contenido_resumido, embedding, vigente)
                    VALUES ('{str(doc.id)}', :titulo, :tipo, :categoria, :fuente, :contenido, :resumido, '{vector_str}'::vector, :vigente)
                """
                conn.execute(text(insert_sql), {
                    "titulo": doc.titulo,
                    "tipo": doc.tipo_documento,
                    "categoria": doc.categoria,
                    "fuente": doc.fuente,
                    "contenido": doc.contenido,
                    "resumido": doc.contenido_resumido or doc.contenido[:500],
                    "vigente": doc.vigente,
                })
                conn.commit()
                print(f"    OK")

            except Exception as e:
                print(f"    Error: {e}")

    print("\nMigration complete!")
    print(f"Documents in pgvector database:")

    with rag_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM documentos_rag_embeddings"))
        count = result.fetchone()[0]
        print(f"  Total: {count}")


if __name__ == "__main__":
    migrate_documents()