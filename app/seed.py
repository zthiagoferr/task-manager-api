import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.services.auth import hash_password

logger = logging.getLogger("task_manager.seed")


async def seed_admin(db: AsyncSession) -> None:
    admin_email = settings.ADMIN_EMAIL
    if not admin_email:
        logger.info("ADMIN_EMAIL nao configurado — seed pulado.")
        return

    result = await db.execute(select(User).where(User.email == admin_email))
    existing = result.scalar_one_or_none()

    if existing:
        if not existing.is_admin:
            existing.is_admin = True
            await db.commit()
            logger.info("Admin ja existe — promovido a admin.")
        else:
            logger.info("Admin ja existe.")
    else:
        admin = User(
            email=admin_email,
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(admin)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            logger.info("Admin ja foi criado por outro worker — ignorando.")
        else:
            logger.info("Admin criado com sucesso.")
