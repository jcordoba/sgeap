-- RAG table with pgvector embeddings

-- Crear tabla documentos_rag_embeddings
CREATE TABLE IF NOT EXISTS documentos_rag_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(500) NOT NULL,
    tipo_documento VARCHAR(100) NOT NULL,
    categoria VARCHAR(200) NOT NULL,
    fuente VARCHAR(200) NOT NULL,
    url_origen VARCHAR(1000),

    -- Contenido original
    contenido TEXT NOT NULL,
    contenido_resumido TEXT,

    -- Metadatos
    metadatos JSONB,
    etiquetas JSONB,
    vigente BOOLEAN DEFAULT TRUE,
    fecha_documento TIMESTAMP,

    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Vector de embeddings (384 dimensiones para all-MiniLM-L6-v2)
    embedding VECTOR(384)
);

-- Índices para búsqueda
CREATE INDEX IF NOT EXISTS idx_rag_embedding_cosine
    ON documentos_rag_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_rag_categoria
    ON documentos_rag_embeddings (categoria);

CREATE INDEX IF NOT EXISTS idx_rag_vigente
    ON documentos_rag_embeddings (vigente);

-- Verificar
SELECT 'Tabla documentos_rag_embeddings creada con vector support!' as status;