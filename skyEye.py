# -*- coding: utf-8 -*-
# @Author: Longda
# @Date:   2022-07-01 16:56:38
# @Last Modified by:   longda
# @Last Modified time: 2022-07-03 03:47:18
import requests
import json
import time
import sys
import os
import argparse
from pyquery import PyQuery as pq
from urllib.parse import quote
requests.packages.urllib3.disable_warnings()

# 写token
def writeToken(token):
	with open("./config.yaml","w",encoding='utf-8') as f:
		f.writelines(token)

# 获取token
def getToken():
	with open("./config.yaml","r",encoding='utf-8') as f:
		token = f.readlines()[0].strip()
		#判断token是否有效
		flag = checkToken(token)
		if flag:
			return token
		else:
			print("[!] token已经过期，请重新指定token或写到config.yaml")
			while True:
				token = input("$ Input Token > ")	
				if "auth_token=" not in token:
					token = "auth_token="+token
				if token=='auth_token=' or checkToken(token)==False:
					continue
				else:
					break
			return token

#验证token有效型
def checkToken(token):
	try:
		#判断token是否有效
		header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
		"Referer":"https://www.tianyancha.com/",
		"Cookie":token}
		url = f"https://www.tianyancha.com/pagination/wechat.xhtml?id=686992107&pn=1"
		res = requests.get(url=url, headers=header, verify=False)
		if res.status_code==200:
			return True
		else:
			return False
	except Exception:
		return False

def outPrint(results):
	if results:
		for item in results:
			print("  ",item)

# 处理结果函数
def dealResult(results):
	temp = []
	for item in results:
		if isinstance(item,list):
			if item[0]!="" and item[1]!="" and item[2]!=None:

				temp.append(item)
		elif isinstance(item,str):
			if item!=" ":
				temp.append(item)
	return temp

# 获取公司Gid/公司全称
def getGId(companyName):
	try:
		company = ""
		gid = ""
		header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
		"Referer":"https://www.tianyancha.com/",
		"Cookie":"aliyungf_tc=ebac36043be5d3ff8bad0668574eee72c6d1862286e3f6aff8bef0358184db6f"}
		url = f"https://www.tianyancha.com/search?key={quote(companyName)}"
		html = requests.get(url=url, headers=header, verify=False).text
		doc = pq(html)
		aDivs = doc('.index_list-wrap___axcs .index_name__qEdWi').items()
		if aDivs:
			div = list(aDivs)
			if div:
				url = div[0].find('a').attr("href")
				company = div[0].find('a span').text()
				gid = url.split("/")[-1]
		while True:
			if company=='' or gid=='':
				company = input("$ Input company > ")
				getGId(company)
			else:
				break
		return company,gid
	except Exception as e:
		return company,gid
	except KeyboardInterrupt:
		exit()

# 获取控股子公司
def subsidiary(gid,rate,delay):
	try:
		myDatas = []
		if rate<90:
			rate = "50"
		elif rate<100:
			rate = "90"
		else:
			rate = "100"
		rateList = {"50":"4","90":"5","100":"6"}
		header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
		"Referer":"https://www.tianyancha.com/",
		"content-type":"application/json",
		"version":"TYC-Web",
		"x-tycid":"1edbe4006ea111eca2d6fdac49e21176",
		"Cookie":"aliyungf_tc=ebac36043be5d3ff8bad0668574eee72c6d1862286e3f6aff8bef0358184db6f"}
		url = f"https://capi.tianyancha.com/cloud-company-background/company/investListV2?_={int(round(time.time() * 1000))}"
		data = {"gid":gid,"pageSize":10,"pageNum":1,"province":"-100","percentLevel":rateList[rate],"category":"-100"}
		resData = requests.post(url=url,json=data,headers=header,verify=False).json()["data"]
		total = resData['total']
		results = resData['result']
		#先获取第一页
		if results:
			for item in results:
				myDatas.append([item['name'],item['percent'],item['regStatus']])
		#页数
		if total%10==0:
			pageNums = total//10
		else:
			pageNums = total//10 + 1
		#遍历页数获取	
		if pageNums > 2:
			for page in range(2,pageNums+1):
				time.sleep(delay/10)
				data = data = {"gid":gid,"pageSize":10,"pageNum":page,"province":"-100","percentLevel":rateList[rate],"category":"-100"}
				resData = requests.post(url=url,json=data,headers=header,verify=False).json()["data"]
				results = resData['result']
				if results:
					for item in results:
						myDatas.append([item['name'],item['percent'],item['regStatus']])		
		return myDatas
	except Exception as e:
		return myDatas
	except KeyboardInterrupt:
		exit()

# get ICP(备案)
def getICP(company,gid,token,delay):
	try:
		ICPData = []
		page = 1
		header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
		"Referer":"https://www.tianyancha.com/",
		"Cookie":token}
		url = f"https://www.tianyancha.com/pagination/icp.xhtml?id={gid}&pn={page}"
		res = requests.get(url=url, headers=header, verify=False)
		html = res.text
		doc = pq(html)
		Trs = doc('.table tbody tr').items()
		if Trs:
			for item in Trs:
				ym = item.find('td:nth-child(5)').text()
				icpNum = item.find('td:nth-child(6) span').text()
				ICPData.append([ym,icpNum])
			if ICPData:
				print("\n[+] 开始获取备案信息：",company)
				outPrint(ICPData)
		while True:
			time.sleep(delay/10)
			tempData = []
			tempData0 = ICPData
			if len(tempData0)>=10:
				page += 1
				url = f"https://www.tianyancha.com/pagination/icp.xhtml?id={gid}&pn={page}"
				try:
					html = requests.get(url=url, headers=header, verify=False).text
					doc = pq(html)
					Trs = doc('.table tbody tr').items()
					if Trs:
						for item in Trs:
							ym = item.find('td:nth-child(5)').text()
							icpNum = item.find('td:nth-child(6) span').text()
							tempData.append([ym,icpNum])
						outPrint(tempData)
						tempData0 = tempData
						ICPData += tempData
						continue
				except Exception as e:
					break
			else:
				break
		return ICPData
	except Exception as e:
		return ICPData
	except KeyboardInterrupt:
		exit()

# get 微信公众号 (公众号/微信号/二维码)
def getWechat(company,gid,token,delay):
	wechatData = []
	page = 1
	header = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
	"Referer":"https://www.tianyancha.com/",
	"Cookie":token}
	url = f"https://www.tianyancha.com/pagination/wechat.xhtml?id={gid}&pn={page}"
	try:
		html = requests.get(url=url, headers=header, verify=False).text
		doc = pq(html)
		Trs = doc('.table tbody tr').items()
		if Trs:
			for item in Trs:
				gzh = item.find('td:nth-child(2) table tr td:nth-child(2) span').text()
				wxh = item.find('td:nth-child(3) span').text()
				ewm = item.find('td:nth-child(4) img').attr("data-src")
				# print("  ",[gzh,wxh,ewm])
				wechatData.append([gzh,wxh,ewm])
			wechatData = dealResult(wechatData)
			if wechatData:
				print("\n[+] 开始获取微信公众号信息:",company)
				outPrint(wechatData)
		#循环查找下一页
		while True:
			time.sleep(delay/10)
			tempData = []
			tempData0 = wechatData
			if len(tempData0)>=10:
				page += 1
				url = f"https://www.tianyancha.com/pagination/wechat.xhtml?id={gid}&pn={page}"
				try:
					html = requests.get(url=url, headers=header, verify=False).text
					doc = pq(html)
					Trs = doc('table tbody tr').items()
					if Trs:
						for item in Trs:
							gzh = item.find('td:nth-child(2) table tr ta:nth-child(2) span').text()
							wxh = item.find('td:nth-child(3) span').text()
							ewm = item.find('td:nth-child(4) img').attr("data-src")
							# print("  ",[gzh,wxh,ewm])
							tempData.append([gzh,wxh,ewm])
						tempData = dealResult(tempData)
						outPrint(wechatData)
						tempData0 = tempData
						wechatData += tempData
						continue
					else:
						break
				except Exception as e:
					break
			else:
				break
		# print(wechatData)
		# outPrint(wechatData)
		return wechatData
	except Exception as e:
		return wechatData
	except KeyboardInterrupt:
		exit()

#get app
def getApp(company,gid,token,delay):
	appData = []
	page = 1
	header = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
	"Referer":"https://www.tianyancha.com/",
	"Cookie":token}
	url = f"https://www.tianyancha.com/pagination/product.xhtml?id={gid}&pn={page}"
	try:
		html = requests.get(url=url, headers=header, verify=False).text
		doc = pq(html)
		Trs = doc('.table tbody tr').items()
		if Trs:
			for item in Trs:
				appData.append(item.find('td:nth-child(3) span').text())
			appData = dealResult(appData)
			if appData:
				print("\n[+] 开始获取app信息:",company)
				outPrint(appData)
		while True:
			time.sleep(delay/10)
			tempData = []
			tempData0 = appData
			if len(tempData0)>=10:
				page += 1
				url = f"https://www.tianyancha.com/pagination/product.xhtml?id={gid}&pn={page}"
				try:
					html = requests.get(url=url, headers=header, verify=False).text
					doc = pq(html)
					Trs = doc('.table tbody tr').items()
					if Trs:
						for item in Trs:
							tempData.append(item.find('td:nth-child(3) span').text())
						tempData = dealResult(tempData)
						outPrint(appData)
						tempData0 = tempData
						appData += tempData
						continue
				except Exception as e:
					break
			else:
				break
		# print(appData)
		return appData
	except Exception as e:
		return appData
	except KeyboardInterrupt:
		exit()

# get Subsidiary（控股子公司）
def getAllSubsidiary(company,gid,deep,rate,delay):
	try:
		print("\n[+] 开始获取控股子公司信息:",company)
		myDatas = [[company,'100%','存续（在营、开业、在册)']]
		allKongGu = myDatas
		#一级控股
		index = 1
		temp = subsidiary(gid,rate,delay)
		if temp:
			print(f" [*] 控股< {index} >级子公司:")
			outPrint(temp)
			allKongGu += temp
		while (index<deep):
			index += 1
			if temp:
				temp1 = []
				for item in temp:
					company,gid = getGId(item[0])
					temp0 = subsidiary(gid,rate,delay)
					if temp0:
						temp1 += temp0
				if temp1:
					print(f" [*] 控股< {index} >级子公司:")
					outPrint(temp1)
				temp = temp1
				#添加到总数据
				allKongGu += temp
			else:
				break
		return allKongGu
	except Exception as e:
		return allKongGu
	except KeyboardInterrupt:
		exit()

def re_parser():
	helpData = "skyEye是一个利用《天眼查》来爬取企业的控股子公司、ICP备案信息、微信公众号、企业APP等信息的资产收集工具,某些功能需要《天眼查》登录后的auth_token,第一次运行程序会生成配置文件：config.yaml,可在其中配置auth_token。"
	parser = argparse.ArgumentParser(add_help=True,description=helpData)
	print()
	parser.add_argument("-r", "--rate", type=int, help="控股比例,默认为50 [50/90/100]",default=50)
	parser.add_argument("-d", "--deep", type=int, help="控股子公司递归查询深度,默认n级 [1/2/3/.../n]", default=100)
	parser.add_argument("-m", "--mode", type=str, help="指定搜索模块，默认all(多个以[,]隔开) [subCompany/icp/wechat/app]", default='all')
	parser.add_argument("-s", "--delay", type=int, help="请求延迟，防止被ban,默认1秒", default=1)
	parser.add_argument("-t", "--token", type=str, help="指定token,似乎有20天+的有效期,一次指定短期可用,默认空", default='')
	parser.add_argument("-u", "--target", type=str, help="查询目标名称(必须指定,可简称/关键字)")
	parser.add_argument("-ci", "--childICP", type=bool, help="是否查询控股子公司ICP备案信息,默认False", default=False)
	parser.add_argument("-cw", "--childWechat", type=bool, help="是否查询控股子公司微信公众号信息,默认False", default=False)
	parser.add_argument("-ca", "--childAPP", type=bool, help="是否查询控股子公司APP信息,默认False", default=False)
	parser.add_argument("-cl", "--childALL", type=bool, help="是否查询控股子公司所有(icp、公众号、app)信息,默认False", default=False)
	args = parser.parse_args()
	return args

# 主函数
def main():
	try:
		if len(sys.argv) <= 1:
			sys.argv.append('-h')
		if not os.path.exists('./config.yaml'):
			writeToken("auth_token=xxxxxxxxxx")
		args = re_parser()
		company,gid = getGId(args.target)
		print(f"[+] 当前公司信息：{company}, GID：{gid}")
		flag = input("$ continue(Y/N) > ")
		ICP = []
		wechat = []
		app = []
		AllSubsidiary = []
		if flag.upper() == 'Y' or flag=='':
			if args.mode == 'all':
				# subCompany
				AllSubsidiary += getAllSubsidiary(company,gid,args.deep,args.rate,args.delay)
				#token
				if args.token=='':
					token = getToken()
				else:
					while True:
						if 'auth_token=' not in args.token:
							token = "auth_token="+args.token
						if not checkToken(token):
							token = input("Input Token > ")
							continue
						else:
							break
					writeToken(token)
				#all
				if args.childALL:
					for item in AllSubsidiary:
						company,gid = getGId(item[0])
						ICP += getICP(company,gid,token,args.delay)
					for item in AllSubsidiary:
						company,gid = getGId(item[0])
						wechat += getWechat(company,gid,token,args.delay)
					for item in AllSubsidiary:
						company,gid = getGId(item[0])
						app += getApp(company,gid,token,args.delay)
				else:
					ICP += getICP(company,gid,token,args.delay)
					wechat += getWechat(company,gid,token,args.delay)
					app += getApp(company,gid,token,args.delay)
				#ICP
				if args.childICP:
					for item in AllSubsidiary[1:]:
						company,gid = getGId(item[0])
						ICP += getICP(company,gid,token,args.delay)
						app += getApp(company,gid,token,args.delay)
				#wechat
				if args.childWechat:
					for item in AllSubsidiary[1:]:
						company,gid = getGId(item[0])
						wechat += getWechat(company,gid,token,args.delay)
				#app
				if args.childAPP:
					for item in AllSubsidiary[1:]:
						company,gid = getGId(item[0])
						app += getApp(company,gid,token,args.delay)
			else:
				if 'subCompany' in args.mode.split(","):
					AllSubsidiary += getAllSubsidiary(company,gid,args.deep,args.rate,args.delay)

				if 'icp' in args.mode.split(","):
					if args.token=='':
						token = getToken()
					else:
						if 'auth_token=' not in args.token:
							token = "auth_token="+args.token
						if not checkToken(token):
							print("[!] 指定token无效")
							while True:
								token = input("$ Input Token > ")
								if 'auth_token=' not in args.token:
									token = "auth_token="+args.token
								if not checkToken(token):
									continue
								else:
									break
						writeToken(token)
					ICP += getICP(company,gid,token,args.delay)

				if 'wechat' in args.mode.split(","):
					if args.token=='':
						token = getToken()
					else:
						if 'auth_token=' not in args.token:
							token = "auth_token="+args.token
						if not checkToken(token):
							print("[!] 指定token无效")
							while True:
								token = input("$ Input Token > ")
								if 'auth_token=' not in args.token:
									token = "auth_token="+args.token
								if not checkToken(token):
									continue
								else:
									break
						writeToken(token)
					wechat += getWechat(company,gid,token,args.delay)

				if 'app' in args.mode.split(","):
					if args.token=='':
						token = getToken()
					else:
						if 'auth_token=' not in args.token:
							token = "auth_token="+args.token
						if not checkToken(token):
							print("[!] 指定token无效")
							while True:
								token = input("$ Input Token > ")
								if 'auth_token=' not in args.token:
									token = "auth_token="+args.token
								if not checkToken(token):
									continue
								else:
									break
						writeToken(token)
					app += getApp(company,gid,token,args.delay)
		else:
			exit()
		return AllSubsidiary,ICP,wechat,app
	except Exception as e:
		print("Error：",e)
		exit()
	except KeyboardInterrupt as e:
		exit()

if __name__=='__main__':
	# subsidiary('中国电信集团有限公司')
	# main('北京百度网讯科技有限公司')
	# getICP('中国电信集团有限公司')
	# getWechat("上海拉扎斯信息科技有限公司")
	# getApp("上海拉扎斯信息科技有限公司")
	# getICP('北京百度网讯科技有限公司')
	# print(re_parser())
	# print(2/10000)
	main()
	
