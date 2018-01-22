import time
import collections

from bs4 import BeautifulSoup
import requests

header={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36','authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}
file_path='E:/programming/MyCode/atom/python/爬虫/www.zhihu.com_知乎/'

#获取无忧代理IP
def getProxy():
    #调用api接口
    order="d755aba97d69316126889d1c75fc79fb"
    apiUrl= "http://api.ip.data5u.com/dynamic/get.html?order=" + order+'&ttl=1&sep=3'
    result=requests.get(apiUrl).text.split(',')
    print(result)
    ip=result[0]
    time_limit=result[1]
    return {'http':'http://'+ip}

def getSoup(url):
    # proxies=getProxy()
    web=requests.get(url,headers=header)
    # web=requests.get(url,headers=header,proxies=proxies)
    web.encoding=web.apparent_encoding
    if web.status_code==200:
        soup=BeautifulSoup(web.text,'html5lib')
        return soup
    else:
        print(web.status_code)
        print("获取"+url+"失败")

def getFormatedTime(timestr):
    #转换时间格式
    local_time=time.strptime(timestr,'%Y-%m-%dT%H:%M:%S.000Z')
    answer_time=time.strftime('%Y-%m-%d %H:%M:%S',local_time)
    return answer_time

def getStringValue(string):
    #将带,的字符串转换成数字
    value_str=''
    if string.endswith("收藏"):
        value_str=string[:-4]
        str_list=value_str.split(',')
        value=0
        for i in range(len(str_list)):
            value+=int(str_list[i])*1000**(len(str_list)-i-1)
        return value
    elif string.endswith("感谢"):
        return 0
    else:
        value_str=string
        str_list=value_str.split(',')
        value=0
        for i in range(len(str_list)):
            value+=int(str_list[i])*1000**(len(str_list)-i-1)
        return value

def getListString(lis):
    #将列表拼接成字符串
    result=''
    for item in lis:
        result+=str(item)+','
    return result[:-1]

def getSiblAttrAt(tag,attr,offset):
    #获取兄弟节点属性
    return tag.parent.contents[offset].attrs[attr]

def getAnswerAmount(soup):
    #获取页面中答案的数量
    return len(soup.select("div.List-item"))

def getPageAmount(user_id):
    #获取用户界面页面数
    user_url='https://www.zhihu.com/people/'+user_id+'/answers'
    user_web=requests.get(user_url,headers=header)
    user_web.encoding=user_web.apparent_encoding
    if user_web.status_code==200:
        soup=BeautifulSoup(user_web.text,'html5lib')
        pagination=soup.select("button.PaginationButton")
        if len(pagination)>1:
            return int(pagination[-2].contents[1])
        elif len(pagination)==1:
            return 1
        else:
            if len(soup.select("div.List-item"))>0:
                return 0
            else:
                return "failed"
    else:
        return "failed"

def isQuestionConnectable(soup):
    try:
        test=soup.select("div[data-zop-question]")[0]
        return True
    except IndexError:
        return False

def getAnswerInfo(soup,offset):
    #获取单个回答的信息
    answer_item=soup.select("div[data-zop]")[offset]
    answer_id=int(answer_item.attrs['name'])
    meta_list=answer_item.select("meta")

    upvote_count=int(meta_list[-5].attrs['content'])
    question_id_temp=meta_list[-4].attrs['content']
    question_id=int(question_id_temp[question_id_temp.index("/question")+10:question_id_temp.index("/answer/")])
    answer_time_temp=meta_list[-3].attrs['content']
    answer_time=getFormatedTime(answer_time_temp)
    comment_count=meta_list[-1].attrs['content']

    if answer_item.span.a is not None:
        user_id_temp=answer_item.span.a.attrs['href']
        try:
            user_id=user_id_temp[user_id_temp.index("/people")+8:]
        except ValueError:
            user_id=user_id_temp
    else:
        user_id='anonymous_user'

    return {'answer_id':answer_id,'question_id':question_id,'user_id':user_id,'upvote_count':upvote_count,
    'comment_count':comment_count,'answer_time':answer_time}

def getUserInfo(soup,user_id):
    user_name=str(soup.h1.span.string)
    user_info=soup.select("div[itemprop=people]")[0]
    voteup_count=getSiblAttrAt(user_info.meta,'content',3)
    thank_count=getSiblAttrAt(user_info.meta,'content',4)
    follower_count=getSiblAttrAt(user_info.meta,'content',5)
    answer_count=getSiblAttrAt(user_info.meta,'content',6)
    article_count=getSiblAttrAt(user_info.meta,'content',7)

    tabs_meta=user_info.select("span.Tabs-meta")
    ask_count=int(tabs_meta[1].string)
    section_count=int(tabs_meta[3].string)
    thought_count=int(tabs_meta[4].string)

    collect_count_temp=soup.select("div.Profile-sideColumnItemValue")
    if len(collect_count_temp)>3:
        collect_count=getStringValue(collect_count_temp[-1].contents[7])
    elif len(collect_count_temp)==0:
        collect_count=0
    else:
        collect_count=getStringValue(collect_count_temp[-1].contents[1])

    common_edit_count=0
    try:
        edit_count_temp=soup.select("a.Profile-sideColumnItemLink")[-1].contents[4]
        common_edit_count=getStringValue(edit_count_temp)
    except IndexError:
        pass

    return {'user_id':user_id,'user_name':user_name,'voteup_count':voteup_count,'thank_count':thank_count,'collect_count':collect_count,
    'common_edit_count':common_edit_count,'follower_count':follower_count,'answer_count':answer_count,
    'ask_count':ask_count,'article_count':article_count,'section_count':section_count,'thought_count':thought_count}

def getQuestionInfo(soup,question_id):
    answer_info=soup.select("div[data-zop-question]")[0]
    data=answer_info.attrs['data-zop-question']
    dic=eval(data.replace('false',"'false'"))

    header_side=answer_info.select("div.QuestionHeader-side")[0]
    follower_count=header_side.select("strong")[0].attrs['title']
    visit_count=header_side.select("strong")[1].attrs['title']

    question_title=dic['title']
    topic_id_list=[]
    for i in range(len(dic['topics'])):
        topic_id_list.append(dic['topics'][i]['id'])
    topic_id_list=getListString(topic_id_list)

    answer_count=getSiblAttrAt(answer_info,'content',4)
    question_comment_count=getSiblAttrAt(answer_info,'content',5)
    create_time_temp=getSiblAttrAt(answer_info,'content',6)
    create_time=getFormatedTime(create_time_temp)
    return {'question_id':question_id,'topic_id_list':topic_id_list,'question_title':question_title,'question_comment_count':question_comment_count,
    'follower_count':follower_count,'visit_count':visit_count,'create_time':create_time,'answer_count':answer_count}

# def getTopicInfo(soup,topic_id):

def getCompleteList(info_type):
    #获取已经完成爬虫的用户列表
    complete_user_list=[]
    with open(file_path+info_type+'_mark.txt','r',encoding='utf8') as f:
        list_temp=f.readlines()
        for user in list_temp:
            complete_user_list.append(user.rstrip('\n'))
    return complete_user_list

def writeCompleteId(id,info_type):
    with open(file_path+info_type+'_mark.txt','a',encoding='utf8') as f:
        f.write(str(id)+'\n')
