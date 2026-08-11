from app.models.document import Document

print(Document.__tablename__)
print(Document.__table__.columns.keys())