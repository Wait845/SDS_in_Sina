import datetime
from os import pardir
from time import sleep
import requests
import forum_sql as sql
import time
import re
import sys
import os


def login():
    current_timestamp = str(int(time.time()))
    # 该url返回登录二维码的ID以及二维码的URL
    url_get_info = "https://login.sina.com.cn/sso/qrcode/image?entry=weibo&size=180&callback=STK_{}".format(current_timestamp)

    info = session.get(url_get_info)
    if info.status_code != 200:
        pass
    info = info.text
    # 找到包含信息的字典
    info = re.findall(r'\((.*)\)', info)[0].replace('true', 'True').replace('false', 'False').replace('null', 'None').replace('none', 'None')
    info = eval(info)
    if info.get('retcode') != 20000000:
        pass

    # 取出二维码ID和二维码URL
    qrid = info.get('data').get('qrid')
    url_image = "https://v2.qr.weibo.cn/inf/" + info.get('data').get('image')[22:]
    # 把二维码写到文件供用户打开扫描
    with open(working_path + '/login_pic.png', 'wb') as file:
        file.write(session.get(url_image).content)
    print("请打开并用新浪微博客户端扫描当前目录下的'logjn_pic.png'")
    

    # 循环检测用户是否登录直到登录成功
    retcode = 0
    while True:
        url_check_login = "https://login.sina.com.cn/sso/qrcode/check?entry=weibo&qrid={}&callback=STK_{}".format(qrid, current_timestamp)
        result_check_login = session.get(url_check_login)
        if result_check_login.status_code != 200:
            pass
        result_check_login = result_check_login.text
        result_check_login = re.findall(r'\((.*)\)', result_check_login)[0].replace('true', 'True').replace('false', 'False').replace('null', 'None').replace('none', 'None')
        result_check_login = eval(result_check_login)
        current_retcode = result_check_login.get('retcode')
        current_msg = result_check_login.get('msg')
        if current_retcode != retcode:
            retcode = current_retcode
            print(current_msg)
        if current_retcode == 20000000:
            current_data_alt = eval(str(result_check_login.get('data'))).get('alt')
            break
        sleep(2)
    
    # if os.path.exists(working_path + '/login_pic.png'):
    #     os.remove(working_path + '/login_pic.png')

    url_login = "https://login.sina.com.cn/sso/login.php?entry=weibo&returntype=TEXT&crossdomain=1&cdult=3&domain=weibo.com&alt={}&savestate=30&callback=STK_160362937349611".format(current_data_alt)
    private = session.get(url_login).text
    private = re.findall(r'\((.*)\)', private)[0].replace('true', 'True').replace('false', 'False').replace('null', 'None').replace('none', 'None')
    private = eval(private)
    private_nickname = private.get('nick')
    private_uid = private.get('uid')

    # 这一步需要把url跑一遍拿cookie，否则登录会不成功
    urls_for_login = eval(str(private.get('crossDomainUrlList')))
    for url in urls_for_login:
        url = url.replace('\\', '')
        # 因为遇到了https,所以在此关闭了ssl验证,会报错
        session.get(url, verify=False)

    print("已登录账号:", private_uid, " 用户名:", private_nickname)


    # sleep(5)
    # 测试能否拿到数据
    # print(session.get('https://weibo.com/ajax/friendships/friends?relate=fans&page=1&uid={id}').text)


def found_user(master_id, target_id):
    relation_list = []
    while target_id != master_id:
        print("target id:", target_id, "master_id:", master_id)
        sql_find_parent = """
        SELECT s_id, s_name, d_name, relation
        FROM relation
        WHERE d_id = '{}'
        """.format(target_id)
        fb_find_parent = db.execute(sql_find_parent)[0]
        parent_id, parent_name, current_name, relation = fb_find_parent
        relation_word = "粉丝" if relation == 0 else "关注"
        temp_relation = "{}({}) 的{} 是{}({})".format(parent_name, parent_id, relation_word, current_name, target_id)
        relation_list.insert(0, temp_relation)
        target_id = parent_id
    
    for i in relation_list:
        print(i)


def add(master_id, master_name, relation):
    global keep_srarch
    found = False
    page = 1
    while True:
        print("正在搜索 {}({}) 的第{}页 =={}".format(master_name, master_id, page, relation))
        # fans
        if relation == 0:
            url_get_user = "https://weibo.com/ajax/friendships/friends?relate=fans&page={}&uid={}".format(page, master_id)
        # follow
        elif relation == 1:
            url_get_user = "https://weibo.com/ajax/friendships/friends?page={}&uid={}".format(page, master_id)
        else:
            print("未输入正确的relation")
            return

        user_result = session.get(url_get_user)
        if user_result.status_code != 200:
            pass
        
        # 因为js的boolean和python的boolean不一样，需要转换一下
        user_result_str = user_result.text.replace('true', 'True').replace('false', 'False')
        # 把文本的json转换成python的字典格式
        user_result_str = eval(user_result_str)
        # 取出包含数据的字典
        user_data = user_result_str['users']
        # 如果next_cursor为0，则不存在下一页
        user_next_cursor = user_result_str['next_cursor']

        # 把fans里的每一个用户都添加到user和relation表中
        for user in user_data:
            user_id = user.get('idstr')
            user_name = user.get('name')
            user_location = user.get('location')
            user_gender = user.get('gender')
            user_followers_count = user.get('followers_count')
            user_friends_count = user.get('friends_count')
            user_created_at = datetime.datetime.strftime(datetime.datetime.strptime(user.get('created_at'), "%a %b %d %H:%M:%S %z %Y"), "%Y-%m-%d %H:%M:%S")
            
            sql_write_user = """
            INSERT INTO user (id, name, location, gender, follower_count, friends_count, create_at, push_time) 
            VALUES ('{}', '{}', '{}', '{}', {}, {}, '{}', '{}')
            """.format(user_id, user_name, user_location, user_gender, user_followers_count, user_friends_count, user_created_at, str(int(time.time())))

            sql_write_relation = """
            INSERT INTO relation (s_id, s_name, d_id, d_name, relation) 
            VALUES ('{}', '{}', '{}', '{}', {})
            """.format(master_id, master_name, user_id, user_name, relation)

            db.execute(sql_write_user)
            db.execute(sql_write_relation)

            if user_id == target_id:
                found = True

        if found:
            print("已找到目标")
            keep_srarch = False
            found_user(start_id, target_id)
            break
        
        # 无更多的粉丝，断开循环并更新该用户的finish为True
        if user_next_cursor == 0:
            sql_update_user_finish = """
            UPDATE user 
            SET finish = true 
            WHERE id = '{}'
            """.format(master_id)
            db.execute(sql_update_user_finish)
            break
        else:
            page += 1


def search():
    # 在user表中找到第一个还未遍历的用户
    sql_search_first_user = """
    SELECT id, name
    FROM user
    WHERE finish = false
    ORDER BY push_time
    LIMIT 1;
    """
    fb_search_first_user = db.execute(sql_search_first_user)[0]
    master_id = fb_search_first_user[0]
    master_name = fb_search_first_user[1]
    print("开始搜索: {}({})".format(master_name, master_id))
    # 搜索粉丝
    add(master_id, master_name, 0)
    # 搜索关注
    add(master_id, master_name, 1)


if __name__ == "__main__":
    global keep_srarch
    keep_srarch = True
    working_path = os.path.dirname(__file__)
    session = requests.session()
    db = sql.database()
    login()
    start_id = input("请输入搜索开始的用户id:")
    target_id = input("请输入目标id:")
    
    # 创建初始用户
    url_get_start_user = "https://weibo.com/ajax/profile/info?uid={}".format(start_id)
    start_user = session.get(url_get_start_user)
    if start_user.status_code != 200:
        pass
    start_user = start_user.text
    start_user = eval(str(start_user).replace('null', 'None').replace('true', 'True').replace('false', 'False').replace('none', 'None')).get('data').get('user')
    start_user_name = start_user.get('name')
    start_user_location = start_user.get('location')
    start_user_gender = start_user.get('gender')
    start_user_follower_count = start_user.get('followers_count')    
    start_user_friends_count = start_user.get('friends_count')
    start_user_create_at = datetime.datetime.strftime(datetime.datetime.strptime(start_user.get('created_at'), "%a %b %d %H:%M:%S %z %Y"), "%Y-%m-%d %H:%M:%S")
    
    sql_write_user = """
    INSERT INTO user (id, name, location, gender, follower_count, friends_count, create_at, push_time) 
    VALUES ('{}', '{}', '{}', '{}', {}, {}, '{}', '{}')
     """.format(start_id, start_user_name, start_user_location, start_user_gender, start_user_follower_count, start_user_friends_count, start_user_create_at, str(int(time.time())))
    db.execute(sql_write_user)

    while keep_srarch:
        search()



    



