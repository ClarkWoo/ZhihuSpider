import random
import time
import win_unicode_console

import requests
from bs4 import BeautifulSoup

import common
import mysqloperation

win_unicode_console.enable()

#连接数据库并获取用户列表
conn=mysqloperation.getMysqlConnect()
sql='select question_id from answer group by question_id'
question_id_list=mysqloperation.getSelectData(conn,sql)
question_length=len(question_id_list)

for i in range(len(question_id_list)):
    question_id=question_id_list[i]
    if question_id not in common.getCompleteList('question'):
        print("正在抓取第"+str(i)+"/"+str(len(question_id_list))+"个问题:"+question_id)
        for page_type in ['','/answers/created']:
            question_url='https://www.zhihu.com/question/'+question_id+page_type
            soup=common.getSoup(question_url)
            if soup is not None and common.isQuestionConnectable(soup):
            #获取问题信息
                question_info=common.getQuestionInfo(soup,question_id)

                #将问题信息写入question表
                mysqloperation.insertZhihu(conn,'question',question_info)

                #获取每个答案信息并写入answer表
                for i in range(common.getAnswerAmount(soup)):
                    answer_info=common.getAnswerInfo(soup,i)
                    mysqloperation.insertZhihu(conn,'answer',answer_info)

            # #暂停3到5秒
            # time.sleep(2*random.random()+3)
        #将问题id写入question_mark.txt
        common.writeCompleteId(question_id,'question')
    else:
        print("问题"+question_id+"已经爬取")

conn.close()
