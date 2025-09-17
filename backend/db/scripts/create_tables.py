from backend.db.session import engine, Base
from backend.db import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created/checked.")
