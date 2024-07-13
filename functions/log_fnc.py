import json
import os
import logging
from logging import getLogger, config
from datetime import datetime

class CustomFormatter(logging.Formatter):
    def format(self, record):
        # clientipがrecordにない場合は、デフォルト値'unknown'を使用
        record.clientip = getattr(record, 'clientip', 'unknown')
        return super(CustomFormatter, self).format(record)

async def setOutputLog():
    """
    ログオブジェクト作成(log-object creation)

    指定のフォーマットでログオブジェクト作成(Log object creation in specified format)

    Returns:

        bool:成功:検索結果 失敗:Fals](Success:search results Failure:False)
    """

    with open(os.getcwd() + '/log_config.json', 'r') as f:
        objLogConf = json.load(f)

    # ディレクトリが存在しなければ作成(If the directory does not exist, create it)
    # logs/{client_id}/20231104.logs
    strLogDir = os.getcwd() + '/logs/' + '/'
    if not os.path.isdir(strLogDir):
        os.makedirs(strLogDir)
        os.chmod(strLogDir, 0o777)

    # ファイル名をタイムスタンプで作成(Create file names with timestamps)
    strDatetimeDat = datetime.now()
    objLogConf["handlers"]["fileHandler"]["filename"] = \
        strLogDir + 'python-{}.logs'.format(strDatetimeDat.strftime("%Y%m%d"))


    # カスタムフォーマッタの設定
    for handler in objLogConf["handlers"].values():
        handler["formatter"] = "custom"

    objLogConf["formatters"]["custom"] = {
        "()": CustomFormatter,
        "format": "[%(asctime)s][%(clientip)s][%(name)s:%(lineno)s][%(funcName)s][%(levelname)s]: %(message)s"
    }

    config.dictConfig(objLogConf)

    objLogger = getLogger()
    return objLogger