#!/usr/bin/env python
#-*- coding: utf8 -*-

__author__ = 'RickyShilx'


def dec255_to_bin8(dec_str):
    bin_str = bin(int(dec_str,10)).replace("0b",'')
    headers = ['', '0', '00', '000', '0000', '00000', '000000', '0000000']
    if len(bin_str)<8:
        bin_str = headers[8-len(bin_str)]+bin_str
    return bin_str

def int_to_bin32(int_str):
    bin_str = bin(int_str).replace("0b",'')
    while len(bin_str)<32:
        bin_str = "0"+bin_str
    return bin_str

def ipstr_to_binstr(ip):
    a,b,c,d = ip.split(".")
    ipbin = dec255_to_bin8(a)+dec255_to_bin8(b)+dec255_to_bin8(c)+dec255_to_bin8(d)
    return ipbin

def binstr_to_ipstr(binstr):
    return str(int(binstr[0:8], base=2))+"."+str(int(binstr[8:16], base=2))+"."+str(int(binstr[16:24], base=2))+"."+str(int(binstr[24:32], base=2))

def ipmask_to_iprange(ipmask):
    ip, mask = ipmask.split("/")
    ipbin = ipstr_to_binstr(ip)
    ipnet_bin = ipbin[0:int(mask)]+ipbin[int(mask):32].replace("1", "0")
    ipstart_bin = bin(int(ipnet_bin, base=2)+1).replace("0b", '')
    ipend_bin = bin(int(ipnet_bin, base=2)+pow(2,32-int(mask))-2).replace("0b", '')
    ipbro_bin = ipbin[0:int(mask)]+ipbin[int(mask):32].replace("0", "1")

    ipnet = binstr_to_ipstr(ipnet_bin)
    ipstart = binstr_to_ipstr(ipstart_bin)
    ipend = binstr_to_ipstr(ipend_bin)
    ipbro = binstr_to_ipstr(ipbro_bin)

    return {"input":ip+"/"+mask, "netaddress":ipnet, "distribute":ipstart+" - "+ipend, "broadcast":ipbro}


def iprange_to_ipmask_core(ipstart, ipend):
    ipseg_set = []

    ipstart_bin = ipstr_to_binstr(ipstart)
    ipend_bin = ipstr_to_binstr(ipend)

    min_mask = -1
    for i in range(1, 33, 1):
        if ipstart_bin[i-1] != ipend_bin[i-1]:
            min_mask = i-1; break

    if min_mask == -1:
        ipseg_set.append(ipstart+"/32")
        return ipseg_set

    max_mask = 33
    for i in range(min_mask+1, 33, 1):
        if ipstart_bin[i-1] == "1":
            max_mask = i; break

    if max_mask != 33:
        seg_head_start = ipstart
        seg_head_end = binstr_to_ipstr(ipstart_bin[0:(max_mask)]+ipstart_bin[(max_mask-1):32].replace("0", "1"))
        ipseg_set.extend(iprange_to_ipmask_core(seg_head_start, seg_head_end))

    one_end = 33
    for i in range(min_mask, 33, 1):
        if ipend_bin[i-1] == "0":
            one_end = i; break

    if one_end != 33:
        seg_end_start = binstr_to_ipstr(ipstart_bin[0:min_mask]+"1"+(ipstart_bin[(min_mask+1):32].replace("1", "0")))
        seg_end_end = ipend
        ipseg_set.extend(iprange_to_ipmask_core(seg_end_start, seg_end_end))

        if max_mask==33:
            seg_start = binstr_to_ipstr(ipstart_bin)
            seg_mask = min_mask+1
            ipseg_set.append(seg_start+"/"+str(seg_mask))
        else:
            seg_start_bin_base = ipstart_bin[0:int(min_mask)]+ipstart_bin[int(min_mask):32].replace("1", "0")
            for j in range(min_mask+2, max_mask, 1):
                seg_start_bin = int_to_bin32(int(seg_start_bin_base,base=2)+pow(2, 32-j))
                seg_start = binstr_to_ipstr(seg_start_bin)
                seg_mask = j

                ipseg_set.append(seg_start+"/"+str(seg_mask))
    else:
        if max_mask==33:
            seg_start = binstr_to_ipstr(ipstart_bin)
            seg_mask = min_mask
            ipseg_set.append(seg_start+"/"+str(seg_mask))
        else:
            seg_start_bin_base = ipstart_bin[0:int(min_mask)]+ipstart_bin[int(min_mask):32].replace("1", "0")
            for k in range(min_mask+1, max_mask, 1):
                seg_start_bin = int_to_bin32(int(seg_start_bin_base,base=2)+pow(2, 32-k))
                seg_start = binstr_to_ipstr(seg_start_bin)
                seg_mask = k

                ipseg_set.append(seg_start+"/"+str(seg_mask))

    return ipseg_set


def iprange_to_ipmask(ipstart, ipend):
    ipseg_set = iprange_to_ipmask_core(ipstart, ipend)

    new_ipseg_set = []
    for seg in ipseg_set:
        ip,mask = seg.split("/")
        ipbin = ipstr_to_binstr(ip)
        new_ipseg_set.append(ipbin+"-"+mask)

    new_ipseg_set = sorted(new_ipseg_set, key=str.lower)

    ipseg_set = []
    for newseg in new_ipseg_set:
        ipbin,mask = newseg.split("-")
        ipseg_set.append(binstr_to_ipstr(ipbin)+"/"+mask)

    return {"ipstart":ipstart, "ipend":ipend, "ipmask_set":ipseg_set}

def iprange_to_ipmask_range(ipseg):
    ipstart, ipend = ipseg.replace(" ","").split("-")
    return iprange_to_ipmask(ipstart, ipend)


if __name__ == '__main__':

    """
    ipseg = ipmask_to_iprange("172.16.2.96/26")

    print u"输入的 IP：\t",ipseg["input"]
    print u"网络地址：\t",ipseg["netaddress"]
    print u"可分配地址：\t",ipseg["distribute"]
    print u"广播地址：\t",ipseg["broadcast"]
    """

    """
    ipmask_set = iprange_to_ipmask_range("10.20.41.5-10.20.41.33")
    print "----------------------"

    print u"输入的网段：\t",ipmask_set["ipstart"],"-",ipmask_set["ipend"]
    for ipmask in ipmask_set["ipmask_set"]:
        print ipmask
    """

    #"""
    ipseg_str = "10.20.40.2-10.20.41.49;10.20.41.5-10.20.41.33;10.20.50.2-10.20.50.12;10.20.64.2-10.20.64.18;10.20.64.20-10.20.64.23;10.4.254.10-10.4.254.20;10.4.254.23-10.4.254.24;10.4.254.27-10.4.254.31;10.4.254.72-10.4.254.74;10.5.240.2-10.5.240.14;"
    ipseg_str = ipseg_str.replace("\s", "")
    ipseg_set = []
    if "," in ipseg_str:
        ipseg_set = ipseg_str.split(",")
    elif ";" in ipseg_str:
        ipseg_set = ipseg_str.split(";")
    else:
        ipseg_set = ipseg_str.split(" ")

    for ipseg in ipseg_set:
        if not "-" in ipseg:
            continue
        print "---------------------",ipseg,"----------------------"
        ipmask_set = iprange_to_ipmask_range(ipseg)
        print u"输入的网段：\t",ipmask_set["ipstart"],"-",ipmask_set["ipend"]
        for ipmask in ipmask_set["ipmask_set"]:
            print ipmask
    #"""
