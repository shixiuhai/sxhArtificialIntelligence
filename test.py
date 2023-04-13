#!/usr/bin/python
# -*- coding: utf-8 -*-
 
"""
 补0方式(ECB加密)
"""
 
import base64
 
from Crypto.Cipher import AES

dataList="eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6Znp4IiwiZGF0YSI6ImVhZ2h6akFFRllHZVV4aDBQMkZnUEVIN2lybTFwRy9GWGNkeE1BbGpqZ3pROFFlWFZLVCthMk5mNm44U1Zuejhvam9vek4ydDd4RmlIeVFxaGlHNjZPN1BIR2owNE9pS0t2RURhVGJFMTZGMFpPVCtYNzR4RWJNdHNHbjVyKzlZYUNGK1BXdHNyMFl1Zy92U29KQmlhbExjaHQxaGY2Q1ZIbzRUQy81K0ZlMVFqRThCM2gvWmE3V2RvUmRoSnVGYVNuc3hxaEFqdEVCdnB5NmhOcGptd1NTQzBKQnQvNVBrTGpuK1A5RDhhVjArbWEyOXoxZ2dyZFVjL2syRTUwQ0cyRFNaU29FN0RHVVRKUWV6S2ZlWWZPTWVOcEhBVktLZy96WVhBS05YNW9KUm5lTldyNDdubHo1Nnp4WTBQWE5tUEhLSHdhQlBHc3g2eGpES056Qm5EbitoMVNZRmMzWFg4ampreGhGT3NDVFlvd24vZC9NelJTUDBOUnp0N2tqc2lpT0dxN1FxWDNXM3BFTmoxUEpDMExoWnJsTGZaRGhteXF2QTFuYUg5YmVCL2d3NC9UczhlMi9vUmhzTjdrSHl2MnpreDFseEQwMDk3SDc3Y3pVcFZpNlpEeXp1Zlh3dkxkS3FpSUhBMk9veHRrQm5wZmR1VDYyZUtNT0RkTkwyQlN5RmxDbUx6eDlYcEd1VnErRU5TMWwrZ3ZoSTZneFYyYTNMMDA0WGFHeG1YSmpnaVV1NEMyeExkTXgranVPUkQ5YjRzd2hydE45bG5tSjlYOUtRamc9PSIsIm5iZiI6MTY4MTIwMjU3MywiZXhwIjoxNjgxMjA2MTczLCJpc3MiOiJ6andoc2MiLCJhdWQiOiJhcGkifQ.dNEDdLj8I7HwTRcoE4AvIWkHow5wblzqAFcLfvtE3qINsnabAC50vwB09CC8P_UCEzhLiRmntF7fonpo01F1NrgxKDM-xNkps8JOq8wG3dqcGHzacootrCQb6h7y3DDpr9WHuw1UAZRWb1KcHXXMpV3A6-kKoXekGbfPgaERFptbogAItusE77tsWzSrRr9_ra3pBrWzUWIglTaTyItc-aya3qOwe6CTPhjld_V4weEYmgcJW2Ibq94_9MHqRktq3PSoZ_moStt-HgB15UGXM1-u3GpNq8lerX3is-HPD8oOK5S5ZOQQQVAtFCejXjet1g7c6epDpXpWfTQy1ADXKA".split(".")
 
# 补足字符串长度为16的倍数
def add_to_16(s):
    while len(s) % 16 != 0:
        s += '\0'
    return str.encode(s)  # 返回bytes
 
 
key = 'LVG3P6P6mJxedPWTwl2TrmhIBWtYK4yY'  # 密钥长度必须为16、24或32位，分别对应AES-128、AES-192和AES-256
text = 'abcdefg'  # 待加密文本
 
aes = AES.new(str.encode(key), AES.MODE_ECB)  # 初始化加密器，本例采用ECB加密模式
# encrypted_text = str(base64.encodebytes(aes.encrypt(add_to_16(text))), encoding='utf8').replace('\n', '')  # 加密
#decrypted_text = str(aes.decrypt(base64.decodebytes(bytes(encrypted_text, encoding='utf8'))).rstrip(b'\0').decode("utf8"))  # 解密
print(dataList)
# print('加密值：', encrypted_text)
decrypted_text = str(aes.decrypt(base64.decodebytes(bytes('eaghzjAEFYGeUxh0P2FgPEH7irm1pG/FXcdxMAljjgzQ8QeXVKT+a2Nf6n8SVnz8ojoozN2t7xFiHyQqhiG66O7PHGj04OiKKvEDaTbE16F0ZOT+X74xEbMtsGn5r+9YaCF+PWtsr0Yug/vSoJBialLcht1hf6CVHo4TC/5+Fe1QjE8B3h/Za7WdoRdhJuFaSnsxqhAjtEBvpy6hNpjmwSSC0JBt/5PkLjn+P9D8aV0+ma29z1ggrdUc/k2E50CG2DSZSoE7DGUTJQezKfeYfOMeNpHAVKKg/zYXAKNX5oJRneNWr47nlz56zxY0PXNmPHKHwaBPGsx6xjDKNzBnDn+h1SYFc3XX8jjkxhFOsCTYown/d/MzRSP0NRzt7kjsiiOGq7QqX3W3pENj1PJC0LhZrlLfZDhmyqvA1naH9beB/gw4/Ts8e2/oRhsN7kHyv2zkx1lxD0097H77czUpVi6ZDyzufXwvLdKqiIHA2OoxtkBnpfduT62eKMODdNL2BSyFlCmLzx9XpGuVq+ENS1l+gvhI6gxV2a3L004XaGxmXJjgiUu4C2xLdMx+juORD9b4swhrtN9lnmJ9X9KQjg=="', encoding='utf8'))).rstrip(b'\0').decode("utf8"))  # 解密

print('解密值：', decrypted_text)