from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, model_validator, field_serializer
from constants.roles import Roles

class TestUser(BaseModel):
    __test__ = False
    email: EmailStr
    fullName: str
    password: str = Field(..., min_length=8, max_length=20)
    passwordRepeat: str
    roles: list[Roles] = Field(default_factory=lambda: [Roles.USER])
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.passwordRepeat:
            raise ValueError("Пароли не совпадают")
        return self

    @field_serializer("roles", when_used="json")
    def serialize_roles(self, roles: list[Roles]) -> list[str]:
        return [role.value for role in roles]


class RegisterUserResponse(BaseModel):
    id: str = Field(min_length=1)
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    verified: bool
    banned: Optional[bool] = None
    roles: list[Roles]
    createdAt: datetime

    @field_serializer("roles", when_used="json")
    def serialize_roles(self, roles: list[Roles]) -> list[str]:
        return [role.value for role in roles]