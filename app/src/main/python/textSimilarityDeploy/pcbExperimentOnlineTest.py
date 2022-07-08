"""
file: 
author: muyongli
create data: 2022/4/07 13:54
email: 1203962063@qq.com
description:  理化生实验文本相似度计算模型 线上服务验证。
"""

import json
import requests

if __name__ == "__main__":

    # requestData = {'examinationPaper': '化学试题1 配置100克5%的氯化钠溶液', 'answerDict': {'1': '5', '2': '94'},"style":{"1":""}}

    requestData = {"examinationPaper": "化学试题3 鉴别硬水和软水并软化硬水", 'answerDict': {'1': '浮渣较少的为硬水，浮渣较多的为软水'}}
    # requestData = {"examinationPaper": "化学试题3 鉴别硬水和软水并软化硬水", 'answerDict': {'1': ''}}

    # requestData = {'examinationPaper': '化学试题5 氧气的实验室制取-装置组装', 'answerDict': {'1': '2KMnO【&sub4】￥￥=【&condition加热】￥￥K【&sub2】MnO【&sub4】+MnO【&sub2】+O【&sub2】↑'}}
    # requestData = {'examinationPaper': '化学试题5 氧气的实验室制取-装置组装', 'answerDict': {'1': ''}, 'style': {'1': '<div class="boxItem spanText" ref="boxItem"><div class="textItem" style="width: 20px;"><span contenteditable="true" class="node-text contenteditable"></span></div></div>'}}

    # requestData = {'examinationPaper': '化学试题6 物理变化与化学变化的探究', 'answerDict': {'1': '物理', '2': '变蓝', '3': '化学', '4': '2NaOH+CuSO【&sub4】￥￥=【&condition】￥￥Cu(OH)【&sub2】↓&&+&&Na【&sub2】SO【&sub4】'}}

    # requestData =  {'examinationPaper': '化学试题7 用铁和硫酸铜溶液反应验证质量守恒定律', 'answerDict': {'1': '192.2', '2': '190',
    #                 '3': '铁钉表面生成红色固体物质，天平平衡', '4': '相等', '5': 'Fe&&+&&CuSO【&sub4】￥￥=【&condition】￥￥FeSO【&sub4】&&+&&Cu'}}

    # requestData = {'examinationPaper': '化学试题8 鉴别稀硫酸、氢氧化钠、碳酸钠、氯化钠溶液','answerDict': {'1': 'NaCl',
    #                '2': 'H【&sub2】SO【&sub4】',
    #                 '3': '气泡', '4': 'Na【&sub2】CO【&sub3】',
    #                 '5': 'Na【&sub2】CO【&sub3】&&+&&2HCl￥￥=【&condition】￥￥2NaCl&&+&&H【&sub2】O&&+&&CO【&sub2】↑', '6': 'NaCl',
    #                 '7': 'Na【&sub2】CO【&sub3】', '8': 'H【&sub2】SO【&sub4】', '9': 'NaOH'}}

    # requestData = {'examinationPaper': '化学试题9 酸和碱的化学性质', 'answerDict': {'1': '变红', '2': '不变色', '3': '变蓝', '4': '变红', '5': '有蓝色沉淀物',
    #                    '6': '2NaOH&&+&&CuSO【&sub4】￥￥=【&condition】￥￥Cu(OH)【&sub2】↓&&+&&Na【&sub2】SO【&sub4】', '7': '蓝色沉淀消失',
    #                     '8': 'Cu(OH)【&sub2】&&+&&2HCl￥￥=【&condition】￥￥CuCl【&sub2】&&+&&2H【&sub2】O'}}

    # requestData = {'examinationPaper': '化学试题10 探究盐酸中哪种粒子使紫色石蕊溶液变红色',
    #  'answerDict': {'1': 'H【&sup+】、Cl【&sup-】、H【&sub2】O', '2': '溶液变红', '3': 'H【&sup+】',
    #                 '4': 'Na【&sup+】、Cl【&sup-】、H【&sub2】O', '5': '无明显变化'}}

    # requestData = {'examinationPaper': '化学试题11 不饱和溶液转化为饱和溶液', 'answerDict': {'1': '降温冷却'}}

    # requestData = {'examinationPaper': '化学试题12 稀盐酸除铁锈', 'answerDict': {'1': '铁锈消失，溶液变为黄色',
    #                         '2': 'Fe【&sub2】O【&sub3】&&+&&6HCl￥￥=【&condition】￥￥2FeCl【&sub3】+3H【&sub2】O'}}

    # requestData =  {'examinationPaper': '物理试题1 探究串联电路中各处电流的关系', 'answerDict': {'1': '0.23', '2': '0.22', '3': '0.25', '4': '相等'}}

    # requestData = {'examinationPaper': '物理试题2 探究串联电路中用电器两端的电压与电源两端电压的关系', 'answerDict': {'1': '1.7', '2': '0.8', '3': '2.5', '4': '等于'}}

    # requestData = {'examinationPaper': '物理试题2 探究串联电路中用电器两端的电压与电源两端电压的关系', 'answerDict': {'1': '', '2': '', '3': '', '4': '==='}}

    ### 字符串中还有字符串的情况如何处理，得把字符串里面的字符串处理掉。才可以用eval内置函数。
    # requestData = {'examinationPaper': '物理试题4 探究电磁铁的磁性强弱与电流大小的关系', 'answerDict': {'1': '0.3', '2': '5', '3': '弱', '4': '0.6', '5': '18', '6': '弱', '7': '强'}}

    # requestData = {'examinationPaper': '物理试题5 探究光反射时的规律', 'answerDict': {'1': '15', '2': '15', '3': '30', '4': '30', '5': '45', '6': '56', '7': '等于'}}
    # requestData = {'examinationPaper': '物理试题5 探究光反射时的规律',
    #  'answerDict': {'1': '30', '2': '32', '3': '45', '4': '45', '5': '70', '6': '70', '7': '='}}

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

    # requestData = {'examinationPaper': '物理试题9 测量蜡块的密度', 'answerDict': {'1': '14.1', '2': '44', '3': '60', '4': '16', '5': '0.9'}}

    # requestData = {'examinationPaper': '物理试题10 探究滑动摩擦力大小与接触面粗糙程度的关系', 'answerDict': {'1': '0-2.5', '2': '0.05', '3': '0.35', '4': '0.75', '5': '大'}}

    # requestData = {'examinationPaper': '物理试题11 探究杠杆的平衡条件', 'answerDict': {'1': '0.5', '2': '10', '3': '5', '4': '1', '5': '5', '6': '5',
    #                                     '7': '1.5', '8': '10', '9': '15', '10': '1.0', '11': '15.0', '12': '15', '13': '等于'}}

    # requestData = {'examinationPaper': '物理试题12 探究浮力大小与物体排开液体体积的关系', 'answerDict': {'1': '1.4', '2': '1', '3': '0.6', '4': '0.4', '5': '0.8', '6': '大'}}

    # s = requests.session()
    #
    # s.keep_alive = False

    headers = {
        "Content-Type": "application/json",
        # 'Connection': 'close'
    }
    obj = requests.post(url="http://localhost:9010/pcbExperiment", data=json.dumps(requestData),
                        headers=headers).content.decode()
    # obj = requests.post(url="http://192.168.122.32:9010/pcbExperiment", data=json.dumps(requestData),
    #                     headers=headers).content.decode()  #开发环境
    # obj = requests.post(url="http://218.26.98.206:49010/pcbExperiment", data=json.dumps(requestData),
    #                     headers=headers).content.decode()  #测试环境
    print(eval(obj))

