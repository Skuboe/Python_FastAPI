# 起動方法
# docker exec -it python uvicorn main:app --reload --host 0.0.0.0
# docker exec -it python gunicorn -k uvicorn.workers.UvicornWorker --bind "0.0.0.0:8000" --reload main:app
# appはFastAPI()を読み込んでる変数となる
# --reloadはソースを変更した場合即時反映される
# 本番orテスト起動方法
# nohup uvicorn main:app --host 0.0.0.0
import os

from fastapi import Depends, FastAPI, status, HTTPException, Security, Request
from aiomysql import create_pool
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN

# エンドポイント管理(endpoint management)
from routers import test

# 共通ユーティリティの読込(Reading common utilities)
from util import util_cmn

# 環境変数へ登録[pip3 install python-dotenv](Register to environment variables [pip3 install python-dotenv])
from dotenv import load_dotenv
load_dotenv()

# APIリクエストのヘッダーに認証情報Authorizationという名前のフィールドを追加し、
# そのフィールドにAPIキーまたはトークンを設定
# Falseに設定されている場合、認証情報がなくてもエラーは発生しません
# Add a field named Authorization to the API request header,
# Set the API key or token in that field
# If set to False, no error will occur without authorization information
api_key_header = APIKeyHeader(name='Authorization', auto_error=False)

# データベース接続プールを取得するための関数
# Function to retrieve database connection pool
def get_db_pool(request: Request):
    return request.app.state.db_pool

# 認証チェック(authentication check)
# asyn 非同期対応のメソッドに定義(asyn Defined for asynchronous-enabled methods)
# await 非同期対応のメソッドを呼び出すときに宣言する(await Declared when calling asynchronous-compatible methods)
async def get_api_key(
    api_key_header: str = Security(api_key_header),
    db_pool=Depends(get_db_pool)
    ):

    correct_key: str = getenv("getApikey")

    if api_key_header in correct_key:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail=f"Could not validate credentials 1:{api_key_header} 2:{correct_key}"
        )

# FastAPIアプリケーションのインスタンスを作成
# Instantiate a FastAPI application
app = FastAPI()

# アプリケーションの起動時にデータベース接続プールを作成
# Create database connection pool at application startup
@app.on_event("startup")
async def startup():
    app.state.db_pool = await create_pool(
        host=os.getenv("MYSQL_LOCALHOST"),
        port=3306,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB"),
        autocommit=True,
        minsize=1,
        maxsize=10
    )

# アプリケーションの終了時にデータベース接続プールを閉じる
# Close the database connection pool when closing the application
@app.on_event("shutdown")
async def shutdown():
    app.state.db_pool.close()
    await app.state.db_pool.wait_closed()

# データベース接続プールを取得するための依存関数
def get_db_pool(request: Request):
    return request.app.state.db_pool

# Noneをわたすことで無効化できる(It can be disabled by handing over None)
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(test.router, dependencies=[Depends(get_api_key)])

# @app.get('/')から始まる関数をPath operation 関数(Path operation function for functions starting with @app.get('/'))
# GETで引数を指定する場合は{}で指定する(When specifying arguments in GET, use {})
#@app.get("/", status_code=status.HTTP_200_OK, tags=['root REST API'])

# GETの引数をつけるときは、id:intとメソッドの引数につけることでエラー時に原因特定に役立つ
# メソッドは↑から順位実行される
# When adding GET arguments, add id:int to the method argument to help identify the cause in case of an error
# Methods are executed in rank order from up
def read_root():
    return {"status": "ok"}

