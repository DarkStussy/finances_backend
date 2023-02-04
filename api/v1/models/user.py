from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str = Field(default=None, regex=r'\w{3,32}')
    password: str = Field(
        default=None,
        regex='^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])'
              '.{8,32}$'
    )
