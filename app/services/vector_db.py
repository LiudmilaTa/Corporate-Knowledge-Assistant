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


def replace_document(filename, chunks):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM documents WHERE filename = %s", (filename,))
        cursor.executemany(
            """
            INSERT INTO documents (filename, page, chunk_id, content, embedding)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (
                    filename,
                    chunk["page"],
                    chunk_id,
                    chunk["content"],
                    chunk["embedding"],
                )
                for chunk_id, chunk in enumerate(chunks)
            ],
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
