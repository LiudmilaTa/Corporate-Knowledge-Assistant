from app.database import get_connection


def test_database_connection_can_be_established():
    conn = get_connection()

    assert conn is not None
    conn.close()
