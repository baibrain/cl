import requests,codecs,bs4,time,sqlite3,sys,re,os,random
from bs4 import BeautifulSoup

'''
解释列表的各项内容
已经存在的更新，不存在的新增

CREATE TABLE "main_page" (
"id"  INTEGER  NOT NULL DEFAULT 1,
"item_title_url"  TEXT(100) NOT NULL,
"item_type"  TEXT(10),
"item_title"  TEXT(200),
"item_comments_num"  INTEGER,
"item_author"  TEXT(50),
"item_author_time"  TEXT(20),
"item_last_replyer"  TEXT(50),
"item_last_replyer_time"  TEXT(20),
"update_time"  timestamp,
PRIMARY KEY ("id","item_title_url"));

'''
def get_items(url,items_list):

##    get_items_start_time = time.clock()
    global is_skip
    formatting_items = []
    no_formatting_items = []
    item_type = None
    item_title = None
    item_title_url = None
    item_comments_num = None
    item_author = None
    item_author_time = None
    item_last_replyer = None
    item_last_replyer_time = None

###有TYPE,积分,精,没有评论
    TYPE = 1
    TITLE = 2
    JIFEN = 3
    NEW = 4
    JING = 5
    
    AUTHOR = 6
    AUTHOR_TIME = 7
    COMMENTS_NUM = 8
    LAST_REPLYER_TIME = 9
    LAST_REPLYER = 10

    SKIP_ITEM = 2###不处理前7行数据

    temp_skip_item = 1
##    end_num = 5
##    start_num_no_new = 3
##    start_num_have_new = 4
##    have_new = 3
    conn = sqlite3.connect('test.db')
    curs = conn.cursor()
    
    patt = re.compile('.+fid=(\d+)')
    mat = patt.match(url)
    item_area = mat.groups()[0]
    for item in items_list:####处理一页中的每一条数据
        is_jifen = False
        is_jing = False
        if type(item) == bs4.element.Tag:
            if  item.name =='tr' :
                
                if  item.get('class')  and ' '.join(item.get('class')) =='tr3 t_one':##一条有效数据tr                  
                    item_l = list(item.stripped_strings)
##                    no_formatting_items.append('###'.join(list(item.stripped_strings)))
                    if is_skip and temp_skip_item <= SKIP_ITEM :###不处理前#行数据
                        temp_skip_item += 1
                        continue
                    item_title_url = item.find('h3').a.get('href')

                    pat1 = re.compile(r'(^\[.*\[.*\]$)|(^\[.*\].*\]$)')###不符合TYPE
                    pat2 = re.compile(r'^\[.+\]$')
                    mat1 = pat1.match(item_l[TYPE])
                    mat2 = pat2.match(item_l[TYPE])
                    pat3 = re.compile(r'^↑[0-9].*')
                    mat3 = pat3.match(item_l[TYPE])
                    count_lose = 0
                    count_comments = 0
                    for i in range(len(item_l)):
                        if '[積分+' in item_l[i]:
                            JIFEN = i
                            is_jifen = True
                            count_lose += 1
                        if 'new' ==   item_l[i]:
                            count_lose += 1
                        if '[精]' ==  item_l[i]:
                            is_jing = True
                            JING = i
                            count_lose += 1
                        if '[' ==  item_l[i]:
                            count_comments = 1
                            start_num = i
                        if ']' ==  item_l[i]:
                            end_num = i
                    if (not mat1 and mat2) or mat3:###有类型type
                        item_type = item_l[TYPE]
                        item_title =item_l[TITLE]
                        if is_jifen:
                            item_title += item_l[JIFEN]
                        if is_jing:
                            item_title += item_l[JING]
                        if count_comments ==0:  ###没有评论
                            try:
                                item_comments_num  = item_l[COMMENTS_NUM+(count_lose-3)]
                                item_author = item_l[AUTHOR+(count_lose-3)]
                                item_author_time = item_l[AUTHOR_TIME+(count_lose-3)]
                                item_last_replyer = item_l[LAST_REPLYER+(count_lose-3)]
                                item_last_replyer_time = item_l[LAST_REPLYER_TIME+(count_lose-3)]
                            except IndexError:
                                print(item_l)
                                print(str(count_lose))
                        else:###有评论
                            item_comments_num  = item_l[COMMENTS_NUM+(end_num-start_num+1)+(count_lose-3)]
                            item_author = item_l[AUTHOR+(end_num-start_num+1)+(count_lose-3)]
                            item_author_time = item_l[AUTHOR_TIME+(end_num-start_num+1)+(count_lose-3)]
                            try:
                                item_last_replyer = item_l[LAST_REPLYER+(end_num-start_num+1)+(count_lose-3)]
                            except:
                                print('解析TYPE出错')
                                print(item_l)
                                print(str(LAST_REPLYER))
                                print(str(end_num))
                                print(str(start_num))
                                print(str(count_lose))
                                print(str(LAST_REPLYER+(end_num-start_num+1)+(count_lose-3)))
                            item_last_replyer_time = item_l[LAST_REPLYER_TIME+(end_num-start_num+1)+(count_lose-3)]
                    else:###没有类型
                        item_type = 'NO TYPE'
                        item_title =item_l[TITLE-1]
                        if is_jifen:
                            item_title += item_l[JIFEN]
                        if is_jing:
                            item_title += item_l[JING]
                        if count_comments ==0:  ###没有评论
                            item_comments_num  = item_l[COMMENTS_NUM+(count_lose-3)-1]
                            item_author = item_l[AUTHOR+(count_lose-3)-1]
                            item_author_time = item_l[AUTHOR_TIME+(count_lose-3)-1]
                            item_last_replyer = item_l[LAST_REPLYER+(count_lose-3)-1]
                            item_last_replyer_time = item_l[LAST_REPLYER_TIME+(count_lose-3)-1]
                        else:###有评论
                            item_comments_num  = item_l[COMMENTS_NUM+(end_num-start_num+1)+(count_lose-3)-1]
                            item_author = item_l[AUTHOR+(end_num-start_num+1)+(count_lose-3)-1]
                            item_author_time = item_l[AUTHOR_TIME+(end_num-start_num+1)+(count_lose-3)-1]
                            item_last_replyer = item_l[LAST_REPLYER+(end_num-start_num+1)+(count_lose-3)-1]
                            item_last_replyer_time = item_l[LAST_REPLYER_TIME+(end_num-start_num+1)+(count_lose-3)-1]              

                   
##                    formatting_items.append((item_type,item_title,item_comments_num,item_author,item_author_time,item_last_replyer,item_last_replyer_time))
                    try:
                        sql_string = 'insert into main_page (item_id,item_area,item_type,item_title,item_comments_num,item_author,item_author_time,item_last_replyer,item_last_replyer_time,item_title_url,update_time) values('
                        item_title = item_title.replace(',','\,').replace("'",' ').replace('"','').replace('(',' ').replace(')',' ').replace('%', ' ').replace('<', ' ').replace('>', ' ')
                        sql_string +=get_item_dir(item_title_url)+',\''+ item_area+'\',\''+item_type+'\',\''+item_title+'\',\''+item_comments_num+'\',\''+item_author+'\',\''+item_author_time+'\',\''+item_last_replyer+'\',\''+item_last_replyer_time+'\',\''+item_title_url+'\',datetime("now","localtime"))'

##                        print(sql_string)
                        curs.execute(sql_string)
##                        conn.commit()
                    except sqlite3.IntegrityError:###重复数据，不新增，更新数据
                        try:
                            sql_cha ='select * from main_page where item_title_url =\''+item_title_url+'\''
                            curs.execute(sql_cha)
                            date = curs . fetchall ()
                            if date[0][6] !=item_last_replyer:
                                sql_string = 'update main_page set  item_last_replyer =\''+item_last_replyer+'\',item_title = \''+item_title+'\',item_area = \''+item_area+'\',item_last_replyer_time = \''+item_last_replyer_time+'\',item_comments_num = \''+item_comments_num+'\',update_time = datetime("now","localtime")   where item_title_url = \'' +item_title_url+'\''
##                            print(sql_string)
                                curs.execute(sql_string)
##                                conn.commit()
                        except:
                            print('11sql_string = '+sql_string)
                            print(sys.exc_info())
                            conn.close()
##                            sys.exit()                           
                    except:
                        print('sql_string = '+sql_string)
                        print(sys.exc_info())
                        conn.close()
                        return
##                        sys.exit()

    conn.commit()
    conn.close()
##    get_items_end_time = time.clock()
##    print('get_items\'s time :' +str(get_items_end_time-get_items_start_time)+' 秒')
    return formatting_items## ,no_formatting_items


def get_page_locate(html_root):
    try:
        page,total_page = html_root.find('div',{'class':'pages'}).input.get('value').split('/')
    except AttributeError:
        return [int('1'),int('1') ]
    return [int(page),int(total_page) ]

def do_it(url,start_page=1,end_page=0):
    global is_skip
    all_url = url+str(start_page)
    resp = requests.get(all_url, headers=headers, timeout=25)
    if resp.status_code != requests.codes.ok:
        print("ERROR!! " + str(resp.status_code))
        sys.exit()
    page = resp.content
    html = BeautifulSoup( page.decode('GB18030'),"html.parser")
    end_page = get_page_locate(html)[1] if end_page == 0 or end_page > get_page_locate(html)[1]  else end_page
    for i in range(start_page,end_page+1):
        if i == 1:
            is_skip = True
        print('正在处理第'+str(i)+'页...',end='-->')
        all_url = url+str(i)
        start_time = time.clock()
        resp = requests.get(all_url, headers=headers, timeout=25)
        if resp.status_code != requests.codes.ok:
            print("ERROR!! " + str(resp.status_code))
            sys.exit()
        page = resp.content
        html = BeautifulSoup( page.decode('GB18030'),"html.parser")
        list_item = html.find(id="ajaxtable").find('tbody')
        items = get_items(url,list_item)
        end_time = time.clock()
        print('第'+str(i)+'页处理完成,共耗时 '+str(end_time-start_time)+' 秒')
        rtime = random.randint(0,4)
        print('sleep---->'+str(rtime))
        time.sleep(10)

#下载图片函数
def download_image_file(img_url,local_dir='.\\',filename=''):
    try: #抛出异常
        t_name = img_url.split('/')[-1]
        t_name_end = t_name.split('.')[-1]
        local_filename = t_name if not filename else filename+'.'+t_name_end
        print('start down --->'+local_filename,end="--->")
        img = requests.get(img_url, stream=True,timeout=3) # here we need to set stream = True parameter
        with open(local_dir+local_filename, 'wb') as f:
##            print(local_dir+local_filename)
            for chunk in img.iter_content(chunk_size=1024*50):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        print('end down' )
        return local_filename
    except:
        print ("something is ERROR ! Ignore it !")

def get_item_dir(url):
    if 'tid=' in url:
        item_dir = url.split('tid=')[1].split('&')[0]
        return item_dir
    else:
        item_dir = url.split('/')[-1].split('.')[0]
        return item_dir

def get_item_comms(url,url_item,start=1,end=1,root_dir='e:\\photos\\'):
    all_url = url+url_item
##    print(all_url)
    item_dir = get_item_dir(all_url)
    img_dir_item = root_dir+item_dir+'\\item\\'
    img_dir_header = root_dir+item_dir+'\\header\\'
    try:
        os.makedirs(img_dir_item)
    except:
        pass
    try:
        os.makedirs(img_dir_header)
    except:
        pass
    resp = requests.get(all_url, headers=headers, timeout=25)
    if resp.status_code != requests.codes.ok:
        print("ERROR!! " + str(resp.status_code))
        sys.exit()
    page = resp.content
    html = BeautifulSoup( page.decode('GB18030'),"html.parser")
    total_page = get_page_locate(html)[1]
    if start == 1:
        imgs = html.findAll('img')
        print('total imgs -->'+str(len(imgs)))
        print("开始处理第1页")
        for img in imgs:
            img_url = img.get('src')
            if img.has_attr('onclick'):###主题图片
                download_image_file(img_url,local_dir=img_dir_item)
            if not img.has_attr('onclick'):###头像###处理父节点
                name = img.findParent('th').font.b.get_text()
                download_image_file(img_url,local_dir=img_dir_header,filename=name)
        print("第1页处理完成")
        

####处理指定页面
    if start <= end and end >=2:
        end_page = end if total_page>end else total_page
        for i in range(2,end_page+1):
            print("开始处理第"+str(i)+"页")
            all_url = url+"read.php?tid="+item_dir+"&page="+str(i)
            resp = requests.get(all_url, headers=headers, timeout=25)
            if resp.status_code != requests.codes.ok:
                print("ERROR!! " + str(resp.status_code))
                sys.exit()
            page = resp.content
            html = BeautifulSoup( page.decode('GB18030'),"html.parser")
            imgs = html.findAll('img')
            for img in imgs:
                img_url = img.get('src')
                if img.has_attr('onclick'):###主题图片
                    download_image_file(img_url,local_dir=img_dir_item)
                if not img.has_attr('onclick'):###头像
                    try:
                        name = img.findParent('th').font.b.get_text()
                    except AttributeError:
                        try:
                            name = img.findParent('th').b.get_text()
                        except AttributeError:
                            continue
                    download_image_file(img_url,local_dir=img_dir_header,filename=name)
            print("第"+str(i)+"页处理完成")

##    with codecs.open('mtime.txt','wt') as file:
##        file.write(resp)
##    print(resp.encode)
##    with open('mtime.html',encoding='utf-8') as fp:
##        soup = BeautifulSoup( fp,"html.parser")
##        print(soup.title)
##with open('mtime.html',encoding='gb2312') as fp:
if __name__ == '__main__':
    item_area = None
    is_skip = False 
    http_head = 'http://c6.xefr.biz/'
##    url = http_head + 'thread0806.php?fid=21&orderway=postdate&asc=DESC&page='
##    url = http_head + 'thread0806.php?fid=8&orderway=postdate&asc=DESC&page='
##    url = http_head + 'thread0806.php?fid=7&page='
    url = http_head + 'thread0806.php?fid=%s&orderway=postdate&asc=DESC&page='
##    url = http_head + 'thread0806.php?fid=22&search=digest&page='
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36', 'Cookie': 'mtime'}

    for area_item in ('16','15','17','2','20','21','22','24','5','7','8'):
        surl = url%area_item
        do_it(surl,1,10)
##    do_it(url,7,10)

    
##    conn = sqlite3.connect('test.db')
##    curs = conn.cursor()
##    s_string = 'select item_title_url from main_page where item_area =21 limit 20'
##    curs.execute(s_string)
##    date = curs . fetchall ()
##    for i in date:
##        get_item_comms(http_head,i[0],1,1)



    

