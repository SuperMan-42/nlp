# -*- coding: utf-8 -*-
# @Time : 2022/5/12 13:50
# @Author : 慕永利
# @FileName : mathLogicOperation.py
# @Email : 1203962063@qq.com
# @Description : 理化生数学和逻辑运算的知识。

import re
import copy

# 比较两个字符串的大小。
def cmpStr(str1,str2): # if str1>=str2 True，否则False
    cmpFlag = "middle"
    for i in range(0,min(len(str1),len(str2))):
        if str1[i]==str2[i]:
            continue
        elif str1[i]>str2[i]:
            cmpFlag = "True"
        else:
            cmpFlag = "False"
    if cmpFlag=="middle":
        if len(str1)<=len(str2):
            return True
        else:
            return False
    elif cmpFlag=="True":
        return True
    elif cmpFlag=="False":
        return False
    else:
        return False

# 对序列进行插入排序。
def insertionSort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and cmpStr(key,arr[j]):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def regexMatch(regex,x):
    """
     利用正则表达式进行匹配。
    :param x:
    :param regex:
    :return:
    """
    try:
        regex = re.sub("\s+","",regex).strip()
        regex = "^"+regex+"$"
        x = re.sub("\s+","",x).strip()
        if re.match(pattern=regex,string=x):
            return True
        else:
            return False
    except Exception:
        return False

def chemicalExpressionMatch(chemicalExpression,standardChemicalExpression):
    """
    对化学表达式进行比较
    :param chemicalExpression:
    :param standardChemicalExpression:
    :return:
    """
    try:
        standardChemicalExpression = re.sub("\s+", " ", str(standardChemicalExpression).strip())
        standardChemicalExpressionALLList = re.split("[、,，和与 ]+", standardChemicalExpression)
        # standardChemicalExpressionALLList.sort()
        standardChemicalExpressionALLList = insertionSort(standardChemicalExpressionALLList)
        if "" in standardChemicalExpressionALLList:
            standardChemicalExpressionALLList.remove("")


        chemicalExpression = re.sub("\s+", " ", chemicalExpression)
        chemicalExpressionAllList = re.split("[、，,和与 ]+", chemicalExpression)
        # chemicalExpressionAllList.sort()
        if "" in chemicalExpressionAllList:
            chemicalExpressionAllList.remove("")
        chemicalExpressionAllList = insertionSort(chemicalExpressionAllList)
    except Exception:
        return False

    if standardChemicalExpressionALLList == chemicalExpressionAllList:
        return True
    else:
        return False



def chemicalEquationMatch(chemicalExpression,standardChemicalExpression):
    """
    对化学方程式进行比较。
    :param chemicalExpression: 2KMnO【&sub4】￥￥=【&condition加热】￥￥K【&sub2】MnO【&sub4】+MnO【&sub2】+O【&sub2】↑
    :param standardChemicalExpression: 2KMnO【&sub4】￥￥(=【&condition加热】|=【&condition△】)￥￥K【&sub2】MnO【&sub4】+MnO【&sub2】+O【&sub2】↑
    :return:
    """
    try:
        chemicalExpression = copy.deepcopy(chemicalExpression)
        standardChemicalExpression = copy.deepcopy(standardChemicalExpression)

        standardChemicalExpression= re.sub("\s+", "", standardChemicalExpression)
        standardChemicalExpressionALLList = re.split("￥￥", standardChemicalExpression)
        standardReactantList = re.split("&&\+&&",standardChemicalExpressionALLList[0])
        standardConditions = standardChemicalExpressionALLList[1]
        standardResultantList = re.split("&&\+&&",standardChemicalExpressionALLList[2])
        # standardReactantList.sort()
        # standardResultantList.sort()
        standardReactantList = insertionSort(standardReactantList)
        standardResultantList = insertionSort(standardResultantList)



        chemicalExpression = re.sub("\s+", "", chemicalExpression)
        chemicalExpressionAllList = re.split("￥￥", chemicalExpression)
        reactantList = re.split("&&\+&&", chemicalExpressionAllList[0])
        conditions = chemicalExpressionAllList[1]
        resultantList = re.split("&&\+&&", chemicalExpressionAllList[2])
        # reactantList.sort()
        # resultantList.sort()
        reactantList = insertionSort(reactantList)
        resultantList = insertionSort(resultantList)

    except Exception:
        return False

    if reactantList == standardReactantList and resultantList == standardResultantList and re.match(standardConditions,conditions):
        return True
    else:
        return False


def numericalLogicOperation(jsonObj,rule,gapOrderList):
    """
    根据数值运算的逻辑关系进行相应的阅卷。
    :param jsonObj: 前端传过来的json串
    :param rule: 规则
    :param gapOrderList: 需要进行阅卷的填空题号。
    :return:
    """
    returnGapOrderList = []
    #   保留默认的几位小数。
    try:
        for i in gapOrderList:
            # if i==3:
            #     print(i)
            key1LayerList = list(rule[str(i)].keys())
            if "decimalNum" in key1LayerList:
                try:
                    if ("dataType" in key1LayerList) and rule[str(i)]["dataType"]=="int":
                        jsonObj["answerDict"][str(i)] = eval(jsonObj["answerDict"][str(i)])
                    else:
                        jsonObj["answerDict"][str(i)] = floatPlaceLimit(
                            x=eval(jsonObj["answerDict"][str(i)]),limitNum=int(rule[str(i)]["decimalNum"]))
                except Exception:
                    jsonObj["answerDict"][str(i)] = str(jsonObj["answerDict"][str(i)]).strip()
            else:
                try:
                    if ("dataType" in key1LayerList) and rule[str(i)]["dataType"] == "int":
                        jsonObj["answerDict"][str(i)] = eval(jsonObj["answerDict"][str(i)])
                    else:
                        jsonObj["answerDict"][str(i)] = floatPlaceLimit(
                            x=eval(jsonObj["answerDict"][str(i)]), limitNum=int(rule[str(i)]["decimalNum"]))
                except Exception:
                    jsonObj["answerDict"][str(i)] = str(jsonObj["answerDict"][str(i)]).strip()


        for i in gapOrderList:  # 这块必须循环两次，应为里面涉及到所有填空题所有序号的替换，所以切不可删除
            for j in gapOrderList:
                if "python" in rule[str(j)].keys():
                    for k in range(0,len(rule[str(j)]["python"])):
                        rule[str(j)]["python"][k] = re.sub("【" + str(i) + "】", " jsonObj[\"answerDict\"][str(" + str(i) + ")] ", rule[str(j)]["python"][k])
                        rule[str(j)]["python"][k] = re.sub("(两数之差|两数的差|两数差)", "twoNumDiff",rule[str(j)]["python"][k])
                        rule[str(j)]["python"][k] = re.sub("(数的绝对值|绝对值)", "numAbs", rule[str(j)]["python"][k])
                        rule[str(j)]["python"][k] = re.sub("数据类型", "isinstance", rule[str(j)]["python"][k])

                        rule[str(j)]["python"][k] = re.sub("匹配", "regexMatch", rule[str(j)]["python"][k]).strip()
                        rule[str(j)]["python"][k] = re.sub("小数", "float", rule[str(j)]["python"][k]).strip()
                        rule[str(j)]["python"][k] = re.sub("乘以", "*", rule[str(j)]["python"][k]).strip()
                        rule[str(j)]["python"][k] = re.sub("整数", "int", rule[str(j)]["python"][k]).strip()
                        rule[str(j)]["python"][k] = re.sub("￥", "\"", rule[str(j)]["python"][k]).strip()

        for i in gapOrderList:
            # if i==4:
            #     print(i)
            if "python" in rule[str(i)].keys():
                try:
                    judgeFlagDict = {"judgeFlag":False}
                    pythonStr = ""
                    for k in range(0,len(rule[str(i)]["python"])):
                        if pythonStr=="":
                            pythonStr = rule[str(i)]["python"][k]
                        else:
                            pythonStr = pythonStr+" or "+rule[str(i)]["python"][k]
                    pythonStr = "judgeFlagDict[\"judgeFlag\"]" + "=(" + pythonStr+")"
                    # ['isinstance( jsonObj["answerDict"][str(5)] ,float) and numAbs(twoNumDiff( jsonObj["answerDict"][str(5)] ,
                    # jsonObj["answerDict"][str(1)] / jsonObj["answerDict"][str(4)] ))<=0.1']
                    # 0.14     3.7358490
                    # 1.4749999999999999           1.49
                    exec(pythonStr)
                    if judgeFlagDict["judgeFlag"]:
                        returnGapOrderList.append(str(i))
                except Exception:
                    pass
    except Exception:
        pass

    return returnGapOrderList


def floatPlaceLimit(x,limitNum=2):
    """
    对浮点型小数的小数位数进行限定，并且对小数最末尾的进行四射五入。
    :param x:  输入的浮点型数值
    :param limitNum:  取值整数，表示保留几位小数。
    :return:
    """
    y = round(round(float(str(x).strip()),limitNum+3),limitNum)  #防止出现1.344999999这种数值的情况出现。
    return y


def twoNumDiff(x,y,limitNum=2):
    """
    求两个数差
    :param x:
    :param y:
    :return:
    """
    return floatPlaceLimit(floatPlaceLimit(x,limitNum=limitNum)-floatPlaceLimit(y,limitNum=limitNum),limitNum=limitNum)


def numAbs(x):
    """
    求两个数差值的绝对值。
    :param x:
    :param y:
    :return:
    """
    return abs(x)


def graphCurveCal(jsonObj,rule):
    """
    专门针对 物理试题8 中的  曲线图进行处理。
    :return:
    """
    judgeFlag = True
    try:
        for i in rule:
            try:
                jsonObj["answerDict"][str(i)] = floatPlaceLimit(jsonObj["answerDict"][str(i)])
            except Exception:
                jsonObj["answerDict"][str(i)] = str(jsonObj["answerDict"][str(i)]).strip()

        gap15 = eval(jsonObj["answerDict"][str(15)])
        for i in range(0,len(gap15)):
            tempGap = gap15[i]
            tempIndex = tempGap["index"]
            if numAbs(twoNumDiff(floatPlaceLimit(tempGap["y"]),jsonObj["answerDict"][str(tempIndex).strip()]))>0.5:
                judgeFlag=False
                break
    except Exception:
        judgeFlag = False
    return judgeFlag





if __name__ == "__main__":

    # x = 6.8759
    # y = floatPlaceLimit(x,limitNum=2)
    # print(y)

    x=1
    y=2
    expr = """
    z = 30
    sum = x+y+z
    print(sum)
    """
    resVal = exec(expr)
    print(resVal)
