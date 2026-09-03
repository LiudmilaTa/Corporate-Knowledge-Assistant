from app.database import get_connection

def save_document(filename, page, chunk_id, content, embedding):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (filename, page, chunk_id, content, embedding)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (filename, page, chunk_id, content, embedding),
    )

    conn.commit()
    cursor.close()
    conn.close()
