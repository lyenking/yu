#coding=utf-8 
#http://www.iteye.com/topic/810507 详情见该网址 
import dpkt  
import sendpkt  
from socket import inet_aton  
from time import strftime  
import socket  
import types  
import uuid  
  
#本地网关MAC地址,可以通过如下方式获取:  
#C:\Users\Administrator>arp -a  
#接口: 192.168.0.100 --- 0xb  
#  Internet 地址         物理地址                                             类型  
#  192.168.0.1    00-03-47-ca-e4-5c     动态  
MASK_MAC='1c-af-f7-c0-65-a8'  
  
  
def get_local_mac():  
    ''''' 
                获得本机Mac地址 
    '''  
    mac=uuid.uuid1().hex[-12:]  
    return '-'.join([mac[(i-1)*2:2*i] for i in range(1,7)])  
  
def send_msg(kwargs):  
    ''''' 
                发送消息,kwargs参数为一个dict对象 
    '''  
    if type(kwargs) is not types.DictType:  
        return  
    #本机ip地址  
    local_ip=kwargs.get('src',socket.gethostbyname(socket.gethostname()))  
    #转码后的源ip地址  
    src_ip=inet_aton(local_ip)  
    #转码后的目的ip地址  
    dst_ip=inet_aton(kwargs.get('dst'))  
    #本机mac地址  
    local_mac=kwargs.get('src_mac',get_local_mac())  
    #转码后的源mac地址  
    src_mac=pack_mac(local_mac)  
    #判断remote_ip和local_ip是否在同一个网段  
    #转码后的目的mac地址  
    dst_mac=pack_mac(kwargs.get('dst_mac'))\  
            if trans(local_ip)==trans(kwargs.get('dst')) else pack_mac(MASK_MAC)  
    host=kwargs.get('host',socket.gethostname())  
    user=kwargs.get('user','User')  
    msg=kwargs.get('msg','Hello')  
      
    #找到第一个网络端口，根据自己的情况修改  
    #安装了VirtualBox、VMWare或者有无线网卡的同学得自己修改下  
    device=sendpkt.findalldevs()[0]    
    #飞鸽监听本地的UDP 2425端口     
    udp=dpkt.udp.UDP(dport=2425,sport=2425)  
    #向飞鸽发送消息命令字  
    #6291458表示下线  
    #6291457表示上线  
    #288表示发送信息  
    #如果是飞秋，65664这个状态会在对方上显示为两个太阳  
    msg="1_lbt4_10#65664#%s#0#0#0:%s:%s:%s:288:%s" \  
        %(local_mac.replace('-',''),int(strftime('%m%d%H%M%S'))+100000000,user,host,msg)  
    msg=msg.encode("gbk")  
    udp.data+=msg  
    udp.ulen=len(udp)  
      
    ip=dpkt.ip.IP(src=src_ip,dst=dst_ip,data=udp,p=dpkt.ip.IP_PROTO_UDP)  
    #重新计算ip的长度,不然消息发送不出去  
    ip.len=len(ip)  
      
    ether=dpkt.ethernet.Ethernet(  
        dst=dst_mac,  
        src=src_mac,  
        type=0x0800,  
        data=ip  
    )  
    sendpkt.sendpacket(str(ether),device)  
  
def trans(ip,mask='255.255.255.0'):  
    ''''' 
          判断两个ip地址是否在同一个网段 
    '''  
    str=[]  
    ip=ip.split(".")  
    mask=mask.split(".")  
    for index,item in enumerate(ip):  
        str.append(int(item)&int(mask[index]))  
    return str  
  
  
def pack_mac(mac,pattern='-'):  
    ''''' 
         网卡地址转为以太网Mac地址 
         例如将"08-00-27-ba-f7-e5"转为"\x08\x00'\xba\xf7\xe5" 
    '''  
    mac=mac.split(pattern.lower())  
    return "".join([chr(int('0x'+x,16)) for x in mac])  
  
if __name__=="__main__":  
    s={  
       'src':'192.168.0.106',  
       'dst':'192.168.0.100',  
       'src_mac':'00-15-AF-AE-E6-C0',  
       #这个地址最好别写错，可以从飞鸽上看到好友的Mac地址  
       'dst_mac':'00-24-81-62-75-12',  
       'host':'哈哈',  
       'user':'呵呵',  
       'msg':'加班呀?'  
    }  
    send_msg(s)