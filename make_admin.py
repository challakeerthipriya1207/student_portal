import sys

from database import SessionLocal
from models import User


def main():
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        return

    email = sys.argv[1].strip().lower()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"No user found with email {email}")
            return
        user.role = "admin"
        db.commit()
        print(f"{email} is now an admin.")
    finally:
        db.close()


if __name__ == "__main__":
    main()