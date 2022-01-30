import sys; sys.path.append("D:\\vscode py\\现代程设\\week 3")
import emotionv2
import jieba
import matplotlib.pyplot as plt

class Tokenizer:
    '''
    按照预先定义好的词典，把文本编码成整数序列;
    为使句子长度整齐，规定特殊号码[PAD]=0，代表填充位。
    '''
    def __init__(self, chars, coding="c", PAD=0):
        '''
        构建词典，即构建汉字到正整数的唯一映射
        '''
        self.chars = chars
        self.coding = coding
        dic = {"[PAD]": 0}
        if coding == "c":
            i = 1
            for char in chars:
                c_list = jieba.lcut(char)
                # 将中文单词分解为单字，英文不变
                for c in c_list:
                    if 97 <= ord(c[0]) <= 122 or 65 <= ord(c[0]) <= 90:
                        # 英文情况
                        if c not in dic: dic[c] = i; i += 1
                    else:
                        # 中文、标点符号等情况
                        for c_chi in c:
                            if c_chi not in dic: dic[c_chi] = i; i += 1
            self.dic = dic
        if coding == "w":
            i = 1
            for char in chars:
                char_list = jieba.lcut(char)
                for c in char_list:
                    if c in dic: continue
                    else: dic[c] = i; i += 1
            self.dic = dic

    def tokenize(self, sentence):
        '''
        输入一句话，返回分词（字）后的字符列表(list_of_chars)
        '''
        list_of_chars = []
        if self.coding == "c":
            c_list = jieba.lcut(sentence)
            for c in c_list:
                if 97 <= ord(c[0]) <= 122 or 65 <= ord(c[0]) <= 90:
                    # 英文情况
                    list_of_chars.append(c)
                else:
                    # 中文、标点符号等情况
                    for c_chi in c:
                        list_of_chars.append(c_chi)
            return list_of_chars
        if self.coding == "w":
            c_list = jieba.lcut(sentence)
            for c in c_list:
                list_of_chars.append(c)
            return list_of_chars

    def encode(self, list_of_chars):
        '''
        输入字符（字或者词）的字符列表，返回转换后的数字列表(tokens)
        '''
        tokens = []
        for char in list_of_chars:
            tokens.append(self.dic[char])
        return tokens

    def trim(self, tokens, seq_len):
        '''
        输入数字列表tokens，整理数字列表的长度；
        不足seq_len的部分用PAD补足，超过的部分截断。
        '''
        n = len(tokens)
        if n <= seq_len:
            # 需要补足
            trimmed_tokens = tokens + ["PAD"] * (seq_len - n)
        else:
            # 需要截断
            trimmed_tokens = tokens[:seq_len]
        return trimmed_tokens

    def decode(self, tokens):
        '''
        将模型输出的数字列表翻译回句子
        '''
        sentence = ""
        dic_inv = {value: key for key, value in self.dic.items()}
        for num in tokens:
            if num == "PAD": sentence += "[PAD]"; continue
            sentence += dic_inv[num]
        return sentence

    def tokens_equal_to_seq_len(self, seq_len):
        '''
        返回所有文本(chars)的长度为seq_len的tokens
        '''
        tokens_list = []
        for char in self.chars:
            list_of_chars = self.tokenize(char)
            if len(list_of_chars) == seq_len:
                tokens = self.encode(list_of_chars)
                tokens_list.append(tokens)
        return tokens_list

    def seq_len_distribution(self, isplot=False):
        '''
        返回所有文本(chars)的最大长度频数，并绘制长度频度分布图
        '''
        dis = [0] * 125
        for char in self.chars:
            length = len(self.tokenize(char))
            if "分享图片" in char and length == 2: continue
            dis[length] += 1
        max_seq_len = dis.index(max(dis))
        if isplot == True:
            x = [i for i in range(125)]
            plt.bar(x, dis)
            plt.xlabel("seq_len"); plt.ylabel("frequency")
            plt.title("Seq_len Distribution")
            plt.savefig("seq_len_distribution3", dpi=800)
            plt.show()
            return max_seq_len
        else:
            return max_seq_len

def main():
    comms_list = emotionv2.get_comms_list()
    t = Tokenizer(comms_list, coding="w")
    list_of_chars = t.tokenize(comms_list[1]) # ; print(list_of_chars)
    tokens = t.encode(list_of_chars) # ; print(tokens)
    trimmed_tokens = t.trim(tokens, 20) # ; print(trimmed_tokens)
    sen = t.decode(trimmed_tokens) # ; print(sen)
    tokens_list = t.tokens_equal_to_seq_len(20)
    max_seq_len = t.seq_len_distribution(isplot=True) ; print(max_seq_len)
    # for i in range(10):
    #     print(tokens_list[i])

if __name__ == '__main__':
    main()