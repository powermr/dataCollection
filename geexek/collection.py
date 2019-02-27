#_*_coding:utf-8_*_
import urllib.request
import urllib.parse
import json
import codecs

def get_competition():
    for num in range(0,80):
        data={'cmptType':-1,'start':num,'searchContent':''}
        request_body=urllib.parse.urlencode(data).encode(encoding='UTF8')
        request_url='http://timerbackend.geexek.com//getCmptListForWeixin.do'
        req=urllib.request.Request(request_url)
        req.add_header('Referer','http://www.geexek.com/score')
        f=urllib.request.urlopen(req,request_body)
        json_content=f.read().decode('UTF8',errors='ignore')
        try:
            with codecs.open(r'D:\dataCollection\geexek\cmptInfo.json', 'a', encoding='utf-8') as f_cp:
                f_cp.write(json_content+',\n')
        except IOError as err:
            print('error ' + str(err))
        finally:
            f_cp.close()
        dic=json.loads(json_content)
        # print(dic)
        try:
            # {'cmptId': 342,
            # 'cmptName': '2016 ANA系列越野挑战赛之西湖五十',
            # 'cmptStartTime': '2016-05-01 07:30:00',
            for d in dic['cmptList']:
                cmptId=d['cmptId']
                cmptName=d['cmptName']
                cmptStartTime=d['cmptStartTime'].split(' ')[0]
                print('比赛id{0},比赛名称{1},比赛日期{2}'.format(cmptId,cmptName,cmptStartTime))
                cmptData={'cmptId':cmptId}
                req_body=urllib.parse.urlencode(cmptData).encode(encoding='UTF8')
                req_url='http://timerbackend.geexek.com/raceBoard/scoreBoardInfo.do?'
                req=urllib.request.Request(req_url)
                res=urllib.request.urlopen(req,req_body)
                json_res=res.read().decode('UTF8',errors='ignore')
                try:
                    with codecs.open(r'D:\dataCollection\geexek\rankInfo.json', 'a', encoding='utf-8') as f_r:
                        f_r.write(json_content+',\n')
                except IOError as err:
                    print('error ' + str(err))
                finally:
                    f_r.close()
                rank_ids=json.loads(json_res)
                # print('比赛名称{}'.format(rank_ids['raceName']))
                for rankIds in rank_ids['roadList']:
                    print(rankIds['roadName'])
                    for rankid in rankIds['rankList']:
                        rkid=rankid['rankId']
                        rkname=rankid['listName']
                        comptData = urllib.request.urlopen(urllib.request.Request('http://timerbackend.geexek.com/getRankData.do')
                                                     ,urllib.parse.urlencode({'rankId':rkid,'pageNo':1}).encode(encoding='UTF8')).\
                            read().decode('UTF8',errors='ignore')
                        # print(json.loads(comptData))
                        try:
                            with codecs.open(r'D:\dataCollection\geexek\rankData.json','a',encoding='utf-8') as fp:
                                fp.write(comptData+',\n')
                        except IOError as err:
                            print('error '+str(err))
                        finally:
                            fp.close()
        except KeyError as e:
            return

def get_competition_by_keyword(kw):
    data = {'cmptType': -1, 'start': 0, 'searchContent':r'绿跑'}
    print(data)
    request_body = urllib.parse.urlencode(data).encode(encoding='UTF8')
    request_url = 'http://timerbackend.geexek.com//getCmptListForWeixin.do'
    req = urllib.request.Request(request_url)
    req.add_header('Referer', 'http://www.geexek.com/score')
    req.add_header('Content-Type',' application/x-www-form-urlencoded; charset=UTF-8')
    f = urllib.request.urlopen(req, request_body)
    json_content = f.read().decode('UTF8', errors='ignore')
    dic = json.loads(json_content)

    for d in dic['cmptList']:

        cmptId = d['cmptId']
        cmptName = d['cmptName']
        cmptStartTime = d['cmptStartTime'].split(' ')[0]
        cmpt_title='''"cmpt_id":{0},"cmpt_name":"{1}","cmpt_date":"{2}"'''.format(cmptId, cmptName, cmptStartTime)
        print(cmpt_title)

        # 根据比赛id获取比赛数据
        cmptData = {'cmptId': cmptId}
        req_body = urllib.parse.urlencode(cmptData).encode(encoding='UTF8')
        req_url = 'http://timerbackend.geexek.com/raceBoard/scoreBoardInfo.do?'
        req = urllib.request.Request(req_url)
        res = urllib.request.urlopen(req, req_body)
        json_res = res.read().decode('UTF8', errors='ignore')

        try:
            with codecs.open(r'D:\dataCollection\geexek\lvpao_rankInfo.json', 'a', encoding='utf-8') as f_r:
                f_r.write('"'+'rk_info'+'":'+json_res + ',\n')
        except IOError as err:
            print('error ' + str(err))
        finally:
            f_r.close()
        # print(json_res)
        rank_ids = json.loads(json_res)
        # print('比赛名称{}'.format(rank_ids['raceName']))
        for rankIds in rank_ids['roadList']:
            compt_zu=rankIds['roadName']
            for rankid in rankIds['rankList']:
                rkid = rankid['rankId']
                comptData = urllib.request.urlopen(
                    urllib.request.Request('http://timerbackend.geexek.com/getRankData.do')
                    , urllib.parse.urlencode({'rankId': rkid, 'pageNo': 1}).encode(encoding='UTF8')). \
                    read().decode('UTF8', errors='ignore')
                # print(json.loads(comptData))
                try:
                    with codecs.open(r'D:\dataCollection\geexek\lvpao_rankData.json', 'a', encoding='utf-8') as fp:
                        fp.write('{'+cmpt_title+''',"compt_zu":"{0}"'''.format(compt_zu)+',"'+'comptData'+'":'+comptData + '},\n')
                except IOError as err:
                    print('error ' + str(err))
                finally:
                    fp.close()

if __name__ == '__main__':
    print("开始采集数据")
    # get_competition()
    get_competition_by_keyword("绿跑")
    print('完成')


# #获取rankId
# http://timerbackend.geexek.com/raceBoard/scoreBoardInfo.do?
# cmptId=10150
#
# #获取rank数据
# http://timerbackend.geexek.com/getRankData.do
# rankId=32594&pageNo=1
#
# rankId=32594&pageNo=4