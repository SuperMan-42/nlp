# -*- coding: utf-8 -*-
# @Time : 2022/5/12 14:53
# @Author : 慕永利
# @FileName : standardAnswerFileOpt.py
# @Email : 1203962063@qq.com
# @Description :  对标准答案文本进行处理


import re
import copy


def standardAnswerLoad(filePath):
    """
    进行模型的加载
    :return:
    """
    resDict = {}
    with open(file=filePath, mode="r", encoding="utf-8") as fp:
        tempKeyList = []
        allLineList = fp.readlines()
        lineNumber = len(allLineList)
        for i in range(0, lineNumber):
            # print(allLineList[i])
            tempList = re.split("\t", str(allLineList[i]).strip())
            if i == 0:
                for tempElem in tempList:
                    tempKeyList.append(str(tempElem).strip())
                    resDict[str(tempElem).strip()] = []
            else:
                for j in range(0, len(tempList)):
                    resDict[tempKeyList[j]].append(str(tempList[j]).strip())
    # print(RuleAndStandardAnswer)
    return resDict


def accordingToConditions(originalDict,paperValue="",paperId="",gapOrderList=[]):
    """
    根据条件，选取特定条件字典。
    :return:
    """
    newDict = copy.deepcopy(originalDict)
    dictKeyList = list(newDict.keys())
    indexList = []

    # '物理试题2 探究串联电路中用电器两端的电压与电源两端电压的关系'
    # '物理试题2 探究串联电路中用电器两端的电压与电源两端电压的关系'
    if paperId != "":
        for i in range(0,len(newDict["examination_paper_id"])):
            if paperId!="" and gapOrderList==[]:
                if str(paperId).strip() == str(newDict["examination_paper_id"][i]).strip():
                    indexList.append(i)
            elif paperId!="" and gapOrderList!=[]:
                for j in range(0,len(gapOrderList)):  # gapOrderList 的下标一定都在 range(0,len(newDict["examination_paper"])) 中， 是它的一个子集。
                    if str(paperId).strip() == str(newDict["examination_paper_id"][i]).strip() and str(gapOrderList[j]).strip() == str(newDict["gap_order"][i]).strip():
                        indexList.append(i)
    elif paperValue!="":
        for i in range(0,len(newDict["examination_paper"])):
            if paperValue!="" and gapOrderList==[]:
                if str(paperValue).strip() == str(newDict["examination_paper"][i]).strip():
                    indexList.append(i)
            elif paperValue!="" and gapOrderList!=[]:
                for j in range(0,len(gapOrderList)):  # gapOrderList 的下标一定都在 range(0,len(newDict["examination_paper"])) 中， 是它的一个子集。
                    if str(paperValue).strip() == str(newDict["examination_paper"][i]).strip() and str(gapOrderList[j]).strip() == str(newDict["gap_order"][i]).strip():
                        indexList.append(i)
    # if newDict["examination_paper"][0]=="化学试题3:鉴别硬水和软水并软化硬水":
    #     pass
    resDict = {}
    for tempKey in dictKeyList:
        resDict[tempKey] = []
        for tempIndex in indexList:
            resDict[tempKey].append(newDict[tempKey][tempIndex])
    # except Exception:
    #     pass
    return resDict

