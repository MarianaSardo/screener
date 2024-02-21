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
    instruments = db.query(Instruments).all()
    return [InstrumentsResponse(id=inst.id,
                                cedear_symbol=inst.cedear_symbol,
                                foreign_market=inst.foreign_market or "",
                                foreign_symbol=inst.foreign_symbol or "",
                                cedear_ratio=inst.cedear_ratio or 0,
                                foreign_ratio=inst.foreign_ratio or 0)
            for inst in instruments]


@router.get("/{symbol}", response_model=InstrumentsResponse, status_code=status.HTTP_200_OK)
async def get_by_symbol(db: db_dependency, symbol: str) -> InstrumentsResponse:
    inst_model = db.query(Instruments).filter(Instruments.foreign_symbol == symbol).first()
    if inst_model is not None:
        return InstrumentsResponse(**inst_model.__dict__)
    raise HTTPException(status_code=404, detail='Instrument no encontrado.')


@router.post("/create_instrument", status_code=status.HTTP_201_CREATED)
async def create_instrument(db: db_dependency, inst_request: InstrumentsRequest):
    existing_instrument = db.query(Instruments).filter(
        (Instruments.cedear_symbol == inst_request.cedear_symbol) |
        (Instruments.foreign_symbol == inst_request.foreign_symbol)
    ).first()

    if existing_instrument:
        raise HTTPException(status_code=400, detail="Instrumento ya existe con el mismo simbolo.")

    inst_model = models.Instruments(**inst_request.model_dump())

    db.add(inst_model)
    db.commit()

    return JSONResponse(content="Instrument creado exitosamente")


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_instrument(db: db_dependency,
                            inst_request: InstrumentsRequest,
                            id: int = Path(gt=0)):
    inst_model = db.query(Instruments).filter(Instruments.id == id).first()
    if inst_model is None:
        raise HTTPException(status_code=404, detail='Instrument no encontrado.')

    inst_model.cedear_symbol = inst_request.cedear_symbol
    inst_model.foreign_market = inst_request.foreign_market
    inst_model.foreign_symbol = inst_request.foreign_symbol
    inst_model.cedear_ratio = inst_request.cedear_ratio
    inst_model.foreign_ratio = inst_request.foreign_ratio

    db.commit()

    return JSONResponse(content=f"Instrument {id} modificado exitosamente")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instrument(db: db_dependency, id: int = Path(gt=0)):
    inst_model = db.query(Instruments).filter(Instruments.id == id).first()

    if inst_model is None:
        raise HTTPException(status_code=404, detail='Instrument no encontrado.')
    db.query(Instruments).filter(Instruments.id == id).delete()
    db.commit()

    return JSONResponse(content=f"Instrument {id} eliminado exitosamente")
