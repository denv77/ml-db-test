import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import uvicorn
from mlx_lm import load, generate
import re

# model, tokenizer = load("mlx-community/DeepSeek-R1-Distill-Qwen-14B-4bit")
model, tokenizer = load("/Users/den/DeepSeek-R1-Distill-Qwen-14B-4bit")


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
#     'user': '',
#     'password': '',
#     'host': '',
#     'port': ''
# }
DB_CONFIG = ""

with open('ddl.txt', 'r') as file:
    ddl = file.read()

messages = [
    {"role": "system", "content": ddl},
]

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

    if tokenizer.chat_template is not None:
        messages.append({"role": "user", "content": request.query})
        prompt = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
    )

    response = generate(model, tokenizer, prompt=prompt, verbose=False, max_tokens=2048)
    logger.info(f"Ответ нейронки: {response}")
    messages.append({"role": "assistant", "content": response})

    sql = re.search('```sql(.*)```', response, re.S).group(1).strip()
    logger.info(f"SQL: {sql}")
    result = await execute_sql(sql)
    return result
    # return response

@app.get("/")
def read_root():
    return {"message": "Hello, Den!"}

if __name__ == "__main__":
    # Запускаем сервер, если скрипт запускается напрямую
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


