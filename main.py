import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

# خواندن تنظیمات از فایل .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# اتصال به دیتابیس (echo=True باعث میشه دستورات SQL رو در ترمینال ببینی)
engine = create_engine(DATABASE_URL, echo=True)

# ۱. تعریف ساختار جدول در دیتابیس (Model)
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

# ۲. تعریف ساختاری که کاربر به API می‌فرسته (Schema)
class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: int | None = None

app = FastAPI()

# ساخت جدول‌ها در دیتابیس هنگام بالا آمدن برنامه
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI + SQLModel"}

# ۳. یک API برای ساختن کاربر جدید در دیتابیس
@app.post("/heroes/")
def create_hero(hero: HeroCreate):
    # تبدیل دیتای ورودی به مدل دیتابیس
    db_hero = Hero.model_validate(hero)
    
    # باز کردن یک نشست (Session) به دیتابیس و ذخیره کردن
    with Session(engine) as session:
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero) # گرفتن ID که دیتابیس به صورت خودکار ساخته
        return db_hero

# ۴. یک API برای خواندن تمام کاربران از دیتابیس
@app.get("/heroes/")
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes
    