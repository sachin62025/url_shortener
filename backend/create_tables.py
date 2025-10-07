from database import engine, Base
import models  # ensure models are imported so Base knows about them

def init_db():
    Base.metadata.create_all(bind=engine)
    print("DB tables created.")

if __name__ == "__main__":
    init_db()
