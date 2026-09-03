from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from api import routes, schema
from api.crud import CRUDComment, CRUDSpot, CRUDUser
from tests.sample import RAW_SPOT, RAW_USER


USER = SimpleNamespace(user_id=1, disabled=False)
OTHER_USER = SimpleNamespace(user_id=2, disabled=False)


def user_payload():
    return schema.UserCreationSchema(**RAW_USER)


def spot_payload():
    return schema.SpotCreateSchema(**RAW_SPOT)


def update_payload():
    return schema.SpotUpdateSchema(spot_name="updated")


def comment_payload():
    return schema.CommentNewSchema(body="comment", spot_id=1)


@pytest.mark.asyncio
async def test_user_routes_map_missing_and_internal_errors(monkeypatch):
    async def missing(*args, **kwargs):
        raise NoResultFound

    async def broken(*args, **kwargs):
        raise RuntimeError("database failure")

    monkeypatch.setattr(CRUDUser, "get_user_by_id", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.get_user(1, object())
    assert raised.value.status_code == 404

    monkeypatch.setattr(CRUDUser, "get_user_by_id", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.get_user(1, object())
    assert raised.value.status_code == 500

    monkeypatch.setattr(CRUDUser, "get_all_users", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.get_all_users(object())
    assert raised.value.status_code == 500


@pytest.mark.asyncio
async def test_create_user_maps_internal_errors(monkeypatch):
    async def broken(*args, **kwargs):
        raise RuntimeError("database failure")

    monkeypatch.setattr(CRUDUser, "add_user", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.create_user(user_payload(), object())
    assert raised.value.status_code == 500


@pytest.mark.asyncio
async def test_user_mutations_validate_ownership_and_missing_users(monkeypatch):
    with pytest.raises(HTTPException) as raised:
        await routes.update_user(2, schema.UserSchema(nickname="new"), object(), USER)
    assert raised.value.status_code == 403

    with pytest.raises(HTTPException) as raised:
        await routes.destroy_user(2, object(), USER)
    assert raised.value.status_code == 403

    async def missing(*args, **kwargs):
        raise NoResultFound

    monkeypatch.setattr(CRUDUser, "update", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.update_user(1, schema.UserSchema(nickname="new"), object(), USER)
    assert raised.value.status_code == 404

    monkeypatch.setattr(CRUDUser, "delete_user", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.destroy_user(1, object(), USER)
    assert raised.value.status_code == 404


@pytest.mark.asyncio
async def test_spot_create_and_get_map_internal_and_missing_errors(monkeypatch):
    async def broken(*args, **kwargs):
        raise RuntimeError("database failure")

    async def missing(*args, **kwargs):
        raise NoResultFound

    monkeypatch.setattr(CRUDSpot, "add_spot", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.create_spot(spot_payload(), object(), USER)
    assert raised.value.status_code == 500

    monkeypatch.setattr(CRUDSpot, "get_spot_by_id", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.get_spot_by_id(1, object())
    assert raised.value.status_code == 404

    monkeypatch.setattr(CRUDSpot, "get_spot_by_id", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.get_spot_by_id(1, object())
    assert raised.value.status_code == 500


@pytest.mark.asyncio
async def test_spot_filter_maps_empty_invalid_and_internal_results(monkeypatch):
    async def empty(*args, **kwargs):
        return []

    async def broken(*args, **kwargs):
        raise RuntimeError("database failure")

    with pytest.raises(HTTPException) as raised:
        await routes.get_spots(owner_id=0, db=object())
    assert raised.value.status_code == 406

    monkeypatch.setattr(CRUDSpot, "get_filtered_spots", empty)
    with pytest.raises(HTTPException) as raised:
        await routes.get_spots(db=object())
    assert raised.value.status_code == 404

    monkeypatch.setattr(CRUDSpot, "get_filtered_spots", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.get_spots(db=object())
    assert raised.value.status_code == 500


@pytest.mark.asyncio
async def test_spot_mutations_map_missing_errors_and_validate_ids(monkeypatch):
    async def missing(*args, **kwargs):
        raise NoResultFound

    monkeypatch.setattr(CRUDSpot, "update", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.update_spot(1, update_payload(), object(), USER)
    assert raised.value.status_code == 404

    monkeypatch.setattr(CRUDSpot, "delete_spot", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.destroy_spot(0, object(), USER)
    assert raised.value.status_code == 406

    with pytest.raises(HTTPException) as raised:
        await routes.destroy_spot(1, object(), OTHER_USER)
    assert raised.value.status_code == 404


@pytest.mark.asyncio
async def test_comment_routes_map_missing_and_internal_errors(monkeypatch):
    async def missing(*args, **kwargs):
        raise NoResultFound

    async def broken(*args, **kwargs):
        raise RuntimeError("database failure")

    monkeypatch.setattr(CRUDComment, "get_comment_by_id", missing)
    with pytest.raises(HTTPException) as raised:
        await routes.get_comment(1, object())
    assert raised.value.status_code == 404

    monkeypatch.setattr(CRUDComment, "get_comment_by_id", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.get_comment(1, object())
    assert raised.value.status_code == 500

    monkeypatch.setattr(CRUDComment, "add_comment", broken)
    with pytest.raises(HTTPException) as raised:
        await routes.create_comment(comment_payload(), object(), USER)
    assert raised.value.status_code == 500
