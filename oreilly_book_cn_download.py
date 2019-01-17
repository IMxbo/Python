import re
import json
import requests
import time
import os
from bs4 import BeautifulSoup as bs
def checkNameValid(name=None):
    """
    检测Windows文件名称！
    """
    if name is None:
        print("name is None!")
        return
    reg = re.compile(r'[\\/:*?"<>|\r\n]+')
    valid_name = reg.findall(name)
    if valid_name:
        for nv in valid_name:
            name = name.replace(nv, " ")
    return name

# web_page = open('web_page.html','r',encoding='utf-8').read()
# # reg_str = r'''<a href="index\.php\?func=book&amp;isbn=(\d{3}-\d-\d{4}-\d{4}-\d)" .*?title="(\S[^|]*)|<div style='float:left;margin:0 10px 5px 0;width:100px;'>&lt;img src='images/bookcover/(\w+\.jpg)'''
# # reg_str = '<a href="index.php?func=book&amp;isbn=(.*?)" class="tip" title="(.*?)|<div.*?img src=\'images/bookcover/(.*?).jpg\' border=.*3px;\'>(.*?)</div></div><div>(.*?)</div>">《(.*?)》</a></td><td valign="top" align="center" nowrap="nowrap">(.*?)</td><td .*nowrap">(.*?)元</td></tr>'
# reg_str= r'''<a href="index.php?func=book&amp;isbn=978-7-5198-2620-8" class="tip" title="机器学习应用系统设计|<div style='float:left;margin:0 10px 5px 0;width:100px;'>&lt;img src='images/bookcover/Machine_Learning_at_work_cvr_s.jpg' border='0'/&gt;<div style='word-wrap:break-word;font-style:italic;margin:6px 3px 8px 3px;'>有贺康顕,中山心太,西林孝:著</div></div><div>对于软件工程师，机器学习已经成为了一种常用术语。本书从“实用”的观点，介绍了如何将机器学习或数据分析的方法和工具应用到实际工作中,以及如何推进仍具有高度不确定性的机器学习项目等方法。本书主要围绕项目启动、系统构成、学习资源收集等经常关注的实践性问题进行阐述。如果你想做出些有显示度的人工智能应用系统的话，从本书学到的知识一定能够发挥积极的作用。</div>">《机器学习应用系统设计》</a>
# </td>
# <td valign="top" align="center" nowrap="nowrap">
# 2018年12月</td>
# <td valign="top" align="center" nowrap="nowrap">
# 68.00元</td>
# </tr>'''
# re_retval = re.compile(reg_str)

# # if os.path.exists('/bookcovers_cn/') == False:
# #     os.mkdir('/bookcovers_cn/')
# info = re_retval.findall(web_page)
# print(info)
# # print(info[0])
# # (scalar(idelta(Test_date1{s="Ingress_port_count4",p="6"}[5s]))-scalar(idelta(Test_date1{s="Egress_port_count1",p="6"}[5s])))/scalar(idelta(Test_date1{s="Ingress_port_count4",p="6"}[5s]))
book_set = []
book_index = 0
web_page = open('web_page.1.html','r',encoding='utf-8').read()
bsObj = bs(web_page)



for book in bsObj.findAll("a"):
    title = book.get("title")
    if title != None:
        book_set.append({})
        book_info_addr = 'http://www.oreilly.com.cn/'+book.get('href')
        isbn = book_info_addr[book_info_addr.rfind('=',1)+1:]

        book_set[book_index]['isbn'] = isbn
        book_set[book_index]['info_addr'] = book_info_addr

        book_html ='<title bookname="'+title.replace('|<div style=\'float:left;margin:0 10px 5px 0;width:100px;\'>','"/>',1)
        # print(book_html)
        bsObj1 = bs(book_html)
        # print(bsObj1)

        for i in bsObj1.findAll('title'):
            book_name_cn = checkNameValid(i.get('bookname'))
            book_set[book_index]['name_cn'] = book_name_cn
 
        for i in bsObj1.findAll('img',{'src':re.compile('images/bookcover/.*?\.[jpggif]+')}):
            # book_cover_cn_addr = 'http://www.oreilly.com.cn/'+i['src'].replace('_s','_l')
            src = i['src']
            book_cover_cn_addr = 'http://www.oreilly.com.cn/'+src[:src.rfind('_s')]+src[src.rfind('_s'):].replace('_s','_l')
            book_set[book_index]['cover_cn_addr'] = book_cover_cn_addr
            # print(book_cover_cn_addr)
            try:
                pass
                book_cover_cn = requests.get(book_cover_cn_addr)
            except:
                print(book_cover_cn)
                continue
            else:
                # book_cover_cn_file_name = os.getcwd()+'\\'+'oreilly_book_cn\\'+i['src'][i['src'].rfind('/')+1:].replace('_s','').replace('_cvr','')
                src = i['src'][i['src'].rfind('/')+1:].replace('_cvr','')
                book_cover_cn_file_name = os.getcwd()+'\\'+'oreilly_book_cn\\'+src[:src.rfind('_s')]+src[src.rfind('_s'):].replace('_s','')
                if os.path.exists(book_cover_cn_file_name):
                    continue
                book_set[book_index]['cover_cn_file_name'] = book_cover_cn_file_name
                print(book_cover_cn_file_name)
                book_cover_cn_file = open(book_cover_cn_file_name,'wb')
                book_cover_cn_file.write(book_cover_cn.content)
                book_cover_cn_file.close()

        author = bsObj1.findAll('div')[0].getText().replace(':著','')
        brief_info = bsObj1.findAll('div')[1].getText()

        book_set[book_index]['author'] = author
        book_set[book_index]['brief_info'] = brief_info
        book_index = book_index + 1
        time.sleep(5)

book_index = 0
cnt = 0
for i in bsObj.findAll('td',{'nowrap':'nowrap'}):
    
    if cnt%2 == 0:
        book_set[book_index]['public_date']=i.getText().replace('\n','')
    else:
        book_set[book_index]['price']=i.getText().replace('\n','')
        book_index = book_index +1
    cnt = cnt +1


# print(book_set)
json_data = json.dumps(book_set,ensure_ascii=False,sort_keys=True, indent=4, separators=(',', ': '))
print(json_data)
with open("tmp.txt", "w",encoding='utf-8') as fp:
    fp.write(json_data)


        # price = bsObj1.findAll('td')[1].getText()

        # print(author)
        # print(brief_info)

        # for i in bsObj1.findAll('div'):
        #     text = i.getText()
        #     print(text)
        #     time.sleep(5)
