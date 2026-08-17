from pydantic import BaseModel, Field, HttpUrl


class PresignRequest(BaseModel):
    content_type: str
    size_bytes: int = Field(gt=0)


class PresignResponse(BaseModel):
    upload_url: str
    key: str


class FotoConfirmar(BaseModel):
    key: str = Field(min_length=1, max_length=500)
    orden: int = Field(default=0, ge=0)


class FotoDesdeUrl(BaseModel):
    """Link de la tienda (o de la imagen) del que sacar la foto."""

    url: HttpUrl
    orden: int = Field(default=0, ge=0)
