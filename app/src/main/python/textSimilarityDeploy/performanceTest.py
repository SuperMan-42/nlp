# -*- coding: utf-8 -*-
# @Time : 2022/6/29 18:41
# @Author : 慕永利
# @FileName : performanceTest.py
# @Email : 1203962063@qq.com
# @Description : 性能自动化测试脚本

import os
import re
import time
import datetime
import requests
import json
from textSimilarityDeploy.pcbIntelligentMarking import ExaminationPaperJudge, ExaminationPaperEvaluateScore


def singleOnlineRequestInterface(requestData):
    """
    线上测试接口
    """
    headers = {
            "Content-Type": "application/json",
            # 'Connection': 'close'
        }
    obj = requests.post(url="http://localhost:9010/pcbExperiment", data=json.dumps(requestData),
                        headers=headers).content.decode()
    # # obj = requests.post(url="http://192.168.122.32:9010/pcbExperiment", data=json.dumps(requestData),
    # #                     headers=headers).content.decode()  #开发环境
    # obj = requests.post(url="http://218.26.98.206:49010/pcbExperiment", data=json.dumps(requestData),
    #                     headers=headers).content.decode()  #测试环境
    # print(eval(obj))
    return eval(obj)


def singleOfflineRequestInterface(requestData):
    """
    线下测试接口
    """
    # 对题进行判对对错。
    judgeObject = ExaminationPaperJudge()
    resultJson = judgeObject.getPcbJudgeResult(requestData)

    # print(resultJson)

    # 根据评分细则进行评分。
    markObject = ExaminationPaperEvaluateScore()
    resultJson = markObject.scoreEvaluate(resultJson)

    del judgeObject
    del markObject

    return resultJson



def test_NLP_OnLine_Interface(testType="online"):
    """
    性能自动化测试的脚本。
    """
    print("开始进行性能测试！")
    print("-"*80)
    allDictData = {}
    keyList = []
    # 读取训练数据并且重构
    with open(file= os.path.dirname(__file__) + "/performanceTestData.txt", mode="r", encoding="utf-8") as fp:
        allTempLine = fp.readlines()
        for i in range(len(allTempLine)):
            # if i==18:
            #     print(i)
            if i == 0:
                tempList = re.split("\t",str(allTempLine[i]).strip())
                for j in range(len(tempList)):
                    allDictData[str(tempList[j]).strip()] = []
                    keyList.append(str(tempList[j]).strip())
            else:
                tempList = re.split("\t", str(allTempLine[i]).strip())
                for j in range(len(tempList)):
                    try:
                        allDictData[keyList[j]].append(eval(tempList[j]))
                    except Exception:
                        allDictData[keyList[j]].append(tempList[j])
    print(allDictData)
    # 读取测试数据并且重构

    for i in range(len(allDictData["requestData"])):
        startTime = datetime.datetime.now()
        # startTime1 = time.time()
        if testType == "online":
            resultData = eval(str(singleOnlineRequestInterface(requestData=allDictData["requestData"][i])))
        elif testType =="offline":
            try:
                resultData = eval(str(singleOfflineRequestInterface(requestData=allDictData["requestData"][i])))
            except Exception:
                resultData = eval(str(singleOfflineRequestInterface(requestData=allDictData["requestData"][i])))
        endTime = datetime.datetime.now()
        # endTime2 = time.time()
        # print(endTime2-startTime1)
        runTime = endTime - startTime
        print(runTime)
        # print(time.strftime('%Y{}%m{}%d{}  %H{}%M{}%S{}',time.localtime()).format("年", "⽉", "⽇", "时", "分", "秒"))
        print(datetime.datetime.now())

        allDictData["resultData"].append(resultData)
        allDictData["开始时间"].append(startTime)
        allDictData["结束时间"].append(endTime)
        allDictData["运行时间"].append(runTime)
    print(allDictData)

    filePath =  os.path.dirname(__file__) + "/performanceOnlineTestResultData.txt"
    if testType=="online":
        filePath =  os.path.dirname(__file__) + "/performanceOnlineTestResultData.txt"
    else:
        filePath =  os.path.dirname(__file__) + "/performanceOfflineTestResultData.txt"

    with open(file=filePath,mode="w",encoding="utf-8") as fp:
        fp.writelines(keyList[0]+"\t"+keyList[1]+"\t"+keyList[2]+"\t"+keyList[3]+"\t"+keyList[4]+"\t"+keyList[5]+"\n")
        for i in range(len(allDictData["requestData"])):
            fp.writelines(str(allDictData["requestData"][i]).strip()+"\t"+str(allDictData["examination_paper"][i]).strip()+"\t"
                          +str(allDictData["resultData"][i]).strip()+"\t"+str(allDictData["开始时间"][i]).strip()+"\t"
                          +str(allDictData["结束时间"][i]).strip()+"\t"+str(allDictData["运行时间"][i]).strip()+"\n")

    print("-"*80)
    print("性能测试结束")



def test():
    # test_NLP_OnLine_Interface(testType="online")
    test_NLP_OnLine_Interface(testType="offline")