# 适用平台 https://jkdk.hnust.edu.cn
# 本来想打包的

import requests
import time
import datetime

import plot_base64


def get_timestamp():
	"""
	获取毫秒级时间戳
	:return:
	"""
	t = time.time()
	t = int(round(t * 1000))
	# print(t)  # 毫秒级时间戳
	return t


# 参数列表

# 是否需要修改昨日数据（如果最后一次核酸时间与昨天的不一致，则需要修改）
need_edit = False
# 要统一修改的健康打卡的时间（全班同学都是这个时间）（need_edit == True）才生效
hssj1 = '2022-11-13'

# 记住我
remember_me = 'true'

# 密码
password = ""
# 用户名
username = ""


# 请求头
# 'X-Access-Token'是令牌


def login():
	"""
	用户登录
	用于获取X-Access-Token
	:return:
	"""
	# 时间戳
	checkkey = get_timestamp()
	url = 'https://fdys.hnust.edu.cn/sys/randomImage/'
	url = url + str(checkkey) + '?_t=' + str(int(checkkey / 1000))

	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/user/login',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
	}

	resp = requests.get(url, headers=headers)
	img = resp.json()['result']
	# 输出验证码（是base64的字符串）
	plot_base64.plot(img)
	captcha = input('请输入验证码!\n')
	url = 'https://fdys.hnust.edu.cn/sys/login'
	parameters = {
		# captcha验证码
		'captcha': captcha,
		'checkKey': checkkey,
		'password': password,
		'remember_me': remember_me,
		'username': username
	}
	hds = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		# 这个会自动计算
		'Content-Length': '104',
		'Content-Type': 'application/json;charset=UTF-8',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/user/login',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
	}

	resp = requests.post(url=url, headers=hds, json=parameters)
	print('登录信息：', resp.json())
	return resp.json()["result"]["token"]


def logout(X_Access_Token):
	"""
	退出登录
	其实这个没用
	写着玩玩
	:param X_Access_Token:
	:return:
	"""
	url = 'https://fdys.hnust.edu.cn/sys/logout'
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/wgh/nubWghJbxx/list',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Njg0MDcyNjYsInVzZXJuYW1lIjoiMTA1MDAyMyJ9.mswZogDcDPHAMt6S6mzavgTQAjsV1_5Wb3lJdgEInv8'
	}
	headers['X-Access-Token'] = X_Access_Token
	resp = requests.post(url=url, headers=headers)
	print('退出登录结果：', resp.json())


def get_list(X_Access_Token, bjid, pageNo=1, pageSize=50):
	"""
	获取本班级同学数据
	到时候更改就直接将这些数据中对应的参数（比如核酸时间）修改再依此上传即可
	:param X_Access_Token:
	:param bjid:
	:param pageNo: 默认1
	:param pageSize: 默认50（todo 需大于班级人数）
	:return:
	"""
	url = 'https://fdys.hnust.edu.cn/wgh/nubWghJbxx/list?column=createTime&order=asc&field=id,,,bjmc,zt,zrs,ytbrs,ysbxx,sfbzx,jkmllm,jkmlym,jkmlhm,hsjgYyin,hsjgYang,hsjgNot&zt=0,-1'
	# tips：这个网站的分页居然是前端实现的，也就是说你每次切换页码和更改页面大小的请求都是pageNo=1, pageSize=50，离大谱

	# 参数处理
	url = url + '&bjid=' + bjid
	url = url + '&pageNo=' + str(pageNo) + '&pageSize=' + str(pageSize)
	ymd = datetime.datetime.now().strftime('%Y-%m-%d')  # 年-月-日
	# print(ymd)
	djrq = ymd
	url = url + '&djrq=' + str(djrq)
	t = get_timestamp()
	# print(t)  # 毫秒级时间戳
	url = url + '&_t=' + str(t)

	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/wgh/nubWghJbxx/list',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Njg0MDcyNjYsInVzZXJuYW1lIjoiMTA1MDAyMyJ9.mswZogDcDPHAMt6S6mzavgTQAjsV1_5Wb3lJdgEInv8'
	}
	headers['X-Access-Token'] = X_Access_Token
	response = requests.get(url, headers=headers)
	print('本班级学生数据：', response.json())
	return response


def edit(list, hssj1, X_Access_Token):
	"""
	编辑同学信息
	暂时只支持统一修改核酸时间
	:param list:
	:param hssj1:
	:param X_Access_Token:
	:return:
	"""
	url = 'https://fdys.hnust.edu.cn/wgh/nubWghJbxx/edit'
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'Content-Length': '1496',
		'Content-Type': 'application/json;charset=UTF-8',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/wgh/nubWghJbxx/list',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Njg0MTg2MjEsInVzZXJuYW1lIjoiMTA1MDAyMyJ9.3W1lLSAh2zYx9quhbkefB98NIAp-6S2R-jJ2mRKlcQI'
	}
	headers['X-Access-Token'] = X_Access_Token
	for i in list:
		time.sleep(0.1)
		i['hssj1'] = hssj1
		response = requests.put(url=url, json=i, headers=headers)
		print('修改每条核酸时间记录的响应：', response.json())


def submit(X_Access_Token, wgid):
	"""
	提交今日数据
	:param X_Access_Token:
	:param wgid:
	:return:
	"""
	url = 'https://fdys.hnust.edu.cn/wgh/nubWghWgSubmit/submitWgDatas'
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'Content-Length': '37',
		'Content-Type': 'application/json;charset=UTF-8',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/wgh/nubWghJbxx/list',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Njg0OTMwODAsInVzZXJuYW1lIjoiMTA1MDAyMyJ9._ghTmA6BHq5e0IwRLq9lKWvQbnejnkWAg5ft-Meuaq4',
	}
	headers['X-Access-Token'] = X_Access_Token
	parameters = {
		'id': wgid,
		'zt': "2"
	}
	response = requests.put(url, headers=headers, json=parameters)
	print('提交结果：', response.json())
	return response


def copy_last(X_Access_Token, wgid):
	"""
	复制昨日数据
	:param X_Access_Token:
	:param wgid:
	:return:
	"""
	print('今日数据为空，正在复制昨日数据...\n')

	# 复制昨日数据
	parameters = {
		# 20050110
		'wgid': wgid
	}
	url = 'https://fdys.hnust.edu.cn/wgh/nubWghWgSubmit/copyWgDatas'
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/wgh/nubWghJbxx/list',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Njg0MDcyNjYsInVzZXJuYW1lIjoiMTA1MDAyMyJ9.mswZogDcDPHAMt6S6mzavgTQAjsV1_5Wb3lJdgEInv8',
	}
	headers['X-Access-Token'] = X_Access_Token
	return requests.post(url, headers=headers, params=parameters)


def get_id(X_Access_Token):
	"""
	获取在获取班级学生信息和复制昨日信息中用到的 班级id
	:param X_Access_Token:
	:return:
	"""
	url = 'https://fdys.hnust.edu.cn/wgh/vwWghBjsubmitTotal/queryTodayBjSubmit'
	parameters = {
		'_t': str(get_timestamp() / 1000),
		'column': 'createTime',
		'order': 'asc',
		'field': 'id,,,bjmc,zt,zrs,ytbrs,ysbxx,sfbzx,jkmllm,jkmlym,jkmlhm,hsjgYyin,hsjgYang,hsjgNot',
		'pageNo': 1,
		'pageSize': 10
	}

	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'DNT': '1',
		'Host': 'fdys.hnust.edu.cn',
		'Origin': 'https://jkdk.hnust.edu.cn',
		'Referer': 'https://jkdk.hnust.edu.cn/wgh/nubWghJbxx/list',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'tenant_id': '0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Njg0OTQ0ODYsInVzZXJuYW1lIjoiMTA1MDAyMyJ9.5l04Aibsg4o2d2Ux2mep9rU_8wzcWhHbWUZ8Pl2xEeg'
	}
	headers['X-Access-Token'] = X_Access_Token
	response = requests.get(url=url, headers=headers, params=parameters)
	print('获取bjid：', response.json())
	return response.json()['result'][0]['bjid']


def need_modify():
	print('是否需要统一修改全班同学的核酸时间信息？')
	key = input('是，请输入时间，格式为："2022-11-13"；\n否，请输入-1！；\n退出，请输入0\n')
	if key == '0':
		exit(0)
	elif key != -1:
		need_edit = True
		hssj1 = key
	else:
		need_edit = False



if __name__ == '__main__':
	# 运行py源代码使用
	need_modify()

	X_Access_Token = login()
	print('本次 X-Access-Token：', X_Access_Token)

	wgid = get_id(X_Access_Token)
	print('获取bjid：', wgid)

	response = get_list(X_Access_Token, wgid)
	if response.json()["result"]["total"] == 0:
		response = copy_last(X_Access_Token, wgid)
		print('复制结果：', response.json())
		response = get_list(X_Access_Token, wgid)

	# 需要修改核酸时间
	if need_edit:
		edit(response.json()["result"]["records"], hssj1, X_Access_Token)
	# 提交数据
	time.sleep(0.5)

	if response.json()["result"]["total"] != 0:
		# 这一批学生数据的id 提交数据的时候会用到
		wgid = response.json()['result']['records'][0]['wgid']
		print('提交数据的时候会用到的wgid：', wgid)
		response = submit(X_Access_Token, wgid)
	else:
		print('没有今日数据，可能是程序出错或者今日已经提交过数据了。')
	# 退出登录
	logout(X_Access_Token)
