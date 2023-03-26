from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(regex=r'\w{3,32}')
    password: str = Field(
        regex='^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])'
              '.{8,32}$'
    )
