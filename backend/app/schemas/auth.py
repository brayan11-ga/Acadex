from pydantic import BaseModel, EmailStr, field_validator

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