import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Создаем приложение FastAPI с кастомными параметрами
# app = FastAPI(
#     title="My API",                # Название API
#     description="This API serves to demonstrate FastAPI with Swagger UI",  # Описание API
#     version="1.0.0",                # Версия API
#     docs_url="/swagger",            # Путь к Swagger UI
#     openapi_url="/custom_openapi.json"  # Путь к OpenAPI JSON
# )

# Настройки базы данных
# DB_CONFIG = {
#     'dbname': 'ml_db_test',
#     'user': 'postgres',
#     'password': 'wmHkTzoC}71u',
#     'host': '37.140.197.22',
#     'port': '5432'
# }
DB_CONFIG = ""


# Модель запроса
class QueryRequest(BaseModel):
    query: str

# Функция выполнения SQL-запроса
async def execute_sql(query: str):
    try:
        conn = await asyncpg.connect(DB_CONFIG)
        rows = await conn.fetch(query)
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при выполнении SQL-запроса: {query}, ошибка: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query")
async def query(request: QueryRequest):
    logger.info(f"Запрос /query: {request.query}")
    result = await execute_sql(request.query)
    return result

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    # Запускаем сервер, если скрипт запускается напрямую
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


