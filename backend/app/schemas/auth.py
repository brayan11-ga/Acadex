# schema/auth.py
from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.contrasena import Contrasena

class LoginRequest(BaseModel):
    correo_electronico: EmailStr
    contrasena: str

    @field_validator("contrasena")
    @classmethod
    def contrasena_no_vacia(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La contraseña no puede estar vacía")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordIn(BaseModel):
    correo_electronico:EmailStr

class ResetPasswordIn(BaseModel):
    token: str
    nueva_contrasena: Contrasena
