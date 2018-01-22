import random
import time
import win_unicode_console

import requests
from bs4 import BeautifulSoup

import common
import mysqloperation

win_unicode_console.enable()

page_mark=0

#连接数据库并获取用户列表
conn=mysqloperation.getMysqlConnect()
sql='select user_id from answer group by user_id'
user_id_list=mysqloperation.getSelectData(conn,sql)
user_id_list.append('chu-yin-wei-lai-59')

user_length=len(user_id_list)
#获取列表中用户网页信息
for i in range(user_length):
    user_id=user_id_list[i]
    #判断是否已经爬取
    if user_id not in common.getCompleteList('user'):
        for page_type in ['','/by_votes']:
            #测试用户界面是否可以爬取
            if common.getPageAmount(user_id) !="failed":
                page_count=common.getPageAmount(user_id)
                if type(page_count)==int:
                    for i in range(page_mark,page_count):
                        user_url='https://www.zhihu.com/people/'+user_id+'/answers'+page_type+'?page='+str(i+1)
                        print("正在抓取用户"+user_id+"第"+str(i+1)+"/"+str(page_count)+"页")
                        soup=common.getSoup(user_url)
                        if soup is not None:
                            if i<1:
                                #获取作者信息
                                user_info=common.getUserInfo(soup,user_id)
                                #将作者信息写入user表
                                mysqloperation.insertZhihu(conn,'user',user_info)

                            #获取每个答案信息并写入answer表
                            for i in range(common.getAnswerAmount(soup)):
                                answer_info=common.getAnswerInfo(soup,i)
                                mysqloperation.insertZhihu(conn,'answer',answer_info)
                            #暂停5到7秒
                            # time.sleep(2*random.random()+5)
            else:
                print("用户设置了隐私保护或用户不存在")
        #将用户id写入user_mark
        common.writeCompleteId(user_id,'user')
    else:
        print("用户"+user_id+"已经爬取")

conn.close()
