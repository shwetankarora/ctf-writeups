# JaWT That Down

**Category**: Web  
**Level**: Easy  
**Points**: 200  
**Description**: The new ultra maximum security plugin I installed on my website is so good that even I can’t log in. Hackers don’t stand a chance.
Website
https://jawt.sdc.tf/

### Writeup

The description of this challenge doesn't have much clues but the creator have deliberately captilized the letters 'J', 'W', 'T' in the heading which caught our attention. We immediately got the hint that this challenge will require the knowledge of JWT and its exploitation. We started by glancing through the website's functionality on a very high level and were easily able to figure out that we somehow have to get through the user login. This will provide us the JWT which can be further exploited to get the flag. After this high level run through, I was assigned to pick up this challenge.


##### Step 1 : Finding User Login Credentials

I started by performing SQL injection in the login form with simple payloads from the top of my head but it didn't work. I was tempted to run `sqlmap` behind the scenes but I resisted and looked through the source code using browser's(Chrome in my case) debugger tools. I took this detour because I had also spent time on the challenge 'HuMongous Mistake'(which I wasn't able to solve) and found some useful comments in the JavaScript source code.

So my approach was to look for potentially dangerous JavaScript functions in JS file `login.js` which was loaded on the login form web page. The code was written in reactJS and one such function was `dangerouslySetInnerHTML`. Under one of the occurences of this function was the user credentials using which I was successfully able to log in. This saved me a lot of time. 

![Browser Debugger Tools JS Code](https://raw.githubusercontent.com/shwetankarora/ctf-writeups/main/2022/SDCTF/web/JaWT_that_down/screenshots/browser_debugger_js_user_pass.png)

However, later I realised that I could have right clicked on the username/password field of login form and selected "Inspect". This would also have shown me the user credentials.

![Browser Debugger Tools HTML Code](https://raw.githubusercontent.com/shwetankarora/ctf-writeups/main/2022/SDCTF/web/JaWT_that_down/screenshots/browser_debugger_user_pass.png)

##### Step 2 : Observe After Log In

After login, the first thing that caught my eye was an extra menu item named 'Flag' on the top left. But once I click on it, it showed "Invalid Token: Access Denied". 

![Browser Flag Menu Item](https://raw.githubusercontent.com/shwetankarora/ctf-writeups/main/2022/SDCTF/web/JaWT_that_down/screenshots/browser_flag_menu_item.png)

![Browser Invalid Token](https://raw.githubusercontent.com/shwetankarora/ctf-writeups/main/2022/SDCTF/web/JaWT_that_down/screenshots/browser_invalid_token.png)

I fired up Burp Suite and intercepted the HTTP call which is sent once I click on 'Flag'. Let's call it flag endpoint. The first thing that caught my eye was the JWT which is passed in Cookie request header. So, I replayed the request after removing the Cookie request header which showed me a different error "No Token: Access Denied". I was fully convinced that I am on the right track and I need to pass a valid JWT in order to proceed. 

![Burp Suite No Token](https://raw.githubusercontent.com/shwetankarora/ctf-writeups/main/2022/SDCTF/web/JaWT_that_down/screenshots/burp_suite_no_token.png)

##### Step 3 : Get Valid JWT for Flag Endpoint

My next step was to figure out why my JWT is invalid. I decoded and read the contents of the JWT on https://jwt.io/ and figured out that the issue time(iat) and expiry time(exp) has a gap of mere 2 seconds which explained the error "Invalid Token: Access Denied" because by the time I clicked on 'Flag' the token was already expired. I had two solutions in my mind to overcome this problem:
1. Either, I can verify if JWT signature verfiication can be bypassed which will allow me to increase the expiry time.
2. Or, I make a script to automate this process of logging in and using the JWT in the next flag endpoint.

**First Approach - Signature Verification Bypass**

I went with the first option because writing a script for me would take comparatively more time. Here is a [good read of JWT's 'none' algorithm](https://medium.com/@phosmet/forging-jwt-exploiting-the-none-algorithm-a37d670af54f).
Essentially, I divided the JWT into 3 base64 encoded parts by splitting it using '.'(period). I base64 decoded the first part on https://www.base64decode.org/, changed the value of "alg" to "none", base64 encoded it on https://www.base64encode.org/. This was tampering of first part of JWT(called header). Then I did the same thing with the second part(called payload) except I increased the expiry to a month. I joined both the parts and recreated my final JWT

*Before*: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IkF6dXJlRGlhbW9uZCIsInRva2VuIjoiZGVmZjVmZmU0YWY0OWYzOWE3ZjI2YTBlN2U0NGQ1NCIsImlhdCI6MTY1MjE3NzExMiwiZXhwIjoxNjUyMTc3MTE0fQ.jmcOs7t4hSFYad3wz2S993jJ7lQOYbG_paBrqSByBBM`

*After*: `eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VybmFtZSI6IkF6dXJlRGlhbW9uZCIsInRva2VuIjoiZGVmZjVmZmU0YWY0OWYzOWE3ZjI2YTBlN2U0NGQ1NCIsImlhdCI6MTY1MjE3NzExMiwiZXhwIjoxNjU0ODU3NDI3fQ.`

However, I got the same error "Invalid Token: Access Denied" using my new token. Hence, I scratched out the first approach and went back to the second approach.

**Second Approach - Automate Log In and Flag Endpoint**

I quickly wrote a little python script which looked like this:
```python
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
```

The above script hits the `/login` endpoint, reads the JWT from Set-Cookie response header, sets it in the the flag endpoint `/s` and prints the request/response of the flag endpoint. It gave me the following output:

```http
< GET /s HTTP/1.1
< Host: jawt.sdc.tf
< User-Agent: python-requests/2.27.1
< Accept-Encoding: gzip, deflate
< Accept: */*
< Connection: keep-alive
< Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IkF6dXJlRGlhbW9uZCIsInRva2VuIjoiMzc5Y2EyOWRmNmQ5ZjM1N2U5ZTdjZWEzOTcxNzQ2NiIsImlhdCI6MTY1MjE3OTI4MCwiZXhwIjoxNjUyMTc5MjgyfQ.7lxeRGwHBFhpeChplXje1-LLHbF_mdZx7DzrCpgl32M
<

> HTTP/1.1 200 OK
> Date: Tue, 10 May 2022 10:41:20 GMT
> Content-Length: 1
> Connection: keep-alive
> X-Powered-By: Express
> Via: 1.1 google
> CF-Cache-Status: DYNAMIC
> Expect-CT: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
> Report-To: {"endpoints":[{"url":"https:\/\/a.nel.cloudflare.com\/report\/v3?s=aiYf7PWSnmhxBfoNe5a%2BJ8YB3o%2BvUj8O1CK55r300zSWI50ioyAHEvt38IH2N8wAQ2B9uC2tmKKR%2B7CaAzOqcSLY%2FOcBKGoaTu%2BmO8MAyiIyIQB3LQ0VOZckW%2BXQMQ%3D%3D"}],"group":"cf-nel","max_age":604800}
> NEL: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
> Server: cloudflare
> CF-RAY: 70920fd6dab29e47-SIN
> alt-svc: h3=":443"; ma=86400, h3-29=":443"; ma=86400
>
d
```

I wasn't able to understand the response of this for a long time. I tried hitting `/d` endpoint by changing the python script but it gave me 404 not found. Similariy, I tried hitting `/sd` and enumerated from `/a` to `/z` both in small and capital letters but got the same result. At this point, I took a new challenge. I later got an idea to give a try to `/s/d` and it worked. It gave me `/c`. Since all the flag of this challenge started with 'sdctf' therefore I continued this methodology by changing the script, saving and hitting one by one. Eventually I got this endpoint `https://jawt.sdc.tf/s/d/c/t/f/{/T/h/3/_/m/0/r/3/_/t/0/k/3/n/s/_/t/h/e/_/l/e/5/5/_/p/r/0/b/l/3/m/s/_/a/d/f/3/d/}` which has the flag.

**Flag** - `sdctf{Th3_m0r3_t0k3ns_the_le55_pr0bl3ms_adf3d}`


### Final Thoughts

In real world applications, short-lived JWTs are very much used. But even if they are short-lived, they can be exploited to retrieve sensitive information. Hence, reducing the expiry time wouldn't necessarily mean that the system is protected.  
Although, being a beginner, I wasn't able to complete this challenge on time because the idea of making the URL the right way came late to me but still at the end of the day I am happy that I was able to solve this challenge on my own.  
During the course of this challenge, I had great fun reading about JWT, JWK and JWS which enhanced my knowledge while at the same time helped me practically understand the exploitation of it.