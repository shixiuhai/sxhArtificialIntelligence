s="M/s Rasika Exports Cell+WhatsApp: +91 99293-81771 Email: ... Delivery Terms: FOB, CNF, CIF Packing: 50kg PP Bags We look forward for Export inquires."

import re
import re
 
# 正则匹配手机号
def judge_phone_number(s:str)->list:
    patter=r""
    phone_list=re.compile(patter).findall(s)
    print(phone_list)
 
if __name__ == '__main__':
    judge_phone_number(s)