"""
file: 
author: muyongli
create data: 2022/4/10 14:14
email: 1203962063@qq.com
description:
"""


# import sys
# from pathlib import Path
# # import codecs
# # sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
#
# sys.path.insert(0, str(Path.cwd().parents[0]))
# sys.path.insert(0, str(Path.cwd().parents[0].parents[0]))
# sys.path.insert(0, str(Path.cwd().parents[0].parents[0].parents[0]))
# sys.path.insert(0, str(Path.cwd().parents[0].parents[0].parents[0].parents[0]))

import os
import json
import logging
from tornado.escape import json_decode
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from textSimilarityDeploy.pcbIntelligentMarking import ExaminationPaperEvaluateScore,ExaminationPaperJudge
from textSimilarityDeploy.performanceTest import test_NLP_OnLine_Interface
#### text2vec 的版本必须是1.0.4，其他的版本的话代码得重构

class OnlineAnswerCorrect():
    """
    线上模型预测，根绝预测给出策略结果
    """
    ########## 模型设置
    # pcbStrategy = PCBStrategy()

    judgeObj = ExaminationPaperJudge()   # 对每张试卷的每个填空题进行判断。
    scoreObj = ExaminationPaperEvaluateScore()   # 根据评分策略进行评估。

    ########## web服务设置
    webThreadNum = 100
    APP_PORT = 9010

    def setLogger(self):
        """
        设置日志
        :return:
        """
        ########## 日志设置
        logger = logging.getLogger('pcbExperiment')  # 参数形式是name='online_logger1'
        logger.setLevel(logging.INFO)
        # 设置日志等级,日志级别等级CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET,从最低等的日志开始记录
        # f_log = logging.FileHandler("../../log/pcbExperimentOnline.log", encoding="utf8", mode="w")
        f_log = logging.FileHandler( os.path.dirname(__file__) + "/pcbExperimentOnline.log", encoding="utf8", mode="w")
        # 设置日志的路径必须以当前脚本所在的当前目录为参照标准。
        # 设置日志的文件路径
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # 设置日志格式，下面语句中的name是online_logger1,levelname=logging.INFO
        f_log.setFormatter(formatter)
        logger.addHandler(f_log)
        # 将日志格式和日志文件建立桥梁
        logger.info("启动日志记录")
        return logger

    def onlinePredict(self,jsonObj):
        """
        从调用端取到输入的json串，然后对json串进行解析，经过模型预测，得到相应的结果。
        :param jsonStr:
        :return:
        """

        # resultJson = self.pcbStrategy.getPCBResult(jsonObj)
        # jsonObj["result"] = resultJson
        # return jsonObj

        resultJson = self.judgeObj.getPcbJudgeResult(jsonObj=jsonObj)
        resultJson = self.scoreObj.scoreEvaluate(jsonObj=resultJson)
        return resultJson



onlineObject = OnlineAnswerCorrect()
logger = onlineObject.setLogger()

class WebServiceHandler(RequestHandler):
    executor = ThreadPoolExecutor(onlineObject.webThreadNum)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    @gen.coroutine
    def post(self):
        try:
            inputs = json_decode(self.request.body)     #str(self.request.body,"gbk")
            logger.info("-" * 80)
            Res = yield self.single_thread_task(inputs)
        except Exception as e:
            logger.error(str(e))
            Res = {}
        self.write(json.dumps(Res))

    @run_on_executor
    def single_thread_task(self, inputs):
        try:
            logger.info("request value: " + str(inputs))
            Res = onlineObject.onlinePredict(inputs)
            logger.info("return value:  " + str(Res))
            return Res
        except Exception as e:
            logger.error(e)
            return {}


def deploy():
    """
    线上部署
    :return：None
    """
    online_app = Application(handlers=[('/pcbExperiment', WebServiceHandler)],   autoreload=False, debug=False)
    online_http_server = HTTPServer(online_app)
    online_http_server.listen(int(onlineObject.APP_PORT))
    logger.info('The service begin running')
    print("The service begin running")
    test_NLP_OnLine_Interface(testType="online")
    IOLoop.instance().start()



if __name__ == "__main__":
    deploy()



