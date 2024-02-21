from fastapi import FastAPI
import models
from database import engine
from routers import instruments, company_rating, stock_prices

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(instruments.router)
app.include_router(company_rating.router)
app.include_router(stock_prices.router)