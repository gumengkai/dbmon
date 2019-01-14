#! /usr/bin/python
# encoding: utf-8

import HTMLParser
import urllib2
from bs4 import BeautifulSoup

url = 'file:///C:/Users/Think/Desktop/test.html'

###构造解析html的类并且获取整个HTML中除去标签的文本数据

urltext = []


class MyHtmlParser(HTMLParser.HTMLParser):
    selected = ('table', 'h1', 'font', 'ul', 'li', 'tr', 'td', 'a')

    def reset(self):
        HTMLParser.HTMLParser.reset(self)
        self._level_stack = []

    def handle_starttag(self, tag, attrs):
        if tag in MyHtmlParser.selected:
            self._level_stack.append(tag)

    def handle_endtag(self, tag):
        if self._level_stack \
                and tag in MyHtmlParser.selected \
                and tag == self._level_stack[-1]:
            self._level_stack.pop()

    def handle_data(self, data):
        if "/".join(self._level_stack) in ('table/tr/td', 'table/tr/td/h1/font', 'table/tr/td/ul/li') and data != '\n':
            # print data
            urltext.append(data)

        ####调用解析html 的类，并且将获取的文本数据传递给urltext 数组

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

html_test = """
<h1 class="awr">
WORKLOAD REPOSITORY report for

</h1>
<p />
<table border="0" width="600" class="tdiff" summary="This table displays database instance information">
<tr><th class="awrbg" scope="col">DB Name</th><th class="awrbg" scope="col">DB Id</th><th class="awrbg" scope="col">Instance</th><th class="awrbg" scope="col">Inst num</th><th class="awrbg" scope="col">Startup Time</th><th class="awrbg" scope="col">Release</th><th class="awrbg" scope="col">RAC</th></tr>
<tr><td scope="row" class='awrnc'>ZJDQ</td><td align="right" class='awrnc'>833766800</td><td class='awrnc'>zjdq2</td><td align="right" class='awrnc'>2</td><td class='awrnc'>10-Aug-17 08:08</td><td class='awrnc'>11.2.0.4.0</td><td class='awrnc'>YES</td></tr>
</table>
<p />
<p />
<table border="0" width="600" class="tdiff" summary="This table displays host information">
<tr><th class="awrbg" scope="col">Host Name</th><th class="awrbg" scope="col">Platform</th><th class="awrbg" scope="col">CPUs</th><th class="awrbg" scope="col">Cores</th><th class="awrbg" scope="col">Sockets</th><th class="awrbg" scope="col">Memory (GB)</th></tr>
<tr><td scope="row" class='awrnc'>zjdddqtm02</td><td class='awrnc'>Linux x86 64-bit</td><td align="right" class='awrnc'> 120</td><td align="right" class='awrnc'>  60</td><td align="right" class='awrnc'>   4</td><td align="right" class='awrnc'>  511.80</td></tr>
</table>
<p />
<table border="0" width="600" class="tdiff" summary="This table displays snapshot information">
<tr><th class="awrnobg" scope="col"></th><th class="awrbg" scope="col">Snap Id</th><th class="awrbg" scope="col">Snap Time</th><th class="awrbg" scope="col">Sessions</th><th class="awrbg" scope="col">Cursors/Session</th><th class="awrbg" scope="col">Instances</th></tr>
<tr><td scope="row" class='awrnc'>Begin Snap:</td><td align="right" class='awrnc'>45952</td><td align="center" class='awrnc'>24-Aug-17 19:30:12</td><td align="right" class='awrnc'>8872</td><td align="right" class='awrnc'>       .2</td><td align="right" class='awrnc'>4</td></tr>
<tr><td scope="row" class='awrc'>End Snap:</td><td align="right" class='awrc'>45958</td><td align="center" class='awrc'>24-Aug-17 21:00:07</td><td align="right" class='awrc'>8910</td><td align="right" class='awrc'>       .2</td><td align="right" class='awrc'>4</td></tr>
<tr><td scope="row" class='awrnc'>Elapsed:</td><td class='awrnc'>&#160;</td><td align="center" class='awrnc'>              89.92 (mins)</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>DB Time:</td><td class='awrc'>&#160;</td><td align="center" class='awrc'>             697.79 (mins)</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
</table>
<p />
<h3 class="awr"><a class="awr" name="99999"></a>Report Summary</h3>
<p />Load Profile<p />
<table border="0" width="600" class="tdiff" summary="This table displays load profile">
<tr><th class="awrnobg" scope="col"></th><th class="awrbg" scope="col">Per Second</th><th class="awrbg" scope="col">Per Transaction</th><th class="awrbg" scope="col">Per Exec</th><th class="awrbg" scope="col">Per Call</th></tr>
<tr><td scope="row" class='awrc'>DB Time(s):</td><td align="right" class='awrc'>               7.8</td><td align="right" class='awrc'>               0.0</td><td align="right" class='awrc'>      0.00</td><td align="right" class='awrc'>      0.00</td></tr>
<tr><td scope="row" class='awrnc'>DB CPU(s):</td><td align="right" class='awrnc'>               5.7</td><td align="right" class='awrnc'>               0.0</td><td align="right" class='awrnc'>      0.00</td><td align="right" class='awrnc'>      0.00</td></tr>
<tr><td scope="row" class='awrc'>Redo size (bytes):</td><td align="right" class='awrc'>       2,240,709.3</td><td align="right" class='awrc'>           1,746.5</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Logical read (blocks):</td><td align="right" class='awrnc'>         528,424.6</td><td align="right" class='awrnc'>             411.9</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Block changes:</td><td align="right" class='awrc'>          12,069.3</td><td align="right" class='awrc'>               9.4</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Physical read (blocks):</td><td align="right" class='awrnc'>             645.7</td><td align="right" class='awrnc'>               0.5</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Physical write (blocks):</td><td align="right" class='awrc'>             671.4</td><td align="right" class='awrc'>               0.5</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Read IO requests:</td><td align="right" class='awrnc'>             431.2</td><td align="right" class='awrnc'>               0.3</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Write IO requests:</td><td align="right" class='awrc'>             458.0</td><td align="right" class='awrc'>               0.4</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Read IO (MB):</td><td align="right" class='awrnc'>               5.0</td><td align="right" class='awrnc'>               0.0</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Write IO (MB):</td><td align="right" class='awrc'>               5.3</td><td align="right" class='awrc'>               0.0</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Global Cache blocks received:</td><td align="right" class='awrnc'>             133.9</td><td align="right" class='awrnc'>               0.1</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Global Cache blocks served:</td><td align="right" class='awrc'>             208.6</td><td align="right" class='awrc'>               0.2</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>User calls:</td><td align="right" class='awrnc'>           5,629.6</td><td align="right" class='awrnc'>               4.4</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Parses (SQL):</td><td align="right" class='awrc'>           1,796.8</td><td align="right" class='awrc'>               1.4</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Hard parses (SQL):</td><td align="right" class='awrnc'>               0.0</td><td align="right" class='awrnc'>               0.0</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>SQL Work Area (MB):</td><td align="right" class='awrc'>              11.8</td><td align="right" class='awrc'>               0.0</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Logons:</td><td align="right" class='awrnc'>               4.4</td><td align="right" class='awrnc'>               0.0</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Executes (SQL):</td><td align="right" class='awrc'>           1,842.3</td><td align="right" class='awrc'>               1.4</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>Rollbacks:</td><td align="right" class='awrnc'>           1,067.3</td><td align="right" class='awrnc'>               0.8</td><td class='awrnc'>&#160;</td><td class='awrnc'>&#160;</td></tr>
<tr><td scope="row" class='awrc'>Transactions:</td><td align="right" class='awrc'>           1,283.0</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td><td class='awrc'>&#160;</td></tr>
</table>
<p />
Instance Efficiency Percentages (Target 100%)
<p />
<table border="0" width="600" class="tdiff" summary="This table displays instance efficiency percentages">
<tr><td scope="row" class='awrc'>Buffer Nowait %:</td><td align="right" class='awrc'>            99.99</td><td class='awrc'>Redo NoWait %:</td><td align="right" class='awrc'>           100.00</td></tr>
<tr><td scope="row" class='awrnc'>Buffer  Hit   %:</td><td align="right" class='awrnc'>            99.89</td><td class='awrnc'>In-memory Sort %:</td><td align="right" class='awrnc'>           100.00</td></tr>
<tr><td scope="row" class='awrc'>Library Hit   %:</td><td align="right" class='awrc'>           100.09</td><td class='awrc'>Soft Parse %:</td><td align="right" class='awrc'>           100.00</td></tr>
<tr><td scope="row" class='awrnc'>Execute to Parse %:</td><td align="right" class='awrnc'>             2.47</td><td class='awrnc'>Latch Hit %:</td><td align="right" class='awrnc'>            99.72</td></tr>
<tr><td scope="row" class='awrc'>Parse CPU to Parse Elapsd %:</td><td align="right" class='awrc'>            93.94</td><td class='awrc'>% Non-Parse CPU:</td><td align="right" class='awrc'>            98.16</td></tr>
</table>

<p />Top 10 Foreground Events by Total Wait Time<p />
<ul>
</ul>
<table border="0" width="600" class="tdiff" summary="This table displays top 10 wait events by total wait time"><tr><th class="awrbg" scope="col">Event</th><th class="awrbg" scope="col">Waits</th><th class="awrbg" scope="col">Total Wait Time (sec)</th><th class="awrbg" scope="col">Wait Avg(ms)</th><th class="awrbg" scope="col">% DB time</th><th class="awrbg" scope="col">Wait Class</th></tr>
<tr><td scope="row" class='awrc'>DB CPU</td><td align="right" class='awrc'>&#160;</td><td align="right" class='awrc'>30.8K</td><td align="right" class='awrc'>&#160;</td><td align="right" class='awrc'>73.6</td><td class='awrc'>&#160;</td></tr>
<tr><td scope="row" class='awrnc'>log file sync</td><td align="right" class='awrnc'>1,217,279</td><td align="right" class='awrnc'>3926.1</td><td align="right" class='awrnc'>3</td><td align="right" class='awrnc'>9.4</td><td class='awrnc'>Commit</td></tr>
<tr><td scope="row" class='awrc'>latch: cache buffers chains</td><td align="right" class='awrc'>93,336</td><td align="right" class='awrc'>2677.6</td><td align="right" class='awrc'>29</td><td align="right" class='awrc'>6.4</td><td class='awrc'>Concurrency</td></tr>
<tr><td scope="row" class='awrnc'>read by other session</td><td align="right" class='awrnc'>87,370</td><td align="right" class='awrnc'>2088.3</td><td align="right" class='awrnc'>24</td><td align="right" class='awrnc'>5.0</td><td class='awrnc'>User I/O</td></tr>
<tr><td scope="row" class='awrc'>db file sequential read</td><td align="right" class='awrc'>1,692,729</td><td align="right" class='awrc'>1187.7</td><td align="right" class='awrc'>1</td><td align="right" class='awrc'>2.8</td><td class='awrc'>User I/O</td></tr>
<tr><td scope="row" class='awrnc'>gc buffer busy acquire</td><td align="right" class='awrnc'>94,607</td><td align="right" class='awrnc'>1011.6</td><td align="right" class='awrnc'>11</td><td align="right" class='awrnc'>2.4</td><td class='awrnc'>Cluster</td></tr>
<tr><td scope="row" class='awrc'>direct path read</td><td align="right" class='awrc'>227,528</td><td align="right" class='awrc'>812.9</td><td align="right" class='awrc'>4</td><td align="right" class='awrc'>1.9</td><td class='awrc'>User I/O</td></tr>
<tr><td scope="row" class='awrnc'>gc current grant 2-way</td><td align="right" class='awrnc'>1,223,967</td><td align="right" class='awrnc'>617.2</td><td align="right" class='awrnc'>1</td><td align="right" class='awrnc'>1.5</td><td class='awrnc'>Cluster</td></tr>
<tr><td scope="row" class='awrc'>gc cr grant 2-way</td><td align="right" class='awrc'>712,618</td><td align="right" class='awrc'>523.5</td><td align="right" class='awrc'>1</td><td align="right" class='awrc'>1.3</td><td class='awrc'>Cluster</td></tr>
<tr><td scope="row" class='awrnc'>latch free</td><td align="right" class='awrnc'>37,468</td><td align="right" class='awrnc'>189</td><td align="right" class='awrnc'>5</td><td align="right" class='awrnc'>.5</td><td class='awrnc'>Other</td></tr>
</table><p />
<p />Wait Classes by Total Wait Time<p />
<ul>
</ul>
<table border="0" width="600" class="tdiff" summary="This table displays wait class statistics ordered by total wait time"><tr><th class="awrbg" scope="col">Wait Class</th><th class="awrbg" scope="col">Waits</th><th class="awrbg" scope="col">Total Wait Time (sec)</th><th class="awrbg" scope="col">Avg Wait (ms)</th><th class="awrbg" scope="col">% DB time</th><th class="awrbg" scope="col">Avg Active Sessions</th></tr>
<tr><td scope="row" class='awrc'>Administrative</td><td align="right" class='awrc'>17,194,757</td><td align="right" class='awrc'>36,275</td><td align="right" class='awrc'>2</td><td align="right" class='awrc'>86.6</td><td align="right" class='awrc'>6.7</td></tr>
<tr><td scope="row" class='awrnc'>DB CPU</td><td align="right" class='awrnc'>&#160;</td><td align="right" class='awrnc'>30,829</td><td align="right" class='awrnc'>&#160;</td><td align="right" class='awrnc'>73.6</td><td align="right" class='awrnc'>5.7</td></tr>
<tr><td scope="row" class='awrc'>User I/O</td><td align="right" class='awrc'>2,777,439</td><td align="right" class='awrc'>4,220</td><td align="right" class='awrc'>2</td><td align="right" class='awrc'>10.1</td><td align="right" class='awrc'>0.8</td></tr>
<tr><td scope="row" class='awrnc'>Commit</td><td align="right" class='awrnc'>1,217,290</td><td align="right" class='awrnc'>3,926</td><td align="right" class='awrnc'>3</td><td align="right" class='awrnc'>9.4</td><td align="right" class='awrnc'>0.7</td></tr>
<tr><td scope="row" class='awrc'>Concurrency</td><td align="right" class='awrc'>1,155,550</td><td align="right" class='awrc'>3,064</td><td align="right" class='awrc'>3</td><td align="right" class='awrc'>7.3</td><td align="right" class='awrc'>0.6</td></tr>
<tr><td scope="row" class='awrnc'>Cluster</td><td align="right" class='awrnc'>2,721,160</td><td align="right" class='awrnc'>2,804</td><td align="right" class='awrnc'>1</td><td align="right" class='awrnc'>6.7</td><td align="right" class='awrnc'>0.5</td></tr>
<tr><td scope="row" class='awrc'>System I/O</td><td align="right" class='awrc'>6,137,081</td><td align="right" class='awrc'>2,124</td><td align="right" class='awrc'>0</td><td align="right" class='awrc'>5.1</td><td align="right" class='awrc'>0.4</td></tr>
<tr><td scope="row" class='awrnc'>Other</td><td align="right" class='awrnc'>4,299,539</td><td align="right" class='awrnc'>1,414</td><td align="right" class='awrnc'>0</td><td align="right" class='awrnc'>3.4</td><td align="right" class='awrnc'>0.3</td></tr>
<tr><td scope="row" class='awrc'>Network</td><td align="right" class='awrc'>23,401,810</td><td align="right" class='awrc'>121</td><td align="right" class='awrc'>0</td><td align="right" class='awrc'>.3</td><td align="right" class='awrc'>0.0</td></tr>
<tr><td scope="row" class='awrnc'>Application</td><td align="right" class='awrnc'>28,234</td><td align="right" class='awrnc'>71</td><td align="right" class='awrnc'>3</td><td align="right" class='awrnc'>.2</td><td align="right" class='awrnc'>0.0</td></tr>
<tr><td scope="row" class='awrc'>Configuration</td><td align="right" class='awrc'>770</td><td align="right" class='awrc'>8</td><td align="right" class='awrc'>11</td><td align="right" class='awrc'>.0</td><td align="right" class='awrc'>0.0</td></tr>
</table>
"""

if __name__ == '__main__':

    soup = BeautifulSoup(html_test)
    table_list =  soup.find_all('table')
    item_list = []
    value_list = []

    dic = {}
    for table in table_list:
        # 实例基础信息
        if table['summary'] in  ("This table displays database instance information","This table displays host information"):
            inst_info = {}
            item_info = table.find_all('th')
            value_info = table.find_all('td')
            for i in xrange(len(item_info)):
                item = item_info[i].get_text()
                value = value_info[i].get_text()
                inst_info[item] = value
        # Elapsed&DB Time
        elif table['summary'] == "This table displays snapshot information":
            res = table.find_all('tr')
            for i in xrange(len(res)):
                if 'Elapsed' in  res[i].get_text():
                    Elapsed = res[i].find_all('td')[2].get_text()
                elif 'DB Time' in  res[i].get_text():
                    DB_Time = res[i].find_all('td')[2].get_text()
            inst_info['Elapsed'] = Elapsed.strip()
            inst_info['DB_Time'] = DB_Time.strip()
        # Load Profile
        elif table['summary'] == "This table displays load profile":
            prof_info = {}
            res = table.find_all('tr')
            for i in xrange(len(res)):
                if res[i].find_all('td'):
                    item =  res[i].find_all('td')[0].get_text().replace(':','').strip()
                    value_per_sec = res[i].find_all('td')[1].get_text().strip()
                    value_per_trs = res[i].find_all('td')[2].get_text().strip()
                    list_value = [value_per_sec,value_per_trs]
                    prof_info[item] = list_value
        # Instance Efficiency Percentages
        elif table['summary'] == "This table displays instance efficiency percentages":
            inst_effi = {}
            res = table.find_all('tr')
            for i in xrange(len(res)):
                if res[i].find_all('td'):
                    item1 = res[i].find_all('td')[0].get_text().replace('%:','').strip()
                    value1 = res[i].find_all('td')[1].get_text().strip()
                    item2 = res[i].find_all('td')[2].get_text().replace('%:','').strip()
                    value2 = res[i].find_all('td')[3].get_text().strip()
                    inst_effi[item1] = value1
                    inst_effi[item2] = value2
        # Top 10 Foreground Events by Total Wait Time
        elif table['summary'] == "This table displays top 10 wait events by total wait time":
            top_10_bag_events = {}
            res = table.find_all('tr')
            for i in xrange(len(res)):
                if res[i].find_all('td'):
                    item = res[i].find_all('td')[0].get_text().replace('%:','').strip()
                    value1 = res[i].find_all('td')[1].get_text().strip()
                    value2 = res[i].find_all('td')[2].get_text().strip()
                    value3 = res[i].find_all('td')[3].get_text().strip()
                    value4 = res[i].find_all('td')[4].get_text().strip()
                    value5 = res[i].find_all('td')[5].get_text().strip()
                    top_10_bag_events[item] = [value1,value2,value3,value4,value5]
        # Wait Classes by Total Wait Time
        elif table['summary'] == "This table displays wait class statistics ordered by total wait time":
            top_10_bag_events = {}
            res = table.find_all('tr')
            for i in xrange(len(res)):
                if res[i].find_all('td'):
                    item = res[i].find_all('td')[0].get_text().replace('%:', '').strip()
                    value1 = res[i].find_all('td')[1].get_text().strip()
                    value2 = res[i].find_all('td')[2].get_text().strip()
                    value3 = res[i].find_all('td')[3].get_text().strip()
                    value4 = res[i].find_all('td')[4].get_text().strip()
                    value5 = res[i].find_all('td')[5].get_text().strip()
                    top_10_bag_events[item] = [value1, value2, value3, value4, value5]

    dic['inst_info'] = inst_info
    dic['prof_info'] = prof_info
    dic['inst_effi'] = inst_effi
    dic['top_10_bag_events'] = top_10_bag_events
    print dic

    # DB TIME,ELAPSED TIME分析
    inst_info = dic['inst_info']
    Elapsed = float(inst_info['Elapsed'].replace('(mins)', ''))
    DB_Time = float(inst_info['DB_Time'].replace('(mins)', ''))
    cpus = float(inst_info['CPUs'])
    if cpus * 0.1 > DB_Time / Elapsed:
        print 'cpu*0.1>DB Time/Elapsed，数据库当前时段负载极低'
    elif cpus * 0.8 > DB_Time / Elapsed and DB_Time / Elapsed > cpus * 0.1:
        print 'cpus*0.8>DB Time/Elapsed>cpus*0.1，数据库当前时段负载较低'

    # Load profile分析
    prof_info = dic['prof_info']
    # Parse and Hard Parse
    Parses = float(prof_info['Parses (SQL)'][0].replace(',',''))
    Hard_Parses = float(prof_info['Hard parses (SQL)'][0].replace(',',''))
    if Parses > 300:
        print "每秒解析数超过300，请检查应用程序效率，尝试调整session_cursor_cache"
    if Hard_Parses > 300:
        print "每秒硬解析数超过100，硬解析较多，sql重用率不高，请检查绑定变量使用或共享池设置是否合理"
    # Rollbacks
    Rollbacks = float(prof_info['Rollbacks'][0].replace(',',''))
    if Rollbacks > 100:
        print '每秒回滚数超过100，大量的回滚会增加数据库负载，且不正常，建议找到相关事务调整业务逻辑'
    # Transactions
    Transactions = float(prof_info['Transactions'][0].replace(',',''))
    if Transactions > 1000:
        print '每秒数据库超过1000，数据库事务繁忙'
    Logons = float(prof_info['Logons'][0].replace(',',''))
    if Logons > 1:
        print '每秒数据库登录数超过1，数据库登录较频繁'

    # Instance Efficiency Percentages
    inst_effi = dic['inst_effi']
    Buffer_Nowait = float(inst_effi['Buffer Nowait'])
    if Buffer_Nowait < 99:
        print "Buffer NOwait低于99%，从缓冲取中获取buffer可能存在争用"
    Buffer_Hit = float(inst_effi['Buffer  Hit'])
    if Buffer_Hit < 90:
        print "缓冲命中率低于90%，考虑调整db_cache_size参数"
    Library_Hit = float(inst_effi['Library Hit'])
    if Library_Hit < 90:
        print "library cache命中率低于90%，考虑调大shared pool/使用绑定变量/修改cursor_sharing"
    Redo_NoWait = float(inst_effi['Redo NoWait'])
    if Redo_NoWait < 90:
        print "表示在LOG缓冲区获得buffer的未等待比例，小于90，考虑增加LOG BUFFER"
    Excute_to_Parse = float(inst_effi['Execute to Parse'])
    if Excute_to_Parse < 50:
        print "SQL解析执行占比较低，建议通过参数调整和SQL优化的手段来增加解析占比，一次解析，多次执行"
    Parse_CPU_to_Parse_Elapsed = float(inst_effi['Parse CPU to Parse Elapsd'])
    if Parse_CPU_to_Parse_Elapsed < 90:
        print "解析等待时间较长"
    Non_Parse_CPU = float(inst_effi['% Non-Parse CPU:'])
    if Non_Parse_CPU<90:
        print "sql解析消耗的CPU时间过多"
    In_memory_sort = float(inst_effi['In-memory Sort'])
    if In_memory_sort < 95:
        print "有大量排序在临时表中进行，考虑适当调大PGA_AGGREGATE_TARGET或SORT_AREA_SIZE"
    Soft_Parse = float(inst_effi['Soft Parse'])
    if Soft_Parse < 95:
        print "软解析比例较低，尝试调整应用使用绑定变量"






























