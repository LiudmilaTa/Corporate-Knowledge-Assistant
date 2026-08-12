from pgvector import Vector

from app.database import get_connection

def search_documents(query_embedding, limit=5):
    conn = get_connection()
    cur = conn.cursor()
    query_embedding = Vector(query_embedding)

    cur.execute(
        """
        SELECT
            filename,
            page,
            chunk_id,
            content,
            embedding <=> %s AS distance
        FROM documents
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (query_embedding, query_embedding, limit),
    )

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results
