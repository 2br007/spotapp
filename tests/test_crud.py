from types import SimpleNamespace

import pytest
from fastapi import Response
from sqlalchemy.exc import NoResultFound

from api.crud import CRUDComment, CRUDSpot, CRUDUser
from api import schema


class FakeResult:
    def __init__(self, value=None, rows=None, rowcount=None):
        self.value = value
        self.rows = rows or []
        self.rowcount = rowcount

    def scalar_one(self):
        if self.value is None:
            raise NoResultFound
        return self.value

    def scalar_one_or_none(self):
        return self.value

    def all(self):
        return self.rows

    def scalars(self):
        return self

    def __iter__(self):
        return iter(self.rows)


class FakeSession:
    def __init__(self, *results):
        self.results = list(results)
        self.added = []
        self.deleted = []

    async def execute(self, query):
        return self.results.pop(0)

    async def flush(self):
        return None

    def add(self, item):
        self.added.append(item)

    async def delete(self, item):
        self.deleted.append(item)


@pytest.mark.asyncio
async def test_user_crud_reads_and_adds():
    user = SimpleNamespace(nickname="nick", email="user@example.com")
    session = FakeSession(FakeResult(user), FakeResult(rows=[user]))

    assert await CRUDUser.get_user_by_email(session, user.email) is user
    assert await CRUDUser.get_all_users(session) == [user]

    added = await CRUDUser.add_user(session, user)
    assert added == schema.UserTerseSchema(nickname="nick", email="user@example.com")
    assert session.added == [user]


@pytest.mark.asyncio
async def test_user_crud_update_and_delete():
    user = SimpleNamespace(user_id=1)
    session = FakeSession(FakeResult(rowcount=1), FakeResult(user))

    assert await CRUDUser.update(session, 1, {"disabled": False}) == (
        "User with user_id=1 is updated!"
    )
    response = await CRUDUser.delete_user(session, 1)

    assert isinstance(response, Response)
    assert session.deleted == [user]


@pytest.mark.asyncio
async def test_user_crud_raises_when_missing():
    session = FakeSession(FakeResult(rowcount=0), FakeResult())

    with pytest.raises(NoResultFound):
        await CRUDUser.update(session, 1, {"nickname": "new"})
    with pytest.raises(NoResultFound):
        await CRUDUser.delete_user(session, 1)


@pytest.mark.asyncio
async def test_spot_crud_reads_filters_and_adds():
    spot = SimpleNamespace(spot_id=1)
    session = FakeSession(FakeResult(spot), FakeResult(rows=[spot]))

    assert await CRUDSpot.get_spot_by_id(session, 1) is spot
    assert await CRUDSpot.get_filtered_spots(
        session, schema.SpotFilterSchema(spot_country="France")
    ) == [spot]

    added = await CRUDSpot.add_spot(session, spot)
    assert added is spot
    assert session.added == [spot]


@pytest.mark.asyncio
async def test_spot_crud_update_and_delete_enforce_owner():
    spot = SimpleNamespace(spot_id=1)
    session = FakeSession(FakeResult(rowcount=1), FakeResult(spot))

    assert await CRUDSpot.update(
        session, 1, {"spot_name": "new"}, owner_id=7
    ) == "Spot with spot_id=1 is updated!"
    response = await CRUDSpot.delete_spot(session, 1, owner_id=7)

    assert isinstance(response, Response)
    assert session.deleted == [spot]


@pytest.mark.asyncio
async def test_spot_crud_raises_when_missing():
    session = FakeSession(FakeResult(rowcount=0), FakeResult())

    with pytest.raises(NoResultFound):
        await CRUDSpot.update(session, 1, {}, owner_id=7)
    with pytest.raises(NoResultFound):
        await CRUDSpot.delete_spot(session, 1, owner_id=7)


@pytest.mark.asyncio
async def test_comment_crud_reads_and_adds():
    comment = SimpleNamespace(comment_id=1)
    session = FakeSession(FakeResult(comment))

    assert await CRUDComment.get_comment_by_id(session, 1) is comment
    added = await CRUDComment.add_comment(session, comment)

    assert added is comment
    assert session.added == [comment]
