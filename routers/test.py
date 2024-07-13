import os
import json
import openai

from typing import Dict, List, TypedDict
from fastapi import APIRouter, Depends, status, HTTPException, Response, File, UploadFile, Form, Request
#from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter

import shutil

# 機能の切り出しはfunctionディレクトリに作成
from functions import vector_fnc
from functions import secure_fnc
from functions import mysqlaio_fnc
from functions import log_fnc
from functions import mail_fnc

# 共通ユーティリティの読込(Reading common utilities)
from util import util_cmn

# エンドポイント管理
router = APIRouter()

def getDbPool(request: Request):
    return request.app.state.db_pool

@router.post("/v1/test", status_code=status.HTTP_200_OK, tags=['development test REST API'])
async def get_v1_test(db_pool=Depends(getDbPool)):

    result_dict = {"text": ""}

    # 辞書をJSON形式に変換
    return result_dict