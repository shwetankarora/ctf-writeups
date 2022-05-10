import requests
from requests_toolbelt.utils import dump

ch = 's'

loginUrl = "https://jawt.sdc.tf/login"
payload = {'username':'AzureDiamond','password':'hunter2'}

r = requests.post(loginUrl, data=payload, allow_redirects=False)
cookieHeader = r.headers['Set-Cookie']
if not cookieHeader:
	print("cookie header not found")
	exit()

cookieKeyValue = cookieHeader.split(";")[0].split("=")

flagUrl = "https://jawt.sdc.tf/"+ch

cookies = {}
cookies[cookieKeyValue[0]] = cookieKeyValue[1]

re = requests.get(flagUrl, cookies=cookies)
data = dump.dump_all(re)
print(data.decode('utf-8'))


# "https://jawt.sdc.tf/"+ch+"/d/c/t/f/{/T/h/3/_/m/0/r/3/_/t/0/k/3/n/s/_/t/h/e/_/l/e/5/5/_/p/r/0/b/l/3/m/s/_/a/d/f/3/d/}"