from fastapi import HTTPException

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os

# 共通ファンクションの読込(Reading common functions)
from functions import log_fnc

# 共通ユーティリティの読込(Reading common utilities)
from util import util_cmn

async def getOpensslDecrypt(strText: str=""):
    """
    復号化処理(decoding process)

    OpenSSLを利用した復号化(Decryption using OpenSSL)

    Args:

        strText (str): 復号化するテキスト(Text to be decrypted)

    Returns:

        bool:成功:復号結果 失敗:Fals](Success:decoding result Failure:False)
    
    Note

        復号化用のキーは、暁プロジェクト利用のものと同一にする(The key for decryption should be the same as the one used by the Dawn Project)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    if strText:
        # 鍵情報の取得(Obtaining key information)

        strKey = os.getenv("APP_ENCRYPT_KEY")
        if len(strKey) != 32:
            raise False
        
        try:
            # base64デコード
            strData = base64.b64decode(strText)

            # 初期化ベクトル（IV）を抽出
            intIvLength = algorithms.AES(strKey.encode()).block_size // 8
            strIv = strData[:intIvLength]
            strEncryptedText = strData[intIvLength:]

            # OpenSSLによる復号化（CBCモード）
            objCipher = Cipher(algorithms.AES(strKey.encode()), modes.CBC(strIv), backend=default_backend())
            strDecryptor = objCipher.decryptor()
            strDecrypted = strDecryptor.update(strEncryptedText) + strDecryptor.finalize()

            # PKCS7パディングの除去
            objPadder = padding.PKCS7(128).unpadder()
            strDecrypted = objPadder.update(strDecrypted) + objPadder.finalize()

            strDecrypted = strDecrypted.decode('utf-8')  # バイト列を文字列に変換
            intPadding = ord(strDecrypted[-1])
            strDecrypted = strDecrypted[:-intPadding]

            return strDecrypted
        
        except Exception as e:
            objLogger.critical(f"復号化処理エラー(Error to decrypted process) key:{strText} Exception:{e}", extra=aryLogExtra)
            return False

    else:
        raise False