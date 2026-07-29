import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth import hash_password

logger = logging.getLogger("task_manager.seed")

ADMIN_EMAIL = "thia80.ferreira@gmail.com"
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "191006"


async def seed_admin(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
    existing = result.scalar_one_or_none()

    if existing:
        existing.is_admin = True
        await db.commit()
        logger.info("Admin ja existe — atualizado.")
    else:
        admin = User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(admin)
        await db.commit()
        logger.info("Admin criado com sucesso.")
