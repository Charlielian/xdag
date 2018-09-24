

import os,sys
import re,time,datetime
from SqlModel import SqlModel
from multiprocessing import Pool
exe_path =os.path.split(os.path.abspath(sys.argv[0]))[0]




def get_last_lnum(path,file):
    f = open(path+file, 'r')  # 读取line_number.txt 得到上次读取的行数
    last_lnum = int(f.readline())
    f.close()
    return last_lnum
def mark_line(path,filename):
    if os.path.exists(path+filename):
        last_lnum = get_last_lnum(path,filename)
        operation_log("Read last row number %s"%(last_lnum) )
        return last_lnum
    else:
        end_exit(3)

    #print("%s does not exist in %s directory"%(filename,txtdir))

#if os.path.exists(xdagdir + "xdag.log") and (not os.path.exists(txtdir + "pylock.txt")) :
#     print("ok")

def makeNewFile(path,filename): # 新建文件
    f = open(path + filename, 'w')
    f.close()
    operation_log("--------------------------Demarcation line Start----------------------------------------")
    operation_log("Pylock.txt does not exist, Create pylock.txt")
    return True
def operation_log(str_context):
    """
    r 只能读
    r+ 可读可写 不会创建不存在的文件 从顶部开始写 会覆盖之前此位置的内容
    w+ 可读可写 如果文件存在 则覆盖整个文件 不存在则创建
    w 只能写 覆盖整个文件 不存在则创建
    a 只能写 从文件底部添加内容 不存在则创建
    a+ 可读可写 从文件顶部读取内容 从文件底部添加内容 不存在则创建
    """
    filename = "Script_Operation.log"
    f = open(txtdir + filename, 'a')
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    cur_time = datetime.datetime.now()
    context = str(cur_time) +" " +str_context +"\n"
    f.write(context)
    f.close()
def xdag_read(xdag_path,txt_path,filter_str,last_lnum):
    operation_log("Start reading file xdag.log ")
    this_num = 0
    #last_lnum = 1
    f_payouts = xdag_path+ "xdag.log"
    payoutrecordlist = []
    if os.path.exists(f_payouts):
        with open(f_payouts, 'r') as f:
            for line in f:
                if this_num > last_lnum and filter_str in line:
                    tempstr = re.sub(r"\s{2,}", " ", line.strip())
                    splitlist = tempstr.split()
                    timevalue = datetime.datetime.strptime(splitlist[0] + " " + splitlist[1][0:8], "%Y-%m-%d %H:%M:%S")
                    data = (tempstr, timevalue, splitlist[6], splitlist[8], splitlist[10])
                    payoutrecordlist.append(data)
                this_num += 1
            sql = "INSERT IGNORE INTO tb_payoutinfo(record, timefield, block, address, xdagcount) VALUES(%s, %s, %s, %s, %s)"
            #print("打印读取了xdag的行数",this_num)
            #print(payoutrecordlist)
            try:
                if len(payoutrecordlist) > 1:
                    SqlModel.put_info_by_sql_many(sql_str=sql, datalist=payoutrecordlist)
                    #print("many")
                    operation_log("INSERT IGNORE INTO tb_payoutinfo by sql_many" )
                    # sql_str, data_list
                else:
                    SqlModel.put_info_by_sql(sql_str=sql, data=payoutrecordlist[0])
                    #print("one")
                    operation_log("INSERT IGNORE INTO tb_payoutinfo by sql")


            except Exception as e:

                print(e)
            #标记已写入行号数
            this_num =1
            f = open(txt_path + "line_number.txt", 'w')
            f.write(str(this_num))
            f.close()
    else:
        #operation_log("xdag.log does not exist in %s directory" % (txtdir))
        end_exit(7)
    operation_log("End reading file xdag.log ")
def matchline(str, file):
    # str:匹配的字符串
    # file:全路径文件名
    # 返回:成功->line，失败->False

    if os.path.exists(file):
        f = open(file, 'r', encoding='gbk')
        readlist = f.readlines()
        f.close()
        for line in readlist:
            if str in line:
                return line
            else:
                pass
        return 0
    else:
        end_exit(6)


def tuple2list(a):
    # 元组转列表
    #print(a,type(a))
    if a == None:
        b = []
    else:
        b = list(a)
        for c in b:
            b[b.index(c)] = list(c)
    return b

def stats(stats_path):
    # file 需要标记的文件，stats_path 为stats.txt 文件全路径
    operation_log("Start reading file stats.txt")
    str_line = matchline('hashrate', stats_path)
    hashrate_net = round(float(str_line.strip().split()[6]) / 1000000, 2)  # 1.全网算力，去除头尾空格再用空格进行分割,然后取列表中的第7个,为全网算力（单位为TH）
    hashrate_pool = round(float(str_line.strip().split()[4]) / 1000000,2)  # 2.矿池算力，去除头尾空格再用空格进行分割,然后取列表中的第5个,为矿池算力（单位为TH）

    str_line = matchline('blocks:', stats_path)
    blockhigh = int(str_line.strip().split()[3])  # 3.区块高度
    str_line = matchline('main blocks', stats_path)
    mainblockhigh = int(str_line.strip().split()[4])  # 4.主区块高度
    str_line = matchline('difficulty', stats_path)
    diff = str_line.strip().split()[4]  # 5.区块难度
    operation_log("End reading file stats.txt")

    return hashrate_net, hashrate_pool, blockhigh, mainblockhigh, diff

def read_miner_txt(path_file):
    #f_miners = txtdir + "miners.txt"
    if os.path.exists(path_file):
        f = open(path_file, 'r', encoding='gbk')
        readlist = f.readlines()
        f.close()
        operation_log("Read miners.txt complete")
        # 读取矿机txt清单
        address = ""
        addresslist_new = []
        # minerid = ""
        minerlist_new = []
        minerlist = []
        # hashrate_1miner = 0
        totalpaid = 0
        operation_log("Start filtering the miners' address and ID")
        for line in readlist:
            splitlist_read = line.strip().split()
            if len(splitlist_read) == 8:
                if splitlist_read[2] == "active":
                    address = splitlist_read[1]  # 第2个为矿工地址
                    addresslist_new.append(address)
                elif splitlist_read[2] == "-":
                    if "minerId:" in splitlist_read[0]:  # 第1个为矿机id
                        minerid = splitlist_read[0].split(":")[1]
                    else:
                        minerid = "default"
                    nopaid_1miner = float(splitlist_read[5])  # 第6个为单机nopaid shares
                    totalpaid = totalpaid + nopaid_1miner
                    minerlist_new.append([address, minerid])
                    minerlist.append([address, minerid, nopaid_1miner])
        operation_log("The list of mine machines has been completed, with a total of %s mines." % (len(minerlist)))
        minerinfo = []

        # print(minerlist)
        for elt in minerlist:
            if totalpaid != 0:
                hashrate_1miner = round(elt[2] / totalpaid * hashrate_pool * 1000 * 1000, 2)  # 单机算力，单位为MH
                minerinfo.append([elt[0], elt[1], hashrate_1miner])  # [[address, minerid, hashrate_1miner]]
            else:
                minerinfo.append([elt[0], elt[1], 0])
        operation_log("Calculation of mine conversion")
        # 清空数据表tb_minerinfo的记录
        sql = "DELETE FROM tb_minerinfo"
        SqlModel.mysql_com(sql_str=sql)
        operation_log("Emptying the record of data table tb_minerinfo")
        # tb_minerinfo
        sql = "INSERT INTO tb_minerinfo(address, minerid, hashrate_1miner) VALUES(%s, %s, %s)"  # 不论是什么数据类型，占位符都用%s
        # print("minerinfo",minerinfo)
        operation_log("Insert records into tb_minerinfo")
        if len(minerinfo) > 1:
            SqlModel.put_info_by_sql_many(sql_str=sql, datalist=minerinfo)
        else:
            SqlModel.put_info_by_sql(sql_str=sql, data=minerinfo[0])  # (mineraddress, minerid, hashrate_1miner)

        addresscount = len(addresslist_new)  # 6.矿池矿工数量
        minercount = len(minerinfo)  # 7.矿池矿机数量
        operation_log("The number of miners %s and the number of mine machines %s can be obtained." % (addresscount, minercount))
        return minercount, addresscount, minerlist_new, addresslist_new, minerinfo
    else:
        end_exit(5)
def update_offlineminer(minerlist_old,minerlist_new,minerlist_offeline):
    # 对比出需写入矿机离线表tb_mineroffline的矿机
    operation_log("Update offline list of mine machines Start")
    minerlist_cmp = []
    if len(minerlist_old) > 0 and len(minerlist_new) > 0:  # 新旧矿机列表对比出离线矿机清单minerlist_cmp列表
        for elt in minerlist_old:
            if not (elt in minerlist_new):
                minerlist_cmp.append(elt)

    if len(minerlist_offeline) > 0 and len(minerlist_cmp) > 0:  # 检查原有离线矿机
        for elt in minerlist_offeline:
            if elt in minerlist_cmp:  # 继续离线，保留最早离线时间
                minerlist_cmp.remove(elt)
            if elt in minerlist_new:  # 重新上线，需在离线矿机tb_mineroffline表删除
                sql = "DELETE FROM tb_mineroffline WHERE address=%s AND minerid=%s"  # 删除记录
                SqlModel.mysql_com(sql_str=sql)

    for elt in minerlist_cmp:
        elt.insert(0, thistime)  # 加入时间字段[timefield,address,minerid]

    sql = "DELETE FROM tb_mineroffline WHERE timefield NOT BETWEEN (NOW() - interval 24 hour) AND now()"  # 删除超过24小时的离线机器记录
    SqlModel.mysql_com(sql_str=sql)

    sql = "INSERT INTO tb_mineroffline(timefield, address, minerid) VALUES(%s, %s, %s)"  # 不论是什么数据类型，占位符都用%s
    SqlModel.mysql_com(sql_str=sql)
    operation_log("Update offline list of mine machines End")

def poolinsert(thistime, hashrate_net, hashrate_pool, blockhigh, mainblockhigh, diff, minercount, addresscount):
    poolinfolist = [thistime, hashrate_net, hashrate_pool, blockhigh, mainblockhigh, diff, minercount, addresscount]
    # print(poolinfolist)
    # tb_poolinfo
    sql = "INSERT INTO tb_poolinfo(timefield, hashrate_net, hashrate_pool, blockhigh, mainblockhigh, diff, minercount, addresscount) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
    SqlModel.put_info_by_sql(sql_str=sql, data=poolinfolist)
    operation_log("Insert records into tb_poolinfo")

def choushui(Master_address,Standby_address,today_UTC):
    ###########################################################################写入tb_blockinfo################################################################################
    # 查今日出块数量
    operation_log("Start calculating today's pumping")
    blockcount_today = 0  #定义变量今日出块数
    sql = "SELECT COUNT(*) FROM tb_payoutinfo WHERE address = %s AND DATE_FORMAT(timefield,'%%Y-%%m-%%d') = DATE_FORMAT(%s,'%%Y-%%m-%%d')"

    result = SqlModel.rows_info_by_data(sql, (Master_address, today_UTC))
    if result == 1:
        retup = SqlModel.get_info_by_sql_data(sql, (Master_address, today_UTC))
        if retup[0] != None:
            blockcount_today = retup[0]
        else:
            blockcount_today = 0
    operation_log("Main address today pumping calculation")
    sql = "SELECT COUNT(*) FROM tb_payoutinfo WHERE address = %s AND DATE_FORMAT(timefield,'%%Y-%%m-%%d') = DATE_FORMAT(%s,'%%Y-%%m-%%d')"
    result = SqlModel.rows_info_by_data(sql, (Standby_address, today_UTC))
    if result == 1:
        retup = SqlModel.get_info_by_sql_data(sql, (Standby_address, today_UTC))
        if retup[0] != None:
            blockcount_today = blockcount_today + retup[0]
        else:
            blockcount_today = blockcount_today + 0
    operation_log("Standby address today pumping calculation")
    # tb_blockinfo
    sql = "REPLACE INTO tb_blockinfo(timefield, blockcount) VALUES(%s, %s)"  # 有则更新，无则插入
    para = [today_UTC, blockcount_today]
    SqlModel.mysql_com_data(sql_str=sql, data=para)
    operation_log("Write today's pumping %s results into database"%(str(blockcount_today)))
def miner_query():
    # 查个人矿机列表
    sql = "SELECT address, minerid FROM tb_minerinfo "
    operation_log("Check personal mine list")
    recordCnt = SqlModel.rows_info_by_sql(sql_str=sql)  # 返回本次操作影响的记录数
    operation_log("Personal miner list is querying to %s rows."%(recordCnt))
    #Personal miner list is querying to 100 rows.
    if recordCnt > 0:
        record = SqlModel.get_info_by_sql(sql_str=sql)
        operation_log("Mine list Query result output to memory")
        minerlist_old = tuple2list(record)
    else:
        minerlist_old =[]
        operation_log("The mine list query result is null and returns an empty list.")
    # print(minerlist_old)
    # 查掉线矿机列表

    sql = "SELECT address, minerid FROM tb_mineroffline "
    operation_log("Check List of drop line mining machines")
    recordCnt = SqlModel.rows_info_by_sql(sql_str=sql)  # 返回本次操作影响的记录数
    operation_log("Offline list of mine machines is querying to %s rows."%(recordCnt))
    #"Offline list of mine machines is querying to 100 rows."
    if recordCnt > 0:
        minerlist_offeline = tuple2list(SqlModel.get_info_by_sql(sql_str=sql))
        operation_log("drop line mining machines Query result output to memory")
    else:
        minerlist_offeline = []
        operation_log("The drop line mining machines query result is null and returns an empty list.")
    return minerlist_old, minerlist_offeline

def addressinfo(addresslist_new):
    ###########################################################################写入tb_addressinfo################################################################################
    # 查个人钱包地址列表
    operation_log("Check personal wallet address list")
    #addresslist_old = []
    addresslist_all = addresslist_new
    sql = "SELECT address FROM tb_addressinfo"
    recordCnt = SqlModel.rows_info_by_sql(sql)  # 返回本次操作影响的记录数
    if recordCnt > 0:
        addresslist_old = tuple2list(SqlModel.get_info_by_sql(sql))
        for elt in addresslist_old:  # 新旧地址列表对比出新增钱包地址，并追加到所有的地址列表里
            if not (elt[0] in addresslist_new):
                addresslist_all.append(elt[0])
        operation_log("The old and new address list compares the new wallet address and appends it to all address lists.")
    else:
        addresslist_old = []
    #addressinfo = []
        operation_log("Old address is empty, no new content added.")

    # print("地址池", addresslist_all)
    ##############查询全部地址24小时平均算力及最近14日收益

    sql = "SELECT address ,hashrate_24h ,payout_last14 FROM tb_addressinfo "
    # recordCnt = cursor.execute(sql)
    operation_log("Inquire all address 24 hours average calculation power and recent 14 day income")
    address_record = SqlModel.get_info_by_sql(sql)
    # print(address_record)
    address_value = {}
    for item in address_record:
        address_value[item[0]] = [item[1], item[2]]
    operation_log("The result is loaded into the dictionary.")
    # print(address_value)
    # 查询昨日及今日收益
    operation_log("Query yesterday and today's earnings")
    # print(yestoday_UTC, today_UTC)
    sql = "select  address, sum(CASE when DATE_FORMAT(timefield,'%%Y-%%m-%%d') = DATE_FORMAT('%s','%%Y-%%m-%%d') then xdagcount else 0 end ) yestoday_sum \
                                  ,sum(CASE when DATE_FORMAT(timefield,'%%Y-%%m-%%d') = DATE_FORMAT('%s','%%Y-%%m-%%d') then xdagcount else 0 end ) today_sum \
                                  FROM tb_payoutinfo  group by  address" % (yestoday_UTC, today_UTC)

    # print(sql)

    address_record = SqlModel.get_info_by_sql(sql)
    # print("pay_list", address_record)
    address_pay_value = {}

    for item in address_record:
        address_pay_value[item[0]] = [item[1], item[2]]
    operation_log("The result is loaded into the dictionary.")
    return  address_value,address_pay_value,addresslist_all
def addmatch(addrstr,address_value,address_pay_value,str_minerinfo,addressinfo):
    if len(addrstr) == 32:  # 判断是否32位的钱包地址
        # 查个人矿机数量
        minercount_person = str_minerinfo.count(addrstr)  # 将二维列表转化为字符串，然后计算包含某钱包地址字符串的个数，得出矿机数量

        # 查个人矿机的总算力
        hashrate_person = 0
        for elt in minerinfo:
            if addrstr in elt[0]:
                hashrate_person = round(hashrate_person + float(elt[2]), 2)

        # 24小时平均算力
        hashrate_24h = ""

        if addrstr in address_value.keys():

            hashrate_24h = address_value[addrstr][0] + "," + str(hashrate_person)
        else:
            hashrate_24h = str(hashrate_person)

        hashratelist = hashrate_24h.split(",")
        if len(hashratelist) > 100:
            find_index = hashrate_24h.find(",", 1)  # 从下标1开始查找
            hashrate_24h = hashrate_24h[find_index + 1:]

        # 查最近14日收益
        payout_last14 = ""

        if addrstr in address_value.keys():
            # result = tuple2list(cursor.fetchall())
            payout_last14 = address_value[addrstr][1]

        if len(payout_last14.split(",")) != 14:
            counter = 2
            while counter <= 14:  # 除昨天的13日，如"1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0"
                dt_temp = today_UTC - datetime.timedelta(days=counter)
                if payout_last14 == "":
                    payout_last14 = str(dt_temp) + ":0"
                else:
                    payout_last14 = str(dt_temp) + ":0," + payout_last14
                counter = counter + 1

        if str(yestoday_UTC) not in payout_last14:  # 判断昨天是否在过去的收益中，不在则查询添加
            payout_yestoday = 0

            if addrstr in address_pay_value.keys():
                payout_yestoday = address_pay_value[addrstr][0]
                # print("昨日收益",payout_yestoday)
            payout_last14 = payout_last14 + "," + str(yestoday_UTC) + ":" + str(payout_yestoday)
            if len(payout_last14.split(",")) > 14:
                index = payout_last14.find(",", 1)  # 从下标1开始查找
                payout_last14 = payout_last14[index + 1:]

        # 查个人今日收益
        payout_today = 0

        if addrstr in address_pay_value.keys():
            payout_today = address_pay_value[addrstr][1]
        addressinfo.append([addrstr, minercount_person, hashrate_person, hashrate_24h, payout_today, payout_last14])
        #addrstr_list = [addrstr, minercount_person, hashrate_person, hashrate_24h, payout_today, payout_last14]
        #return addrstr_list


def address_judge(minerinfo,addresslist_all,address_value,address_pay_value,yestoday_UTC):
    addressinfo = []
    str_minerinfo = str(minerinfo)
    operation_log("There are %s addresses.Start Address cycle" % (len(addresslist_all)))
    #p = Pool(20)
    for addrstr in addresslist_all:
        # print(addrstr)
        addmatch(addrstr, address_value, address_pay_value, str_minerinfo, addressinfo)
        #p.apply_async(addmatch, args=(addrstr, address_value, address_pay_value, str_minerinfo, addressinfo,))
        #addrstr_list = addmatch(addrstr, address_value, address_pay_value, str_minerinfo)
        #addressinfo.append(addrstr_list)
    #p.close()
    #p.join()
    operation_log("End Address cycle")
    return addressinfo


def insert_ioo(addressinfo):
    sql = "INSERT INTO tb_addressinfo(address, minercount, hashrate, hashrate_24h, payout_today, payout_last14) VALUES(%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE \
                           minercount = values(minercount), hashrate = values(hashrate), hashrate_24h = values(hashrate_24h), payout_today = values(payout_today), payout_last14 = values(payout_last14)"
    try:

        if len(addressinfo) > 1:
            SqlModel.put_info_by_sql_many(sql, addressinfo)
        else:
            SqlModel.put_info_by_sql(sql, addressinfo[0])
        operation_log("Insert tb_addressinfo success")
    except:
        info = sys.exc_info()
        operation_log("Insert tb_addressinfo failure")
        operation_log("Exception message %s"%(info))
        operation_log("Capture abnormality %s"%(info[0]+":"+info[1]))
        #print(info[0], ":", info[1])  # 捕获异常
def clear_mysqldata():
    operation_log("Start clearing MySQL redundant data")
    ###########################################################################清除MYSQL冗余数据################################################################################
    dt = today_UTC - datetime.timedelta(days=15)  # 15
    sql = "DELETE FROM tb_poolinfo WHERE DATE_FORMAT(timefield,'%%Y-%%m-%%d') < DATE_FORMAT(%s,'%%Y-%%m-%%d')"
    SqlModel.put_info_by_sql(sql, dt)

    dt = today_UTC - datetime.timedelta(days=3)  # 3
    sql = "DELETE FROM tb_payoutinfo WHERE DATE_FORMAT(timefield,'%%Y-%%m-%%d') < DATE_FORMAT(%s,'%%Y-%%m-%%d')"
    SqlModel.put_info_by_sql(sql, dt)
    operation_log("Clear MySQL redundant data complete")

def end_exit(tt):# 异常退出情况，后续可根据情况添加。
    if tt == 1:
        os.remove(txtdir + "pylock.txt")  # 任务执行完成删除锁文件
        operation_log("Task execution completed, deleted files pylock.txt")
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()
    elif tt == 2 :
        operation_log("Failed to create file pylock.txt")
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()
    elif tt == 3 :
        operation_log("%s does not exist in %s directory" % ("line_number.txt", txtdir))
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()
    elif tt == 4 :
        operation_log("--------------------------Demarcation line Start----------------------------------------")
        operation_log("pylock.txt already exists in %s directory" % (txtdir))
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()

    elif tt == 5 :

        operation_log("%s does not exist in %s directory" % ("miners.txt", txtdir))
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()
    elif tt == 6 :

        operation_log("%s does not exist in %s directory" % ("stats.txt", txtdir))
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()

    elif tt == 7:
        operation_log("xdag.log does not exist in %s directory" % (txtdir))
        operation_log("--------------------------Demarcation line End----------------------------------------")
        exit()
if __name__ == '__main__':

    ##时间格式，提取当前系统时间，待下面各模块引用
    time_now = int(time.time())  # 获取当前时间
    time_local = time.localtime(time_now)  # 转换成localtime
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的字符串时间格式(2016-05-09 08:00:00)
    time_str_format = time.strftime("%Y%m%d%H%M%S", time_local)
    thistime = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')  # 转化成真正的时间格式
    today_UTC = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').date()  # 转化成日期格式(2016-05-09)
    yestoday_UTC = today_UTC - datetime.timedelta(days=1)
    # ---------------------------------------------分界线-----------------------------------------
    #公共变量，提前定义待模块引用
    filter_str = ":MESS]  Xfer : from"
    Master_address = "sMJroMaAcEWgkhl7ht7IIZMMUE7jJ+B/"    #抽水地址1
    Standby_address = "m4R6GV3gdGVCcXzvHnfWS35FfRJNgdfA"   #抽水地址2
    txtdir = exe_path + "\\"  #运行环境地址
    xdagdir = exe_path + "\\"  #运行环境地址
    SqlModel = SqlModel() #引用查询模块
    #---------------------------------------------分界线-----------------------------------------

    if os.path.exists(txtdir + "pylock.txt"):  ##先判断是否有锁文件在，如在则不运行，记录log然后退出。
        end_exit(4)
    else:
        if makeNewFile(txtdir , "pylock.txt"):  # 新建锁判断文件
            last_lnum = mark_line(txtdir,"line_number.txt") #读取上次读取行数
            xdag_read(xdagdir,txtdir,filter_str,last_lnum)  #xdag文件读取
            hashrate_net, hashrate_pool, blockhigh, mainblockhigh, diff = stats(txtdir + "stats.txt") #stats文件读取

            minerlist_old, minerlist_offeline = miner_query()  #矿工列表及离线矿机列表
            minercount, addresscount ,minerlist_new,addresslist_new,minerinfo=read_miner_txt(txtdir + "miners.txt")  #矿池矿工列表 矿池矿机列表
            poolinsert(thistime, hashrate_net, hashrate_pool, blockhigh, mainblockhigh, diff, minercount, addresscount) #导入数据库

            update_offlineminer(minerlist_old, minerlist_new, minerlist_offeline)  #更新离线矿机列表
            choushui(Master_address, Standby_address, today_UTC)  #计算两个地址抽水数
            address_value, address_pay_value,addresslist_all = addressinfo(addresslist_new) #地址列表及收益
            addressinfo = address_judge(minerinfo, addresslist_all, address_value, address_pay_value, yestoday_UTC)  #地址循环
            insert_ioo(addressinfo) #地址循环后，结果导入数据库。
            ##############################
            clear_mysqldata() #删除数据库冗余数据
            end_exit(1)
        else:
            end_exit(2)







