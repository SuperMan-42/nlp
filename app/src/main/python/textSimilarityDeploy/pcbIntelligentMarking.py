# -*- coding: utf-8 -*-
# @Time : 2022/5/11 15:06
# @Author : 慕永利
# @FileName : pcbIntelligentMarking.py
# @Email : 1203962063@qq.com
# @Description : 理化生智能阅卷

import os
import copy
import re
from textSimilarityDeploy.standardAnswerFileOpt import standardAnswerLoad,accordingToConditions
from textSimilarityDeploy.mathLogicOperation import regexMatch,chemicalEquationMatch,numericalLogicOperation,chemicalExpressionMatch,graphCurveCal
from textSimilarityDeploy.albertSimilarityModelPredict import TextSimilarity_Model

class ExaminationPaperEvaluateScore():

    def __init__(self):
        """
        智能打分
        """
        # self.dict_markingStrategy = self.markStrategyStructured(standardAnswerLoad(filePath="../textSimilarityData/strategy/markingStrategy"))
        self.dict_markingStrategy = self.markStrategyStructured(standardAnswerLoad(filePath=os.path.dirname(__file__)+"/markingStrategy"))


    def markStrategyStructured(self,dic):
        """
        用eval内置函数将字典中的字符串转换为dict
        :param dic:
        :return:
        """
        for i in range(0,len(dic["marking_strategy"])):
            try:
                dic["marking_strategy"][i] = eval(str(dic["marking_strategy"][i]))
            except Exception:
                dic["marking_strategy"][i] = dic["marking_strategy"][i]
        return dic


    def scoreEvaluate(self,jsonObj):
        """
        根据评分策略给出整张试卷的得分。
        :param jsonObj:
        :return:
        """
        scoreStrategy = {}
        try:
            paperIndex = self.dict_markingStrategy["examination_paper_id"].index(str(jsonObj["examination_paper_id"]).strip())
        except Exception:
            paperIndex = self.dict_markingStrategy["examination_paper"].index(str(jsonObj["examinationPaper"]).strip())
        tempStrategy = copy.deepcopy(self.dict_markingStrategy["marking_strategy"][paperIndex])
        for score_point in tempStrategy.keys():
            tempGapList = tempStrategy[score_point]["gap"]
            tempJudgeFlag = True
            for i in tempGapList:
                if jsonObj["result"][str(i).strip()]["judge"] != "正确":
                    tempJudgeFlag = False
                    break
            if tempJudgeFlag == True:
                scoreStrategy[score_point] = tempStrategy[score_point]
            else:
                scoreStrategy[score_point] = tempStrategy[score_point]
                scoreStrategy[score_point]["score"] = "0分"
        jsonObj["scoreStrategy"] = scoreStrategy
        return jsonObj


class ExaminationPaperJudge():

    def __init__(self):
        """
        智能阅卷
        """
        # 记录文本答案的规则和标准答案等信息。
        # self.dict_textRuleAndStandardAnswer = standardAnswerLoad(filePath="../textSimilarityData/strategy/textRuleAndStandardAnswer")
        self.dict_textRuleAndStandardAnswer = standardAnswerLoad(filePath=os.path.dirname(__file__)+"/textRuleAndStandardAnswer")

        # self.dict_noneTextRuleAndStandardAnswer = standardAnswerLoad(filePath="../textSimilarityData/strategy/noneTextRuleAndStandardAnswer")
        self.dict_noneTextRuleAndStandardAnswer = standardAnswerLoad(filePath=os.path.dirname(__file__)+"/noneTextRuleAndStandardAnswer")

        # self.dict_standardAnswer = standardAnswerLoad(filePath="../textSimilarityData/strategy/standardAnswer")
        self.dict_standardAnswer = standardAnswerLoad(filePath=os.path.dirname(__file__)+"/standardAnswer")

        self.pcbModel = TextSimilarity_Model()
        # print(self.dict_noneTextRuleAndStandardAnswer)

    def returnJsonInit(self,singlePaperDict,jsonObj):
        """
        :param singlePaperDict: 当前试卷的所有填空，进行返回json串的初始化。
        :return:
        """
        resultJson = copy.deepcopy(jsonObj)
        # 首先对所有是否带的单位进行处理
        for i in range(1,len(resultJson["answerDict"].keys())+1):
            if singlePaperDict["unit"][i-1] == "no":
                continue
            else:
                resultJson["answerDict"][str(i)] = re.sub("\s+","",str(resultJson["answerDict"][str(i)]).strip()).strip()
                resultJson["answerDict"][str(i)] = re.sub(str(singlePaperDict["unit"][i-1])+"$","",str(resultJson["answerDict"][str(i)]))

        resultJson["result"] = {}
        if "examination_paper_id" in singlePaperDict.keys():
            for i in range(0,len(singlePaperDict["examination_paper_id"])):
                resultJson["result"][str(i+1).strip()] = {"judge":"错误","score":"0分","analysis":singlePaperDict["analysis"][i]}
        elif "examination_paper" in singlePaperDict.keys():
            for i in range(0, len(singlePaperDict["examination_paper"])):
                resultJson["result"][str(i + 1).strip()] = {"judge": "错误", "score": "0分","analysis": singlePaperDict["analysis"][i]}
        return resultJson

    def returnJsonModify(self,gapOrderList,resultJson,standardAnswerSet):
        """
        :param gapOrderList:
        :param resultJson:
        :param standardAnswerSet:
        :return:
        """
        for i in gapOrderList:
            tempIndex = standardAnswerSet["gap_order"].index(str(i))
            resultJson["result"][str(i)]["judge"] = "正确"
            resultJson["result"][str(i)]["score"] = "1分"
            resultJson["result"][str(i)]["analysis"] = standardAnswerSet["answer_analysis"][tempIndex]
        return resultJson

    def getPcbJudgeResult(self,jsonObj):
        """
        对前端求情过来的json串进行处理。
        :param jsonObj: web服务接口传送过来的试卷和作答答案。  已经是json状。
        :return:
        """
        #  前端传过来的试卷名字examinationPaper
        examination_paper_id = ""
        examinationPaper = ""
        if "examination_paper_id" in jsonObj.keys():
            examination_paper_id = re.sub("\s+","",str(jsonObj["examination_paper_id"])).strip()
        else:
            examinationPaper = re.sub("\s+"," ",str(jsonObj["examinationPaper"])).strip()

        # # 判断试卷的词典，从中选取前端过来的需要进行判卷的试卷信息。
        tempSinglePaperDict = {}
        if examination_paper_id != "":
            tempSinglePaperDict = accordingToConditions(originalDict=self.dict_standardAnswer,
                                                        paperId=examination_paper_id,
                                                        gapOrderList=[])  # 选取字典中是这张试卷的所有信息。
        elif examinationPaper!="":
            tempSinglePaperDict = accordingToConditions(originalDict=self.dict_standardAnswer,
                                                    paperValue=examinationPaper,
                                                    gapOrderList=[])  # 选取字典中是这张试卷的所有信息。
        ##  提前给当前试卷上的所有题设置默认的返回值
        resultJson = self.returnJsonInit(tempSinglePaperDict,jsonObj)

        currentPaperGapNum = len(jsonObj["answerDict"])  # 表示当前试卷总共有多少个填空题。
        i = 1

        haveJudge = [] #记录当前已经阅卷阅卷填空题序号至列表中。
        while(i < currentPaperGapNum+1):

            ######### 调试bug
            # if i==5:
            #     print(i)

            if i in haveJudge:  #表示当前填空题已经阅卷。
                i = i+1
                continue

            if tempSinglePaperDict["gap_related"][i-1] == "itself":   # 当和填空题和其他空没有逻辑关系，单个填空题的阅卷
                # # 获取到当前填空题 阅卷时需要的信息。
                tempSinglePaperSingleGapDict = {}
                if examination_paper_id != "":
                    tempSinglePaperSingleGapDict = accordingToConditions(originalDict=tempSinglePaperDict,
                                                                         paperId=examination_paper_id,
                                                                         gapOrderList=[i])
                else:
                    tempSinglePaperSingleGapDict = accordingToConditions(originalDict=tempSinglePaperDict,
                                                                     paperValue=examinationPaper,
                                                                     gapOrderList=[i])
                # # 获取到当前填空题 阅卷时需要的信息。

                if re.search("noneText",tempSinglePaperSingleGapDict["gap_type"][0]):
                    resultJson = self.noneTextJudge([i],resultJson)

                elif re.search("text",tempSinglePaperSingleGapDict["gap_type"][0]):
                    resultJson = self.textJudge([i],resultJson)

                haveJudge.append(i)

            else:
                # # 获取到当前填空题 阅卷时需要的信息。
                tempSinglePaperSingleGapDict = {}
                tempGapOrderList = eval(str(tempSinglePaperDict["gap_related"][i-1]))
                if examination_paper_id != "":
                    tempSinglePaperSingleGapDict = accordingToConditions(originalDict=tempSinglePaperDict,
                                                                         paperId=examination_paper_id,
                                                                         gapOrderList=tempGapOrderList)
                else:
                    tempSinglePaperSingleGapDict = accordingToConditions(originalDict=tempSinglePaperDict,
                                                                     paperValue=examinationPaper,
                                                                     gapOrderList=tempGapOrderList)
                # # 获取到当前填空题 阅卷时需要的信息。

                if re.search("noneText",tempSinglePaperSingleGapDict["gap_type"][0]):
                    resultJson = self.noneTextJudge(tempGapOrderList, resultJson)

                elif re.search("text",tempSinglePaperSingleGapDict["gap_type"][0]):
                    resultJson = self.textJudge(tempGapOrderList, resultJson)

                for j in tempGapOrderList:
                    haveJudge.append(j)

            i = i+1

        return resultJson



    def textJudge(self,gapOrderList,resultJson):
        """
        对文本答案的填空题进行阅卷
        :param gapOrderList: 需要进行阅卷的填空题 填空序号列表
        :param resultJson:
        :return:
        """
        textRuleAndStandardAnswer = copy.deepcopy(self.dict_textRuleAndStandardAnswer)  # 选取非文本阅卷的所有信息。
        if "examination_paper_id" in resultJson.keys():
            textRuleAndStandardAnswer = accordingToConditions(originalDict=textRuleAndStandardAnswer,
                                                              paperId=resultJson["examination_paper_id"],
                                                              gapOrderList=gapOrderList)
        else:
            textRuleAndStandardAnswer = accordingToConditions(originalDict=textRuleAndStandardAnswer,
                                                                  paperValue=resultJson["examinationPaper"],
                                                                  gapOrderList=gapOrderList)
        try:
            if len(gapOrderList) == 1:  # 文本阅卷都是单个填空题。不存在填空关联的问题。
                # 取单个试卷上的单个题
                tempMaxPro = 0
                tempAnswerAnalysis = ""
                tempJudge = "错误"
                tempIndexFlag = 0
                for i in range(0,len(textRuleAndStandardAnswer["answer_analysis"])):
                    ##########  这一块是预测代码的逻辑
                    probability, predict_index, predict_labels = self.pcbModel.predict(
                        text1=resultJson["answerDict"][str(gapOrderList[0]).strip()],
                        text2=textRuleAndStandardAnswer["standard_answer"][i], threshold=0.80)  # 预测产生相应的标签
                    ##########  这一块是预测代码的逻辑
                    # predict_labels = float(format(float(str(predict_labels).strip()), ".1f"))
                    if probability > tempMaxPro and probability >= 0.85 and predict_labels==1:  #首先必须保证是相似
                        tempIndexFlag = i
                        tempMaxPro = probability
                        tempAnswerAnalysis = textRuleAndStandardAnswer["answer_analysis"][i]
                        tempJudge = textRuleAndStandardAnswer["judge"][i]
                if tempJudge=="正确":
                    resultJson["result"][str(gapOrderList[0])]["judge"] = tempJudge
                    resultJson["result"][str(gapOrderList[0])]["analysis"] = tempAnswerAnalysis
                    resultJson["result"][str(gapOrderList[0])]["score"] = "1分"
                elif tempJudge == "错误":
                    resultJson["result"][str(gapOrderList[0])]["judge"] = "错误"
                    resultJson["result"][str(gapOrderList[0])]["analysis"] = textRuleAndStandardAnswer["answer_analysis"][0]
                    resultJson["result"][str(gapOrderList[0])]["score"] = "0分"
        except Exception:
            pass
        return resultJson


    def noneTextJudge(self,gapOrderList,resultJson):
        """
        对非文本填空题进行阅卷。
        :param gapOrderList: 需要进行阅卷的填空题 填空序号列表
        :param resultJson:
        :return:
        """
        tempNoneTextRuleAndStandardAnswer = copy.deepcopy(self.dict_noneTextRuleAndStandardAnswer)  #选取非文本阅卷的所有信息。
        if "examination_paper_id" in resultJson.keys():
            tempNoneTextRuleAndStandardAnswer = accordingToConditions(originalDict=tempNoneTextRuleAndStandardAnswer,
                                            paperId=resultJson["examination_paper_id"],gapOrderList=gapOrderList)
        else:
            tempNoneTextRuleAndStandardAnswer = accordingToConditions(originalDict=tempNoneTextRuleAndStandardAnswer,
                                                                      paperValue=resultJson["examinationPaper"],
                                                                      gapOrderList=gapOrderList)

        if len(gapOrderList)==1:
            # 取单个试卷上的单个题
            ruleType = tempNoneTextRuleAndStandardAnswer["rule_type"][0]

            if ruleType == "regex": #正则表达式
                curStandardAnswerRule = re.sub("\s+", "", str(tempNoneTextRuleAndStandardAnswer["rule"][0])).strip()
                if regexMatch(regex=curStandardAnswerRule,x=resultJson["answerDict"][str(gapOrderList[0]).strip()]):  #将前端学生作答和标准答案进行比对，如果是True，表示阅卷的结果是正确的。
                    resultJson = self.returnJsonModify(gapOrderList=gapOrderList,standardAnswerSet=tempNoneTextRuleAndStandardAnswer,
                                                       resultJson=resultJson)
            elif ruleType == "chemicalEquation": #化学方程式
                curStandardAnswerRule = re.sub("\s+", "", str(tempNoneTextRuleAndStandardAnswer["rule"][0])).strip()
                if chemicalEquationMatch(chemicalExpression=resultJson["answerDict"][str(gapOrderList[0]).strip()],
                                           standardChemicalExpression=curStandardAnswerRule):  #表示阅卷的结果是正确的。
                    resultJson = self.returnJsonModify(gapOrderList=gapOrderList,
                                                       standardAnswerSet=tempNoneTextRuleAndStandardAnswer,
                                                       resultJson=resultJson)
            elif ruleType == "chemicalExpression": #化学表达式
                if chemicalExpressionMatch(chemicalExpression=resultJson["answerDict"][str(gapOrderList[0]).strip()],
                                           standardChemicalExpression=str(tempNoneTextRuleAndStandardAnswer["rule"][0]).strip()):
                    resultJson = self.returnJsonModify(gapOrderList=gapOrderList,
                                                       standardAnswerSet=tempNoneTextRuleAndStandardAnswer,
                                                       resultJson=resultJson)

            elif ruleType == "numericalLogicOperation":
                curStandardAnswerRule = eval(re.sub("\s+", " ", str(tempNoneTextRuleAndStandardAnswer["rule"][0])).strip())
                returnGapOrderList = numericalLogicOperation(jsonObj=resultJson,
                                                             rule=curStandardAnswerRule,
                                                             gapOrderList=gapOrderList)
                if returnGapOrderList != []:
                    resultJson = self.returnJsonModify(gapOrderList=returnGapOrderList,
                                                       standardAnswerSet=tempNoneTextRuleAndStandardAnswer,
                                                       resultJson=resultJson)
            elif ruleType == "graphCurve":
                curStandardAnswerRule = eval(re.sub("\s+", " ", str(tempNoneTextRuleAndStandardAnswer["rule"][0])).strip())
                if graphCurveCal(jsonObj=resultJson,rule=curStandardAnswerRule):
                    resultJson = self.returnJsonModify(gapOrderList=gapOrderList,
                                                       standardAnswerSet=tempNoneTextRuleAndStandardAnswer,
                                                       resultJson=resultJson)


        elif len(gapOrderList)>1:
            ruleType = tempNoneTextRuleAndStandardAnswer["rule_type"][0]
            if ruleType == "numericalLogicOperation":
                curStandardAnswerRule = eval(re.sub("\s+", " ", str(tempNoneTextRuleAndStandardAnswer["rule"][0])).strip())
                # try:
                returnGapOrderList = numericalLogicOperation(jsonObj=resultJson,
                                                             rule=curStandardAnswerRule,
                                                             gapOrderList=gapOrderList)
                # except Exception:
                #     print(resultJson)
                if returnGapOrderList!=[]:
                    resultJson = self.returnJsonModify(gapOrderList=returnGapOrderList,
                                                       standardAnswerSet=tempNoneTextRuleAndStandardAnswer,
                                                       resultJson=resultJson)

        return resultJson


if __name__ == "__main__":

    # requestData = {'examinationPaper': '化学试题1 配置100克5%的氯化钠溶液',"examination_paper_id":"1400201", 'answerDict': {'1': '5', '2': '95'}}
    # requestData = {"examination_paper_id":"1400201", 'answerDict': {'1': '5', '2': '95'}}

    # requestData = {'examinationPaper': '化学试题3 鉴别硬水和软水并软化硬水', "examination_paper_id":"1400203",  'answerDict': {'1': '浮渣较多的是硬水，浮渣较少的是软水'}}
    # requestData = {"examination_paper_id": "1400203",'answerDict': {'1': '浮渣较多的是硬水，浮渣较少的是软水'}}

    # requestData =  {'examinationPaper': '化学试题5 氧气的实验室制取-装置组装', 'answerDict':
    #              {'1': '2KMnO【&sub4】￥￥=【&condition加热】￥￥MnO【&sub2】&&+&&K【&sub2】MnO【&sub4】&&+&&O【&sub2】↑'}}
    # requestData = {'examination_paper_id': '1400205', 'answerDict':
    #     {'1': '2KMnO【&sub4】￥￥=【&condition加热】￥￥MnO【&sub2】&&+&&K【&sub2】MnO【&sub4】&&+&&O【&sub2】↑'}}

    # requestData = {'examinationPaper': '化学试题5 氧气的实验室制取-装置组装', 'answerDict': {'1': ''}, 'style': {'1': '<div class="boxItem spanText" ref="boxItem"><div class="textItem" style="width: 20px;"><span contenteditable="true" class="node-text contenteditable"></span></div></div>'}}

    # requestData = {'examinationPaper': '化学试题6 物理变化与化学变化的探究',"examination_paper_id":"1400206", 'answerDict': {'1': '物理', '2': '蓝色沉淀', '3': '化学','4': '2NaOH&&+&&CuSO【&sub4】￥￥=【&condition】￥￥Na【&sub2】SO【&sub4】&&+&&Cu(OH)【&sub2】↓'}}

    # requestData =   {'examinationPaper': '化学试题7 用铁和硫酸铜溶液反应验证质量守恒定律', 'answerDict': {'1': '139.2', '2': '139.2', '3': '铁钉表面生成红色固定物质，天平平衡', '4': '我不会做',
    #                     '5': 'Fe&&+&&CuSO【&sub4】￥￥=【&condition】￥￥FeSO【&sub4】&&+&&Cu'}}
    # requestData = {'examinationPaper': '化学试题7 用铁和硫酸铜溶液反应验证质量守恒定律',
    #  'answerDict': {'1': '', '2': '', '3': '溶液变为浅绿色，产生红色物体，天平未倾斜', '4': '', '5': ''}}

    requestData =  {'examinationPaper': '化学试题8 鉴别稀硫酸、氢氧化钠、碳酸钠、氯化钠溶液', 'answerDict': {'1': 'NaCl', '2': 'H【&sub2】SO【&sub4】', '3': '气泡', '4': 'Na【&sub2】CO【&sub3】', '5': 'Na【&sub2】CO【&sub3】&&+&&2HCL￥￥=【&condition】￥￥2NaCl&&+&&H【&sub2】O&&+&&CO【&sub2】↑', '6': 'NaCl', '7': 'Na【&sub2】CO【&sub3】', '8': 'H【&sub2】SO【&sub4】', '9': 'NaOH'}}

    # requestData = {'examinationPaper': '化学试题9 酸和碱的化学性质', 'answerDict': {'1': '变红', '2': '不变色', '3': '变蓝', '4': '变红', '5': '有红色沉淀',
    #                    '6': '2NaOH&&+&&CuSO【&sub4】￥￥=【&condition】￥￥Cu(OH)【&sub2】↓&&+&&Na【&sub2】SO【&sub4】', '7': '蓝色沉淀消失',
    #                     '8': 'Cu(OH)【&sub2】&&+&&2HCl￥￥=【&condition】￥￥CuCl【&sub2】&&+&&2H【&sub2】O'}}

    # requestData = {'examinationPaper': '化学试题10 探究盐酸中哪种粒子使紫色石蕊溶液变红色',
    #  'answerDict': {'1': 'H【&sup+】,Cl【&sup-】,H【&sub2】O,', '2': '溶液变红', '3': 'H【&sup+】',
    #                 '4': 'Na【&sup+】和Cl【&sup-】和H【&sub2】O', '5': '无明显变化'}}

    # requestData = {'examinationPaper': '化学试题11 不饱和溶液转化为饱和溶液', 'answerDict': {'1': '降温冷却'}}

    # requestData = {'examinationPaper': '化学试题12 稀盐酸除铁锈', 'answerDict': {'1': '铁锈消失，溶液变为黄色',
    #                         '2': 'Fe【&sub2】O【&sub3】&&+&&6HCl￥￥=【&condition】￥￥2FeCl【&sub3】+3H【&sub2】O'}}

    # requestData =  {'examinationPaper': '物理试题1 探究串联电路中各处电流的关系', 'answerDict': {'1': '0.23', '2': '0.22', '3': '0.25', '4': '相等'}}

    # requestData = {'examinationPaper': '物理试题2 探究串联电路中用电器两端的电压与电源两端电压的关系', 'answerDict': {'1': '1.7', '2': '0.8', '3': '2.5', '4': '等于'}}

    # requestData = {'examinationPaper': '物理试题2 探究串联电路中用电器两端的电压与电源两端电压的关系', 'answerDict': {'1': '', '2': '', '3': '', '4': '==='}}

    # requestData = {'examinationPaper': '物理试题3 测量小灯泡的额定功率', 'answerDict': {'1': '4', '2': '10'}}
    # requestData = {'examinationPaper': '物理试题3 测量小灯泡的额定功率', 'answerDict': {'1': '0.59', '2': '1.485'}}

    ### 字符串中还有字符串的情况如何处理，得把字符串里面的字符串处理掉。才可以用eval内置函数。
    # requestData = {'examinationPaper': '物理试题4 探究电磁铁的磁性强弱与电流大小的关系', 'answerDict': {'1': '0.3', '2': '5', '3': '弱', '4': '0.6', '5': '18', '6': '弱', '7': '强'}}

    # requestData = {'examinationPaper': '物理试题5 探究光反射时的规律', 'answerDict': {'1': '15', '2': '15', '3': '30', '4': '30', '5': '45', '6': '56', '7': '等于'}}
    # requestData = {'examinationPaper': '物理试题5 探究光反射时的规律', 'answerDict': {'1': '10', '2': '10', '3': '50度', '4': '50', '5': '30', '6': '30', '7': '='}}

    # requestData = {'examinationPaper': '物理试题6 探究平面镜成像时像与物的关系', 'answerDict': {'1': '7.1', '2': '7.1', '3': '相等', '4': '7.3', '5': '7.3', '6': '相等', '7': '相等', '8': '相等'}}

    # requestData = {'examinationPaper': '物理试题7 探究凸透镜成像的规律', 'answerDict': {'1': '35', '2': '倒立', '3': '缩小', '4': '实像', '5': '16', '6': '30', '7': '倒立', '8': '缩小', '9': '实像', '10': '16.7', '11': '16', '12': '倒立', '13': '放大', '14': '实像', '15': '35', '16': '18', '17': '倒立', '18': '放大', '19': '实像', '20': '30', '21': '倒立缩小的实像', '22': '倒立放大的实像'}}

    # requestData = {'examinationPaper': '物理试题8 探究水沸腾时温度变化的特点', 'answerDict': {'1': '30-100', '2': '1摄氏度', '3': '90', '4': '92',
    #                          '5': '96', '6': '100', '7': '100', '8': '100', '9': '100', '10': '100', '11': '100', '12': '100','13': '100',
    #                    '14': '保持不变', '15': '[{"index":3,"x":"0.0","y":"90.2"},{"index":4,"x":"0.5","y":"92.1"},{"index":5,"x":"1.0","y":"96.2"},'
    #                                        '{"index":6,"x":"1.5","y":"99.8"},{"index":7,"x":"2.0","y":"99.9"},{"index":8,"x":"2.5","y":"100.0"},'
    #                                        '{"index":9,"x":"3.0","y":"99.8"},{"index":10,"x":"3.5","y":"99.8"},{"index":11,"x":"4.0","y":"100.0"},'
    #                                        '{"index":12,"x":"4.5","y":"99.9"},{"index":13,"x":"5.0","y":"100.0"}]'}}
    # requestData = {'examinationPaper': '物理试题8 探究水沸腾时温度变化的特点',
    #  'answerDict': {'1': '0-100摄氏度', '2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '',
    #                 '11': '', '12': '', '13': '', '14': '', '15': ''}}

    # requestData =  {'examinationPaper': '物理试题10 探究滑动摩擦力大小与接触面粗糙程度的关系', 'answerDict': {'1': '0~2.5', '2': '0.05牛', '3': '0.01', '4': '', '5': '越大'}}

    # requestData = {'examinationPaper': '物理试题10 探究滑动摩擦力大小与接触面粗糙程度的关系', 'answerDict': {'1': '0-2.5', '2': '0.05', '3': '0.35', '4': '0.75', '5': '大'}}

    # requestData = {'examinationPaper': '物理试题11 探究杠杆的平衡条件', 'answerDict': {'1': '0.5', '2': '10', '3': '5', '4': '1', '5': '5', '6': '5',
    #                                     '7': '1.5', '8': '10', '9': '15', '10': '1.0', '11': '15.0', '12': '15', '13': '等于'}}


    # requestData = {'examinationPaper': '物理试题12 探究浮力大小与物体排开液体体积的关系', 'answerDict': {'1': '1.4', '2': '1', '3': '0.6', '4': '0.4', '5': '0.8', '6': '大'}}

    judgeObject = ExaminationPaperJudge()

    resultJson = judgeObject.getPcbJudgeResult(requestData)

    # print(resultJson)


    # 根据评分细则进行评分。
    markObject = ExaminationPaperEvaluateScore()

    resultJson = markObject.scoreEvaluate(resultJson)

    print(resultJson)


