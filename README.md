# SDS_in_Sina
六度分离理论在微博的运用

# 介绍
六度分离理论（Six Degrees of Separation）：“你和任何一个陌生人之间所间隔的人不会超过五个，也就是说，最多通过五个人你就能够认识任何一个陌生人。”根据这个理论，你和世界上的任何一个人之间只隔着五个人，不管对方在哪个国家，属哪类人种，是哪种肤色。 [百度百科](https://baike.baidu.com/item/%E5%85%AD%E5%BA%A6%E5%88%86%E7%A6%BB%E7%90%86%E8%AE%BA/7485118?fr=aladdin)

本脚本会爬取微博用户的关注与粉丝列表，并储存到数据库。当爬取完一个用户所有的粉丝和关注后，会对下一个未执行的用户执行相同的步骤。在执行脚本后登录，并输入起始微博ID和目标微博ID，程序将开始运行。 直到找到目标ID后结束，并输出起始ID与目标ID之间的关系.