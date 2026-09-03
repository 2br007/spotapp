import asyncio

from sqlalchemy import select

from api.db import SessionFactory
from api.models import SpotDBModel, UserDBModel
from api.utils import PasswordHasher
from seed_data import GIJON_SPOTS, SEED_USER


async def seed():
    async with SessionFactory() as session:
        async with session.begin():
            user = await session.scalar(
                select(UserDBModel).where(UserDBModel.email == SEED_USER["email"])
            )
            if user is None:
                user = UserDBModel(
                    **{key: value for key, value in SEED_USER.items()
                       if key != "password"},
                    password=PasswordHasher().hash_password(SEED_USER["password"]),
                )
                session.add(user)
                await session.flush()

            for spot_data in GIJON_SPOTS:
                existing = await session.scalar(
                    select(SpotDBModel).where(
                        SpotDBModel.spot_name == spot_data["spot_name"],
                        SpotDBModel.spot_city == spot_data["spot_city"],
                    )
                )
                if existing is None:
                    session.add(
                        SpotDBModel(
                            **spot_data,
                            spot_pic=None,
                            spot_photos=[],
                            comment=[],
                            spot_full_address=(
                                f"{spot_data['spot_street']}, "
                                f"{spot_data['spot_street_number']}, "
                                f"{spot_data['spot_city']}, "
                                f"{spot_data['spot_country']}"
                            ),
                            owner_id=user.user_id,
                        )
                    )

    print(f"Seeded {len(GIJON_SPOTS)} Gijon spots")


if __name__ == "__main__":
    asyncio.run(seed())
