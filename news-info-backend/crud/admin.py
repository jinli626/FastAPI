import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.admin import Admin, AdminToken
from utils import security


async def get_admin_by_username(db: AsyncSession, username: str):
    query = select(Admin).where(Admin.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate_admin(db: AsyncSession, username: str, password: str):
    admin = await get_admin_by_username(db, username)
    if not admin:
        return None
    if not security.verify_password(password, admin.password):
        return None
    return admin


async def create_admin_token(db: AsyncSession, admin_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    query = select(AdminToken).where(AdminToken.admin_id == admin_id)
    result = await db.execute(query)
    admin_token = result.scalar_one_or_none()

    if admin_token:
        admin_token.token = token
        admin_token.expires_at = expires_at
    else:
        admin_token = AdminToken(
            admin_id=admin_id,
            token=token,
            expires_at=expires_at
        )
        db.add(admin_token)

    await db.commit()
    return token


async def get_admin_by_token(db: AsyncSession, token: str):
    query = select(AdminToken).where(AdminToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query = select(Admin).where(Admin.id == db_token.admin_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def change_admin_password(db: AsyncSession, admin: Admin, old_password: str, new_password: str):
    if not security.verify_password(old_password, admin.password):
        return False
    admin.password = security.get_hash_password(new_password)
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return True
