from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse
import models
from database import SessionLocal
from models import Instruments

router = APIRouter(
    prefix='/instruments',
    tags=['instruments'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class InstrumentsRequest(BaseModel):
    cedear_symbol: str = Field(min_length=1, max_length=255)
    foreign_market: str = Field(min_length=1, max_length=255)
    foreign_symbol: str = Field(min_length=1, max_length=255)
    cedear_ratio: float = Field(gt=0, lt=100)
    foreign_ratio: float = Field(gt=0, lt=100)


class InstrumentsResponse(BaseModel):
    id: int
    cedear_symbol: str
    foreign_market: str
    foreign_symbol: str
    cedear_ratio: float
    foreign_ratio: float


@router.get("/", response_model=List[InstrumentsResponse], status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency) -> List[InstrumentsResponse]:
    instrumentos = db.query(Instruments).all()
    return [InstrumentsResponse(id=inst.id,
                                cedear_symbol=inst.cedear_symbol,
                                foreign_market=inst.foreign_market or "",
                                foreign_symbol=inst.foreign_symbol or "",
                                cedear_ratio=inst.cedear_ratio or 0,
                                foreign_ratio=inst.foreign_ratio or 0)
            for inst in instrumentos]


@router.get("/{symbol}", response_model=InstrumentsResponse, status_code=status.HTTP_200_OK)
async def get_by_symbol(db: db_dependency, symbol: str) -> InstrumentsResponse:
    simbolo = db.query(Instruments).filter(Instruments.foreign_symbol == symbol).first()
    if simbolo is not None:
        return InstrumentsResponse(**simbolo.__dict__)
    raise HTTPException(status_code=404, detail='Instrument no encontrado.')


@router.post("/create_instrument", status_code=status.HTTP_201_CREATED)
async def create_instrument(db: db_dependency, inst_request: InstrumentsRequest):
    inst_existe = db.query(Instruments).filter(
        Instruments.foreign_symbol == inst_request.foreign_symbol).first()

    if inst_existe:
        raise HTTPException(status_code=400, detail="Ya existe un instrument con el foreign_symbol que está intentando crear.")

    instrumento = models.Instruments(**inst_request.model_dump())

    db.add(instrumento)
    db.commit()

    return JSONResponse(content="Instrument creado con exito.")


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_instrument(db: db_dependency,
                            inst_request: InstrumentsRequest,
                            id: int = Path(gt=0)):
    instrumento = db.query(Instruments).filter(Instruments.id == id).first()
    if instrumento is None:
        raise HTTPException(status_code=404, detail='Instrument no encontrado.')

    instrumento.cedear_symbol = inst_request.cedear_symbol
    instrumento.foreign_market = inst_request.foreign_market
    instrumento.foreign_symbol = inst_request.foreign_symbol
    instrumento.cedear_ratio = inst_request.cedear_ratio
    instrumento.foreign_ratio = inst_request.foreign_ratio

    db.commit()

    return JSONResponse(content=f"Instrument {id} modificado exitosamente")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instrument(db: db_dependency, id: int = Path(gt=0)):
    instrumento = db.query(Instruments).filter(Instruments.id == id).first()

    if instrumento is None:
        raise HTTPException(status_code=404, detail='Instrument no encontrado.')
    db.query(Instruments).filter(Instruments.id == id).delete()
    db.commit()

    return JSONResponse(content=f"Instrument {id} eliminado exitosamente")
