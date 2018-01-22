import requests

import common

user_id='cbb0813'
user_url='https://www.zhihu.com/people/'+user_id

soup=common.getSoup(user_url)
# user_info=common.getUserInfo(soup,user_id)

print(common.getPageAmount(user_id))
