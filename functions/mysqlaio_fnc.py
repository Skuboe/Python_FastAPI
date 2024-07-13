import os
import aiomysql
import math
import json

from fastapi import Request
from pydantic import BaseModel
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from typing import Optional, Any

# 共通ファンクションの読込(Reading common functions)
from functions import secure_fnc
from functions import log_fnc

from util import util_cmn

async def getQuery(objDbPool, strMethod, strSql: str="", aryParam: list=()):
    """
    SELECTベース処理(SELECT-based processing)

    SELECT処理時に利用する共通メソッド(Common methods used during SELECT processing)

    Args:

        objDbPool (object): コネクションプーリング

        strMethod (str): 呼び出しメソッド名(Calling method name)

        strSql (str): sql

        aryParam (list): params

    Returns:

        bool:成功:結果 失敗:Fals](Success:results Failure:False)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    # SQLが存在しなければfalseを返却(Return false if SQL does not exist)
    if strSql == "":
        return False

    try:
        async with objDbPool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(strSql, aryParam)
                aryData = await cur.fetchall()
    except aiomysql.Error as e:
        objLogger.critical(f"MySQL error [method:{strMethod}: sql:{strSql}] args:{e.args[0]} {e.args[1]}", extra=aryLogExtra)
        return False    

    return aryData

async def getFetchOneQuery(objDbPool, strMethod, strSql: str="", aryParam: list=()):
    """
    SELECTベース処理「fetchone」(SELECT-based processing)

    SELECT処理時に利用する共通メソッド(Common methods used during SELECT processing)

    Args:

        objDbPool (object): コネクションプーリング

        strMethod (str): 呼び出しメソッド名(Calling method name)

        strSql (str): sql

        aryParam (list): params

    Returns:

        bool:成功:結果 失敗:Fals](Success:results Failure:False)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    # SQLが存在しなければfalseを返却(Return false if SQL does not exist)
    if strSql == "":
        return False

    try:
        async with objDbPool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(strSql, aryParam)
                aryData = await cur.fetchone()
    except aiomysql.Error as e:
        objLogger.critical(f"MySQL error [method:{strMethod}: sql:{strSql}] args:{e.args[0]} {e.args[1]}", extra=aryLogExtra)
        return False    

    return aryData

async def execQuery(objDbPool, strMethod, strSql: str="", aryParam: list=()):
    """
    実行ベース処理(run-based processing)

    実行処理時に利用する共通メソッド(Common methods used during run processing)

    Args:

        objDbPool (object): コネクションプーリング

        strMethod (str): 呼び出しメソッド名(Calling method name)

        strSql (str): sql

        aryParam (list): params

    Returns:

        bool:成功:結果 失敗:Fals](Success:results Failure:False)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    # SQLが存在しなければfalseを返却(Return false if SQL does not exist)
    if strSql == "":
        return False

    try:
        async with objDbPool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(strSql, aryParam)
                await conn.commit()
    except aiomysql.Error as e:
        objLogger.critical(f"ERROR [Method-{strMethod}] {e.args[0]}: {e.args[1]}", extra=aryLogExtra)
        return False    

    return True

async def execQueryAndGetLastId(objDbPool, strMethod, strSql: str="", aryParam: list=()):
    """
    実行ベース処理且つINSERTしたIDを取得する(Execution-based processing and INSERTed IDs are retrieved)

    実行処理時に利用する共通メソッド(Common methods used during run processing)

    Args:

        objDbPool (object): コネクションプーリング

        strMethod (str): 呼び出しメソッド名(Calling method name)

        strSql (str): sql

        aryParam (list): params

    Returns:

        bool:成功:結果 失敗:Fals](Success:results Failure:False)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    # SQLが存在しなければfalseを返却(Return false if SQL does not exist)
    if strSql == "":
        return False

    try:
        async with objDbPool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(strSql, aryParam)
                await conn.commit()

                # Get last inserted id
                strSql = "SELECT LAST_INSERT_ID() as last_insert_id"
                aryParam = ()
                await cur.execute(strSql, aryParam)
                aryData = await cur.fetchone()
                if aryData == False:
                    return False

                intLastId = aryData["last_insert_id"]
    except aiomysql.Error as e:
        objLogger.critical(f"ERROR [Method-{strMethod}] {e.args[0]}: {e.args[1]}", extra=aryLogExtra)
        return False    

    return intLastId

