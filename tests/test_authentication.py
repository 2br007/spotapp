from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from jose import JWTError

from api import authentication


@pytest.mark.asyncio
async def test_get_current_user_resolves_token_subject(monkeypatch):
    user = SimpleNamespace(email="user@example.com", disabled=False)

    async def get_user_by_email(db, email):
        assert email == user.email
        return user

    monkeypatch.setattr(authentication.CRUDUser, "get_user_by_email",
                        get_user_by_email)
    monkeypatch.setattr(authentication.jwt, "decode",
                        lambda *args, **kwargs: {"sub": user.email})

    result = await authentication.get_current_user("token", db=object())

    assert result is user


@pytest.mark.asyncio
async def test_get_current_user_rejects_unknown_subject(monkeypatch):
    async def get_user_by_email(db, email):
        return None

    monkeypatch.setattr(authentication.CRUDUser, "get_user_by_email",
                        get_user_by_email)
    monkeypatch.setattr(authentication.jwt, "decode",
                        lambda *args, **kwargs: {"sub": "missing@example.com"})

    with pytest.raises(HTTPException) as raised:
        await authentication.get_current_user("token", db=object())

    assert raised.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_active_user_rejects_disabled_user():
    disabled_user = SimpleNamespace(disabled=True)

    with pytest.raises(HTTPException) as raised:
        await authentication.get_current_active_user(disabled_user)

    assert raised.value.status_code == 403


@pytest.mark.asyncio
async def test_get_current_active_user_returns_enabled_user():
    user = SimpleNamespace(disabled=False)

    assert await authentication.get_current_active_user(user) is user


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token(monkeypatch):
    def decode(*args, **kwargs):
        raise JWTError

    monkeypatch.setattr(authentication.jwt, "decode", decode)

    with pytest.raises(HTTPException) as raised:
        await authentication.get_current_user("token", db=object())

    assert raised.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_token_without_subject(monkeypatch):
    monkeypatch.setattr(authentication.jwt, "decode",
                        lambda *args, **kwargs: {})

    with pytest.raises(HTTPException) as raised:
        await authentication.get_current_user("token", db=object())

    assert raised.value.status_code == 401


def test_create_access_token_uses_default_expiration():
    token = authentication.create_access_token({"sub": "user@example.com"})

    payload = authentication.jwt.decode(
        token, authentication.SECRET_KEY,
        algorithms=[authentication.ALGORITHM],
    )

    assert payload["sub"] == "user@example.com"
    assert "exp" in payload
