from pydantic import BaseModel

class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int