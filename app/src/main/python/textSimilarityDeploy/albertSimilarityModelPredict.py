# -*- coding: utf-8 -*-
# @Time : 2022/6/9 17:33
# @Author : 慕永利
# @FileName : albertSimilarityModelPredict.py
# @Email : 1203962063@qq.com
# @Description : albert 预测代码

import os
import re
import tensorflow.compat.v1 as tf

class TextSimilarity_Model():
    """
    利用模型进行文本相似度计算
    """
    label_list = [0,1]
    label_list.sort()
    do_lower_case = True  # 是不是转小写
    batch_size = 1
    max_seq_length = 100
    is_training = False
    use_one_hot_embeddings = False

    def __init__(self, max_seq_lenth=100):
        """ Creates graphs, sessions and restore models."""
        # self.pb_model_path = "../textSimilarityData/model/textSimilarityModel/textSimilarity_model.pb"    # 文本相似度计算的模型路径
        self.pb_model_path = os.path.dirname(__file__)+"/textSimilarity_model.pb"

        # self.bert_vocab_file = "../textSimilarityData/model/textSimilarityModel/vocab.txt"
        self.bert_vocab_file = os.path.dirname(__file__)+"/vocab.txt"

        self.max_seq_length = max_seq_lenth
        # 用户模型输入的时候应用
        self.vocabDict = self.loadVocab()  # 将汉字转换为索引的工具。

        with tf.gfile.GFile(self.pb_model_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())

        with tf.Graph().as_default() as self.graph:
            tf.import_graph_def(
                graph_def,
                input_map=None,
                return_elements=None,
                name='prefix',
                op_dict=None,
                producer_op_list=None)
        self.input_ids = self.graph.get_tensor_by_name('prefix/input_ids:0')
        self.input_mask = self.graph.get_tensor_by_name('prefix/input_mask:0')
        self.segment_ids = self.graph.get_tensor_by_name('prefix/segment_ids:0')  # 按照当时转换为pd模型的时候转换的输入设置的输入。
        self.probabilities = self.graph.get_tensor_by_name('prefix/softmax/probabilities:0')
        self.sess = tf.Session(graph=self.graph)
        _, _, _ = self.predict(text1="化学", text2="物理", threshold=0.80)

    def loadVocab(self):
        """
        加载词典。
        :return:
        """
        tempDict = {}
        with open(file=self.bert_vocab_file, mode="r", encoding="utf-8") as fp:
            allLine = fp.readlines()
            for i in range(0, len(allLine)):
                tempDict[str(allLine[i]).strip()] = i
        return tempDict

    def sentence2wordId(self, x):
        """
        将word映射为相应的id。
        :return:
        """
        wordIdList = []
        for word in x:
            try:
                wordIdList.append(self.vocabDict[str(word).strip()])
            except Exception:
                wordIdList.append(self.vocabDict["[UNK]"])
        return wordIdList

    def apply_function_to_str(self, x):
        x = re.sub("\s+", " ", str(x)).lower().strip()
        x = re.sub("[^，。！？,;；\s\.\?!\[\]0-9a-z\u4e00-\u9fa5]", "", x).strip()
        x = re.sub("[。]+", "。", x)
        x = re.sub("[，]+", "，", x)
        x = re.sub("[？]+", "？", x)
        x = re.sub("[；]+", "；", x)
        x = re.sub("[！]+", "！", x)
        x = re.sub("[;]+", ";", x)
        x = re.sub("[,]+", ",", x)
        x = re.sub("[\.]+", ".", x)
        x = re.sub("[\?]+", "?", x)
        x = re.sub("[!]+", "!", x)
        return x

    def _truncate_seq_pair(self, tokens_a, tokens_b, max_length):
        """Truncates a sequence pair in place to the maximum length."""
        while True:
            total_length = len(tokens_a) + len(tokens_b)
            if total_length <= max_length:
                break
            if len(tokens_a) > len(tokens_b):
                tokens_a.pop()
            else:
                tokens_b.pop()

    def _convert_single_sentence(self, tokens_a, tokens_b, max_seq_length=50):
        '''
            convert a sentence to a numpy array
            text_a: CLS [seq] SEP
        '''
        # tokens_a = self.tokenizer.tokenize(tokens_a)
        tokens_a = re.split("\s+", re.sub("", " ", tokens_a).strip())
        # tokens_b = None
        if tokens_b is not None:
            # tokens_b = self.tokenizer.tokenize(tokens_b)
            tokens_b = re.split("\s+", re.sub("", " ", tokens_b).strip())
            self._truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            # Account for [CLS] and [SEP] with "- 2"
            if len(tokens_a) > max_seq_length - 2:
                tokens_a = tokens_a[0:(max_seq_length - 2)]
        tokens = []
        segment_ids = []
        tokens.append("[CLS]")
        segment_ids.append(0)
        for token in tokens_a:
            tokens.append(token)
            segment_ids.append(0)
        tokens.append("[SEP]")
        segment_ids.append(0)

        if tokens_b:
            for token in tokens_b:
                tokens.append(token)
                segment_ids.append(1)
            tokens.append("[SEP]")
            segment_ids.append(1)

        # input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        input_ids = self.sentence2wordId(tokens)
        input_mask = [1] * len(input_ids)
        while len(input_ids) < max_seq_length:
            input_ids.append(0)
            input_mask.append(0)
            segment_ids.append(0)
        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length

        return [input_ids], [input_mask], [segment_ids]

    def predict(self, text1, text2, threshold):
        """
        Function to run the inference
        """
        text1 = self.apply_function_to_str(str(text1).strip())
        text2 = self.apply_function_to_str(str(text2).strip())
        if text1=="" or text2=="":
            return 0,0,0
        elif len(text1) * 1.0 / len(text2) < 0.5 or len(text2) * 1.0 / len(text1) < 0.5:
            return 0, 0, 0
        else:
            input_ids, input_mask, segment_ids = self._convert_single_sentence(tokens_a=text1,tokens_b=text2,
                                    max_seq_length=self.max_seq_length)
            feed_dict = {self.input_ids: input_ids, self.input_mask: input_mask,
                         self.segment_ids: segment_ids}
            probability = self.sess.run(self.probabilities, feed_dict)
            max_pro = max(probability[0])
            predict_index = list(probability[0]).index(max_pro)
            predict_label = self.label_list[predict_index]
            if max_pro>=threshold:
                return max_pro,predict_index,predict_label
            else:
                return max_pro,0,0


if __name__ == "__main__":

    text1 = "大小"
    text2 = "小"
    textSimilarityModel = TextSimilarity_Model()
    for i in range(0,1):
        probability, predict_index, predict_labels = textSimilarityModel.predict(
            text1=text1, text2=text2, threshold=0.5)
        print(probability)
        print(predict_index)
        print(predict_labels)
        print("-"*80)


    text1 = "浮渣较少的是软水，浮渣较多的是硬水"
    text2 = "浮渣较多的为硬水，浮渣较少的为软水"
    probability, predict_index, predict_labels = textSimilarityModel.predict(
        text1=text1, text2=text2, threshold=0.5)
    print(probability)
    print(predict_index)
    print(predict_labels)
    print("-" * 80)




