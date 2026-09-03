from http import HTTPStatus
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from tests import sample


async def get_user_by_id_empty_stub(db: AsyncSession,
                                    user_id: int):
    return []


async def get_user_by_id_stub(db: AsyncSession,
                              user_id: int):
    return sample.EXAMPLE_USER


async def get_all_users_stub(db: AsyncSession):
    return [sample.EXAMPLE_USER, sample.EXAMPLE_USER]


async def create_new_user_stub(db: AsyncSession,
                               user):
    return sample.EXAMPLE_NEW_USER_ADD


async def delete_user_stub(db: AsyncSession,
                           user_id: int):
    return Response(status_code=HTTPStatus.NO_CONTENT.value)


async def get_spot_by_id_stub(db: AsyncSession,
                              spot_id: int):
    return sample.EXAMPLE_SPOT


async def get_spots_stub(db: AsyncSession,
                         filter):
    return [sample.EXAMPLE_SPOT, sample.EXAMPLE_SPOT]


async def get_spot_by_id_empty_stub(db: AsyncSession,
                                    spot_id: int):
    return []


async def create_new_spot_stub(db: AsyncSession,
                               spot):
    return sample.EXAMPLE_SPOT


async def delete_spot_stub(db: AsyncSession,
                           spot_id: int,
                           owner_id: int = None):
    return Response(status_code=HTTPStatus.NO_CONTENT.value)


async def get_comment_by_id_stub(db: AsyncSession,
                                 comment_id: int):
    return sample.EXAMPLE_COMMENT


async def get_comment_by_id_empty_stub(db: AsyncSession,
                                       comment_id: int):
    return []


async def create_new_comment_stub(db: AsyncSession,
                                  comment):
    return sample.EXAMPLE_COMMENT
