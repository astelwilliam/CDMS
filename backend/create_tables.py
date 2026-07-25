from app.db.session import Base, engine
import app.models

print("Registered tables:")
for table in Base.metadata.sorted_tables:
    print(" -", table.name)

print("\nCreating database tables...")
Base.metadata.create_all(bind=engine)
print("Done!")