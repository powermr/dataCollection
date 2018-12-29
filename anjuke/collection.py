#_*_coding:utf-8_*_
import math
import time
import urllib.request as urllib2
from bs4 import BeautifulSoup

import pymysql

def url_request(u,h):
    req=urllib2.Request(u,headers=h)
    # print(req.headers,req.type,req.data)
    res=urllib2.urlopen(req)
    html=res.read().decode('UTF8',errors='ignore')
    return html

def create_table():
    db=pymysql.connect("192.168.217.132","root","root","anjuke")
    cursor=db.cursor()
    cursor.execute('''
    CREATE TABLE `wf_new_loupan` (  
     `id` int(11) NOT NULL AUTO_INCREMENT, 
     `lp_name` varchar(20) DEFAULT NULL,  
     `lp_address` varchar(255) DEFAULT NULL,
     `huxing` varchar(255) DEFAULT NULL,
     `tags_wrap` varchar(255) DEFAULT NULL,
     `price` varchar(255) DEFAULT NULL,
     `details_url` varchar(50) DEFAULT NULL,
     `collection_date` date DEFAULT NULL,
   PRIMARY KEY (`id`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8 ''')
    db.close()

def get_newloupandata():
    try:
        db=pymysql.connect("192.168.217.132","root","root","anjuke",charset="utf8")
    except  ConnectionError as e:
        print("mysql connect error:"+e)
        exit(1)
    cursor=db.cursor()
    date_now=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    url="https://wf.fang.anjuke.com/loupan/all/"
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
    referer="https://weifang.anjuke.com/"
    header={"User-Agent":user_agent,"Referer":referer}

    html=url_request(url,header)
    bsObj=BeautifulSoup(html,"lxml")

    total=bsObj.find("span",{"class","total"}).em.text
    pages=math.ceil(int(total)/30)
    try:
        for i in range(1,pages+1):
            print(i)
            request_url=url+"p"+str(i)+"/"
            print("开始采集："+request_url)
            html=url_request(request_url,header)

            bsObj=BeautifulSoup(html,"lxml")
            div_key_list=bsObj.find("div",{"class","key-list"})
            items=div_key_list.findAll("div",{"class","item-mod"})
            print(len(items))

            for item in items:

                try:
                    # lp_name 楼盘名
                    lp_name=item.div.h3.text
                    # 详情链接
                    details_url=item.div.a.get("href")
                    # 地址
                    lp_address=item.find("a",{"class","address"}).text.replace('\n','')
                    # 户型 建筑面积
                    huxing=item.find("a",{"class","huxing"}).text.strip().replace('\n','').replace('\t','')
                    huxing=' '.join(huxing.split())
                    # 说明标签
                    tags_wrap=item.find("a",{"class","tags-wrap"}).text.replace('\n','|')
                    # 价格
                    price=item.find("a",{"class","favor-pos"}).text.replace('\n','')
                except AttributeError as err:
                    print(err)
                sql='''
                insert into wf_new_loupan(
                lp_name,lp_address,huxing,tags_wrap,price,details_url,collection_date
                )values(
                '%s','%s','%s','%s','%s','%s','%s'
                )
                '''%(lp_name,lp_address,huxing,tags_wrap,price,details_url,date_now)
                print(sql)
                cursor.execute(sql)
                print("="*16)
            time.sleep(5)
        db.commit()
    except:
        db.rollback()

    db.close()

def get_saleloupandata():
    try:
        db=pymysql.connect("192.168.217.132","root","root","anjuke",charset="utf8")
    except ConnectionError as  e:
        print("mysql connect error:"+e)
        exit(1)
    cursor=db.cursor()
    date_now=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    url="https://weifang.anjuke.com/sale/"
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
    referer="https://weifang.anjuke.com/"
    header={"User-Agent":user_agent,"Referer":referer}

    page=1

    try:
        while True:
            request_url=url+"p"+str(page)+"/"
            html=url_request(request_url,header)
            bsObj=BeautifulSoup(html,"lxml")
            li_houselist=bsObj.find("ul",{"id","houselist-mod-new"})
            items=li_houselist.findAll("li",{"class","list-item"})
            print(len(items))

            for item in items:
                try:
                    house_t=item.find("div",{"class","house-title"}).text.replace('\n','').split('安选')
                    house_title=house_t[0]
                    try:
                        anxuan=house_t[1].strip()
                    except IndexError:
                        anxuan=''

                    details_url=item.a.get("href")
                    div_details=item.findAll("div",{"class","details-item"})

                    house_details=div_details[0].text.replace('\n','').split('|')
                    # 户型
                    huxing=house_details[0]
                    # 面积
                    proportion=house_details[1]
                    # 所属楼层
                    floor=house_details[2]
                    # 房子建造年份
                    build_date=house_details[3].split('年建造')[0]
                    # 卖方
                    seller=house_details[3].split('年建造')[1][1:]

                    house_address=div_details[1].text.replace('\n','').strip()

                    house_tags=item.find("div",{"class","tags-bottom"}).text.replace('\n','')

                    price=item.find("div",{"class","pro-price"}).text.replace('\n','').split('万')
                    total_price=price[0]
                    unit_price=price[1]

                except AttributeError as e:
                    print(e)

                sql='''
                    insert into wf_sale_house(
                        house_title,anxuan,huxing,proportion,floor,build_date,seller,house_address,house_tags,total_price,unit_price,details_url,collection_date
                    )value(
                        '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'
                    )            
                '''%(house_title,anxuan,huxing,proportion,floor,build_date,seller,house_address,house_tags,total_price,unit_price,details_url,date_now)

                print(sql)
                cursor.execute(sql)
            try:
                bsObj.find("a",{"class","aNxt"}).text
                page=page+1
            except AttributeError:
                print("没有下一页了")
                break

        db.commit()
        print("二手房数据采集完成")
    except pymysql.err.InternalError as e:
        print("error: "+e)
        db.rollback()
    finally:
        db.close()



if __name__ == '__main__':
    # create_table()
    get_newloupandata()
    get_saleloupandata()



