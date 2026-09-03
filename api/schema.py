from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class SchemaModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Error(BaseModel):
    message: str = Field(description="Error description",
                         examples=[404, 406, 500])
    code: int = Field(description="Error status code",
                      examples=["Not found",
                                "<Validation error description>",
                                "<Internal server error description>"],
                      )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None


class InputDataValidator(BaseModel):
    user_id: Optional[int] = Field(None, gt=0, le=2147483647)
    spot_id: Optional[int] = Field(None, gt=0, le=2147483647)
    comment_id: Optional[int] = Field(None, gt=0, le=2147483647)


class InputSpotDataValidator(BaseModel):
    spot_id:  Union[int, None] = Field(None, gt=0, le=2147483647)  # check int32 range
    spot_country: Union[str, None] = None
    spot_city: Union[str, None] = None
    spot_street: Union[str, None] = None
    owner_id: Union[int, None] = Field(None, gt=0, le=2147483647)  # check int32 range


class UserCreationSchema(SchemaModel):
    nickname: str
    first_name: str
    last_name: str
    user_pic: Union[str, None]
    email: str
    password: str
    premium_account_type: bool = False

class UserTerseSchema(SchemaModel):
    nickname: str
    email: str

class UserOpenSchema(SchemaModel):
    nickname: str
    first_name: str
    last_name: str
    user_pic: Union[str, None]
    friends: Union[List[str], None] = Field(default_factory=list)
    spot_photos: Union[List[str], None] = Field(default_factory=list)
    added_spots: Union[List[str], None] = Field(default_factory=list)
    favourite_spots: Union[List[str], None] = Field(default_factory=list)

class UserSchema(SchemaModel):
    nickname: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    user_pic: Union[str, None] = None
    email: Union[str, None] = None
    password: Union[str, None] = None
    premium_account_type: Union[bool, None] = None
    disabled: Union[bool, None] = None

class UserFullSchema(SchemaModel):
    nickname: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    user_pic: Union[str, None] = None
    email: Union[str, None] = None
    password: Union[str, None] = None
    premium_account_type: Union[bool, None] = None
    friends: Union[List[str], None] = Field(default_factory=list)
    spot_photos: Union[List[str], None] = Field(default_factory=list)
    added_spots: Union[List[str], None] = Field(default_factory=list)
    favourite_spots: Union[List[str], None] = Field(default_factory=list)
    created_at: datetime

class SpotSchema(SchemaModel):
    spot_name: str
    spot_pic: Union[str, None] = None
    spot_photos: List[str]
    spot_country: str
    spot_city: str
    spot_street: str
    spot_street_number: str
    spot_description: Union[str, None] = None
    spot_raiting: Optional[float] = Field(None, ge=0, le=5)
    comment: Union[List[str], None] = None
    sport_type: str = Field("skateboarding", min_length=3, max_length=20)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    owner_id: int

class SpotCreateSchema(SpotSchema):
    owner_id: Optional[int] = None


class SpotUpdateSchema(SchemaModel):
    spot_name: Union[str, None] = None
    spot_photos: Union[List[str], None] = None
    spot_country: Union[str, None] = None
    spot_city: Union[str, None] = None
    spot_street: Union[str, None] = None
    spot_street_number: Union[str, None] = None
    spot_description: Union[str, None] = None
    spot_raiting: Optional[float] = Field(None, ge=0, le=5)

class SpotFilterSchema(SchemaModel):
    spot_id:  Union[int, None] = Field(None, gt=0, le=2147483647)  # check int32 range
    spot_country: Union[str, None] = None
    spot_city: Union[str, None] = None
    spot_street: Union[str, None] = None
    owner_id: Union[int, None] = Field(None, gt=0, le=2147483647)  # check int32 range


class CommentNewSchema(SchemaModel):
    body: str
    spot_id: int = Field(gt=0, le=2147483647)

class CommentFullSchema(SchemaModel):
    comment_id: int
    body: str
    created_at: datetime
