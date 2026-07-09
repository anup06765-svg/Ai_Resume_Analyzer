from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class UserRegister(BaseModel):

    full_name: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=50
    )


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class UserResponse(BaseModel):

    id: int

    full_name: str

    email: EmailStr

    class Config:

        from_attributes = True