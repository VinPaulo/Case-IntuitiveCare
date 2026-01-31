from pydantic import BaseModel, Field
from typing import List, Optional

class OperadoraBase(BaseModel):
    razao_social: str
    cnpj: str
    uf: str

class OperadoraCreate(OperadoraBase):
    registro_operadora: int

class OperadoraUpdate(BaseModel):
    razao_social: Optional[str] = None
    uf: Optional[str] = None

class OperadoraResponse(OperadoraBase):
    registro_ans: int

    class Config:
        from_attributes = True

class PaginatedOperadoras(BaseModel):
    data: List[OperadoraResponse]
    total: int
    page: int
    limit: int

class DespesaResponse(BaseModel):
    ano: int
    trimestre: int
    valordespesas: float

class TopOperadora(BaseModel):
    razao_social: str
    total_despesa: float

class EstatisticasResponse(BaseModel):
    total_geral: Optional[float]
    media_geral: Optional[float]
    top_5: List[TopOperadora]

class DespesaUF(BaseModel):
    uf: str
    total_despesa: float
    media_por_operadora: float

class CrescimentoOperadora(BaseModel):
    razao_social: str
    crescimento: Optional[float]
