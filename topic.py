import collections

import requests
from bs4 import BeautifulSoup

import mysqloperation
import common

#连接数据库
conn=mysqloperation.getMysqlConnect()

#获取信息
topic_id_list=[19776749]
topic_id=topic_id_list[0]
header={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'}
topic_url='https://www.zhihu.com/topic/'+str(topic_id)+'/top-answers'
topic_web=requests.get(topic_url,headers=header)
topic_web.encoding=topic_web.apparent_encoding
if(topic_web.status_code==200):
    soup=BeautifulSoup(topic_web.text,'html5lib')
    #获取话题信息
    topic_name=str(soup.h1.string)
    topic_follow_count=int(soup.select("strong")[0].attrs['title'])
    topic_answer_count=int(soup.select("strong")[1].attrs['title'])

    #将话题信息写入topic表
    topic_dic=collections.OrderedDict()
    topic_dic['topic_id']=topic_id
    topic_dic['topic_name']=topic_name
    topic_dic['topic_follow_count']=topic_follow_count
    topic_dic['topic_answer_count']=topic_answer_count
    mysqloperation.insertZhihu(conn,'topic',topic_dic)

    #获取每个回答信息
    current_answer=soup.select("div.List-item")
    for i in range(len(current_answer)):
        answer_item=soup.select("div[data-zop]")[i]
        answer_info=answer_item.attrs['data-zop']
        meta_list=answer_item.select('meta')
        dic=eval(answer_info)

        answer_id=int(dic['itemId'])
        question_id_temp=meta_list[0].attrs['content']
        question_id=int(question_id_temp[question_id_temp.index("/question")+10:])

        #处理匿名用户
        if answer_item.span.a is not None:
            user_id_temp=answer_item.span.a.attrs['href']
            user_id=user_id_temp[user_id_temp.index("/people")+8:]
        else:
            user_id='anonymous_user'

        upvote_count=int(meta_list[7].attrs['content'])
        comment_count=meta_list[11].attrs['content']

        #转换时间格式
        answer_time_temp=meta_list[9].attrs['content']
        answer_time=common.getFormatedTime(answer_time_temp)

        #将答案信息写入answer表
        answer_dic=collections.OrderedDict()
        answer_dic['answer_id']=answer_id
        answer_dic['question_id']=question_id
        answer_dic['user_id']=user_id
        answer_dic['upvote_count']=upvote_count
        answer_dic['comment_count']=comment_count
        answer_dic['answer_time']=answer_time
        mysqloperation.insertZhihu(conn,'answer',answer_dic)
else:
    print("failed")

conn.close()
