import re
import tiktoken
import math
import json
import sys
import socket
import pandas as pd

from xml.sax.saxutils import unescape
from bs4 import BeautifulSoup

# 共通ファンクションの読込(Reading common functions)
from functions import mysqlaio_fnc
from functions import log_fnc
from functions import secure_fnc

async def getApikey(objDbPool):
    """
    認証キー取得(Certification key acquisition)

    REST API用の認証キーをMySQLから取得(Authentication keys for REST API from MySQL)

    Args:

        objDbPool (object): コネクションプーリング

    Returns:

        str:認証キー(authentication key)
    """

    aryPythonAuthorizationKey = await mysqlaio_fnc.getPythonAuthorizationKey(objDbPool)

    return aryPythonAuthorizationKey

def getCleanText(strText: str):
    """
    HTMLタグ・改行・空白の削除(Removal of HTML tags, line breaks and white space)

    指定のテキストからHTMLタグ・改行・空白の削除(Removal of HTML tags, line breaks and whitespace from specified text)

    Args:

        strText (str): テキスト(text)

    Returns:

        str:除去されたテキスト(Text with unnecessary material removed)
    """

    # 特殊タグのデコード(Decoding of special tags)
    strText = unescape(strText)
    strText = strText.replace('&nbsp;', ' ')

    # 前後の空白の削除(Deletion of preceding and following spaces)
    strText = strText.strip()

    # 連続した空白の削除(Deletion of consecutive spaces)
    strText = strText.replace('　', '')
    strText = strText.replace(' ', '')
    strText = re.sub('\s+', ' ', strText)

    # HTMLタグの削除(Delete HTML tags)
    strText = re.sub('<.+?>', '', strText)

    # 改行を削除(Remove line breaks)
    strText = strText.replace('\n', '')
    strText = strText.replace('\r\n', '')
    strText = strText.replace('\r', '')
    
    return strText

def getOrthopedicsTime(intTime: int):
    """
    timeのフォーマット(Format of time)

    timモジュールを「00:00:00」の形にフォーマットする(Format the tim module in the form '00:00:00')

    Args:

        intTime (int): time(time)

    Returns:

        str:フォーマットされたテキスト(Formatted text)
    """

    intHour = intTime // 3600
    intMinute = (intTime % 3600) // 60
    intSecond = (intTime % 3600 % 60)

    return str(intHour).zfill(2) + ":" + str(intMinute).zfill(2) + ":" + str(intSecond).zfill(2)

def getEncodeDictToUtf8(objInputDict):
    """
    エンコード変換(encode conversion)

    辞書等のデータをループしてUTF-8に変換する(Looping through dictionaries and other data and converting them to UTF-8)

    Args:

        objInputDict (mix): 辞書などのデータ(Dictionaries and other data)

    Returns:

        mix:エンコードされた辞書等のデータ(Encoded dictionaries and other data)
    """
    for key, value in objInputDict.items():
        if isinstance(value, str):
            objInputDict[key] = value.encode('utf-8').decode('utf-8')
        elif isinstance(value, dict):
            objInputDict[key] = getEncodeDictToUtf8(value)
        elif isinstance(value, list):
            newList = []
            for item in value:
                if isinstance(item, dict):
                    newList.append(getEncodeDictToUtf8(item))
                elif isinstance(item, str):
                    newList.append(item.encode('utf-8').decode('utf-8'))
                else:
                    newList.append(item)
            objInputDict[key] = newList
                
    return objInputDict

def getConvertSize(intSize, strUnit="B"):
    """
    バイト単位変換(byte conversion)

    バイトから指定の単位に変換する(Convert from bytes to specified units)

    Args:

        intSize (int): バイトデータ(byte data)

        strUnit (str): 変換する単位(Unit of measure to be converted)

    Returns:

        str:変換した値(Converted value)

    Note:

        単位(unit):"B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"
    """

    aryUnits = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
    i = aryUnits.index(strUnit.upper())
    intSize = round(intSize / 1024 ** i, 2)

    return f"{intSize} {aryUnits[i]}"

async def getJoinStrings(strS1, strS2):
    """
    文字列同士を結合するときに末尾が重複している部分を削除して結合する(When merging strings, delete duplicate endings and merge them together.)

    Args:

        strS1 (str): ベース文字列(base string)

        strS2 (str): 結合する文字列(String to be combined)

    Returns:

        str:結合文字列(combined character string)
    """

    for i in range(min(len(strS1), len(strS2)), -1, -1):
        if strS1.endswith(strS2[:i]):
            return strS1 + strS2[i:]
        
    return strS1 + strS2

async def getIpAddress():
    """
    アクセスしている人のIPアドレスの取得(Obtaining the IP address of the person accessing the site)

    Returns:

        str:IPアドレス(IP address
    """

    # ホスト名を取得、表示
    strHost = socket.gethostname()
    strIp = socket.gethostbyname(strHost)
    aryLogExtra = { 'clientip' : strIp }

    return aryLogExtra

async def getGmoErrorMsg(strErrorCode :str, strErrorInfo :str):
    """
    GMOペイメントのエラーコードからメッセージを取得(Get message from GMO Payments error code)

    Args:

        strErrorCode (str): エラーコード(error code)

        strErrorInfo (str): 詳細コード(detail code)

    Returns:

        str:GMOエラーメッセージ[取得できない場合は空](GMO error message [empty if not obtained])
    """

    aryGmoErrorFile = []

    if strErrorCode.upper()[0] == "E":
        aryGmoErrorFile.append("gmo_e")
        aryGmoErrorFile.append("gmo_e_m")
    elif strErrorCode.upper()[0] == "C":
        aryGmoErrorFile.append("gmo_c")
    elif strErrorCode.upper()[0] == "G":
        aryGmoErrorFile.append("gmo_g")
    elif strErrorCode.upper()[0] == "M":
        aryGmoErrorFile.append("gmo_m")
        aryGmoErrorFile.append("gmo_e_m")
        aryGmoErrorFile.append("gmo_carrier")
        aryGmoErrorFile.append("gom_linepay")
    else:
        return ""

    strGmoErrorMsg = ""
    for strFileName in aryGmoErrorFile:
        # HTMLファイルを開く
        with open(f'./files/gmo/{strFileName}.html', 'r') as file:
            html = file.read()

        # BeautifulSoupオブジェクトを作成
        soup = BeautifulSoup(html, 'html.parser')

        # テーブルを見つける
        table = soup.find('table')

        # 全てのテーブルを見つける
        tables = soup.find_all('table')

        # 二番目のテーブルを選択
        table = tables[1]

        # 各行をループし、検索条件に一致するものを探す
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                # 例: エラーコード 'G02' に一致する行を探す
                if strErrorInfo in cells[1].text:
                    # 条件に一致した行のデータを出力（または他の処理）
                    if strFileName == "gmo_m" or strFileName == "gmo_carrier" or strFileName == "gom_linepay" or strFileName == "gmo_paysle":
                        strGmoErrorMsg = cells[2].text
                    else:
                        strGmoErrorMsg = cells[3].text
                    break
        
        if strGmoErrorMsg != "":
            break
    
    if strGmoErrorMsg == "－":
        return ""

    return strGmoErrorMsg