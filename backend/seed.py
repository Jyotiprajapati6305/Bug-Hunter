"""Seed script: creates roles, demo users, challenge categories and sample challenges.

Run with:  python seed.py
(or inside the backend container: docker compose exec backend python seed.py)

Idempotent: safe to run multiple times — existing rows are left alone.
"""
import logging

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.challenge import Challenge, ChallengeCategory
from app.models.user import Role, User, UserProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

DEMO_USERS = [
    {"email": "admin@bughunter.dev", "username": "admin", "password": "Admin123!", "role": "admin"},
    {"email": "dev@bughunter.dev", "username": "dev", "password": "Dev123!", "role": "developer"},
    {"email": "tester@bughunter.dev", "username": "tester", "password": "Tester123!", "role": "tester"},
]

ROLES = ["admin", "developer", "tester"]

CATEGORIES = [
    {"name": "Web UI Testing", "slug": "web-ui", "description": "Find bugs in web user interfaces."},
    {"name": "API Testing", "slug": "api-testing", "description": "Find bugs in REST/GraphQL APIs."},
    {"name": "Security Testing", "slug": "security", "description": "Find security vulnerabilities."},
]

CHALLENGES = [
    {
        "title": "Broken Checkout Flow",
        "description": (
            "An e-commerce checkout page has a multi-step form (cart -> shipping -> payment -> "
            "confirmation). Explore the flow and find functional bugs, e.g. validation gaps, "
            "state not persisting between steps, or incorrect totals."
        ),
        "difficulty": "beginner",
        "type": "functional",
        "base_xp": 50,
        "category_slug": "web-ui",
    },
    {
        "title": "User API Authorization Bypass",
        "description": (
            "A REST API exposes /api/users/{id} endpoints. Test authorization boundaries between "
            "user roles and look for IDOR (insecure direct object reference) or missing auth checks."
        ),
        "difficulty": "intermediate",
        "type": "api",
        "base_xp": 80,
        "category_slug": "api-testing",
    },
    {
        "title": "Login Form Injection Risks",
        "description": (
            "A login form may be vulnerable to SQL injection or XSS. Probe the input fields and "
            "report any injection vulnerabilities you can demonstrate."
        ),
        "difficulty": "advanced",
        "type": "security",
        "base_xp": 100,
        "category_slug": "security",
    },
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        role_map: dict[str, Role] = {}
        for role_name in ROLES:
            role = db.query(Role).filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name, description=f"{role_name.title()} role")
                db.add(role)
                db.commit()
                logger.info("Created role: %s", role_name)
            role_map[role_name] = role

        for spec in DEMO_USERS:
            existing = db.query(User).filter_by(email=spec["email"]).first()
            if existing:
                logger.info("User already exists: %s", spec["email"])
                continue
            user = User(
                email=spec["email"],
                username=spec["username"],
                hashed_password=hash_password(spec["password"]),
                role_id=role_map[spec["role"]].id,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.flush()
            profile = UserProfile(user_id=user.id, display_name=spec["username"])
            db.add(profile)
            db.commit()
            logger.info("Created demo user: %s (%s)", spec["email"], spec["role"])

        category_map: dict[str, ChallengeCategory] = {}
        for cat in CATEGORIES:
            existing = db.query(ChallengeCategory).filter_by(slug=cat["slug"]).first()
            if existing is None:
                existing = ChallengeCategory(
                    name=cat["name"], slug=cat["slug"], description=cat["description"]
                )
                db.add(existing)
                db.commit()
                logger.info("Created category: %s", cat["name"])
            category_map[cat["slug"]] = existing

        for ch in CHALLENGES:
            existing = db.query(Challenge).filter_by(title=ch["title"]).first()
            if existing:
                logger.info("Challenge already exists: %s", ch["title"])
                continue
            challenge = Challenge(
                category_id=category_map[ch["category_slug"]].id,
                title=ch["title"],
                description=ch["description"],
                difficulty=ch["difficulty"],
                type=ch["type"],
                base_xp=ch["base_xp"],
                is_published=True,
            )
            db.add(challenge)
            db.commit()
            logger.info("Created challenge: %s", ch["title"])

        logger.info("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
