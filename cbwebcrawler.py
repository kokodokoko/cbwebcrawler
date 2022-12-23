import collections
import csv
import time
import re
from dotenv import load_dotenv
load_dotenv()
from os import environ
import requests
from lxml import etree

# Type: person
#       [Personal Investments]
#       [Partner Investments]
# Type: organization
#       /recent_investments -> investments
#       /company_financials/investors -> investors

# Location
# Funding
# Listing

# class="component--field-formatter field-type-identifier link-accent ng-star-inserted"
# title="Meson Network"
# aria-label="Meson Network"
# href="/organization/meson-network">

organization_dict = {}
person_dict = {}
process_list = []

DEBUG = True
def m_print(a, b = "", c = "", d = ""):
    if DEBUG:
        print(a, b, c, d)

# TODO: log in for webcrawler
crunchbase_email = environ.get("crunchbase_email")
crunchbase_password = environ.get("crunchbase_password")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Cookie': 'cid=CihvxmOOrEyi/wAvA4jsAg==; featureFlagOverride=%7B%7D; featureFlagOverrideCrossSite=%7B%7D; _pxvid=c26390de-750f-11ed-9d57-565862726262; _gcl_au=1.1.293046520.1670996887; _delighted_web={%220SrRdbRV9pdk0Aem%22:{%22_delighted_fst%22:{%22t%22:%221670996888079%22}%2C%22_delighted_lst%22:{%22t%22:%221670384558000%22%2C%22m%22:{%22token%22:%22ubPU8vJjd1Bh3YUtKNXx9X4B%22}}}}; drift_aid=d919cb12-4b8c-43a4-9520-db757c579319; driftt_aid=d919cb12-4b8c-43a4-9520-db757c579319; xsrf_token=blLv7FdTQDm0zLenGSIx8Wg4jqWmhQR4IkwECy0Bhlo; __cflb=02DiuJLCopmWEhtqNz4kLfsbkjf8jWM2bFQjEbpQVUo32; pxcts=645a46e8-825f-11ed-b84e-6a45674e7156; _gid=GA1.2.316933372.1671758177; ln_or=eyIzOTYwMzYiOiJkIn0%3D; fs_uid=#BA8KZ#5539844091367424:6412034080854016:::#335440b6#/1703298614; drift_eid=3db4c554-95f1-42eb-a342-1c8a72abe036; _hp2_props.973801186=%7B%22Logged%20In%22%3Afalse%2C%22Pro%22%3Afalse%2C%22cbPro%22%3Afalse%7D; _hp2_ses_props.973801186=%7B%22ts%22%3A1671774069843%2C%22d%22%3A%22www.crunchbase.com%22%2C%22h%22%3A%22%2Flogin%22%7D; _pxff_cc=U2FtZVNpdGU9Tm9uZTsgU2VjdXJlOyA=; _pxff_fp=1; _pxff_ne=1; _pxff_bsco=1; _px3=4e3a5250471129c130f5906510c1ed1bfd4bf2c9dd99dc9fefff4477a53b931a:JkFyhDXcsVJsTC5hHVn/nleO6KgUhMFITisu01BlYXokxgKMQwpgL7hXmpZ2vTLfOF5U5boPvNCulmXsNHidzw==:1000:9S8UGh5bRsYtlPKZf3mGk2neuuJLD9VkcviC5/Zb03GsBeLLXZPsw+tF2u1EZLs73IUaytYWwjSd2tdH6ncP6Mwag4U8n/BNNf5M3rgai8tFd4HnzQOkFofmj7oDuZOfjcIbNR7Q8mjPo1boTMpg6uCClccMdTmtD0I6CHjDOUU/fqNBBmaidIgVIRuy8rCestfWTzPRtnVaowXw9xXYhg==; _gat_UA-60854465-1=1; OptanonConsent=isIABGlobal=false&datestamp=Fri+Dec+23+2022+14%3A41%3A15+GMT%2B0900+(Japan+Standard+Time)&version=6.23.0&hosts=&consentId=a06a5240-3ff4-4143-b917-dd7cfb811a0d&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CBG7%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=JP%3B31; OptanonAlertBoxClosed=2022-12-23T05:41:15.347Z; _uetsid=66260100825f11edabb8958eb3a77f69; _uetvid=1464038016f511ed8ecc5333390fec59; _ga_PGHC4BDGLM=GS1.1.1671774073.8.1.1671774075.0.0.0; _ga=GA1.1.1859030454.1670996887; _ga_97DKWJJNRK=GS1.1.1671774073.8.1.1671774075.0.0.0; _hp2_id.973801186=%7B%22userId%22%3A%225132992811669308%22%2C%22pageviewId%22%3A%228463963930842023%22%2C%22sessionId%22%3A%225218847807489205%22%2C%22identity%22%3A%22shh_name%40hotmail.com%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%7D; _pxhd=N9kFfx1X8jMw-XBAgp8QSDousvzEW9qXwo4JjwLInsDIe34A7gQmp4h4kq4nD6mUxcPuRkUx3sJZe-9YsvmFog; authcookie=eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJiZjY5NDA3MS0zY2QxLTRmZDctYjdiMS1mNWZlMmM1YmI5MWQiLCJpc3MiOiJ1c2Vyc2VydmljZV81ZGFlZjgzN182NDkiLCJzdWIiOiIzZGI0YzU1NC05NWYxLTQyZWItYTM0Mi0xYzhhNzJhYmUwMzYiLCJleHAiOjE2NzE3NzQ0MjUsImlhdCI6MTY3MTc3NDEyNSwicHJpdmF0ZSI6IlhBbVRTc2V5enVsWjVuRE5BTnlJOTBoQUxkVVRpSUJwSzBlTUFkTWNrdlZ4ZCtmRTMwTFp1N1MvNExSbXFRU0RtQy9xY2dCSm1yd1laanM3VzVMQWZhZ1V5em1QOTNSdTY0S3RIcGw4SEkrMG1qN0hWQ2c3VHI2WG5WNDdKK1pkOENqb2dLK01Za0pVT0Z3VWE0YTUxVzRMUmNpMXlwM01xQUVlVldZNW5OQ0lXeE1jaDRKR20wVllxcDVTNnY0TWJITDBnUXlFUmZSQ0pIZmtRTnpmUWd0UTlTUzM4MEI5bTdSVjM0ckpZRHArUG15eE9LWmgyd1dEKzgyUnI5aVhtVFY2MENLWXhWemphSWlPOEVXdGNMZ3JsUkVQdDhXVG5ld1oxSE5KRVpUNG9VSDZnQys5bVNoRlNEVHRla3F0cjlkMVBzSExYYXN2YzVFRC9Ca2dVeUgxa05YSGlYMzdZNHZNaUtLOG9lUHkwenBWZWd4cWZheFFPQllXK1Ixa0hEa2J5bHZnOEZHOUJMMVRaU3IxUGRmS0lzUS96V0ZDU1hOOExtV2ZvMjN3b1VRVElYTUd3cGgyc2o5bzhHZzRPdm03M3NCNGNGUXNYZFR0V3lkeFUrMy91QkhXbElVWE9oZmpaNUNlNG1mU0I0V0RCQkFqQnk5a1B4eVRwVWUweTh3bnZ6dTQ2d1JHRit6dHpvNzNEelF3WktTQXdDNzQ4MlNEK1REOTE2dWkyWDYxV2JLaEsvK2xvTzU5bkhvS3krcGJoem02TzZKb2xweno2TUpkZGlUaEV2dkFGS0kxaUw3d0plUG5QTWZGWk1KbHdEMVdabmZUSXYrbDJURFAyZXU1ODVaRmM1M0NCTFFRNzI5bmsrR1YvTnNlSEw3bEE0MVVKMWt2NU9VV1M4YkxSTGFqUjNMa2liTTdJQzhmSllLV3VJWWwrUnJJNEpkYStvT3lSOFgrekJuNmFrOVpZQXd0NlhoZm9MUFkzejNZSk1JUERuTXg0OHk0bC9KQmFmT1NYNFhwVGp0U1Y1dEtwbEVtOXZpcUtBUVdEY3NXZ2FnZGpzQWdJUE9jZUI2a1FSc29mc0hiWkNBMmtIamZ6ZTV2OE1XR2JmWTh5STN5Vm9acHV3Y2ptMldtdS9TTGJ0aUN2aTNDd3QwN0g3SnFLWlFlMmpUT213c3dDUi9tZTVONG8xOWdsejZUT09oODFLRWlmU2tmejZMNTRncTdDQVFHTWZwTXFnbWlKdDVrWXU0UW02cWoxMzgrLzBUa1BHN2UrOStLWGtWWitGL040Rmk2a0pXUmI4bi82UkpkaHUraFA3M0VOWm1lT3EvbmhqalNCT2tPQXFvUWdHNVBJNFJ3NkFpK2psb2UwR3Zsc010bHk5WFFBZlowRTJ1Q1BSSlBXYzZrWXVTZ0ttUnUyZG9lSlE2cTdLNGJRS0JSb1hwZE5Ib1ZPSmlBZVlEalQwOVpRYjJ0TUJ2cm9UaXd2eldwYXN2ZTVEM0thZm42WVNEUlFCUjB4RjR4bDFVQ0ZCeWJBS1o2UUwvRUoveURTcXJ5dWxiU2RvTnVvVEdRMTE5bnBRU1BvaEhOQzJ2eVZlWSt2M2FZeGVDZ24xdE5uVFA0RWNYM1lmUTdyS0c4RWhaenNRPT0iLCJwdWJsaWMiOnsic2Vzc2lvbl9oYXNoIjoiLTE3NjU3MTU5NTUifX0.4EYtO095QbET1Sq3IWV-YdENBzmUE11_nXF3Pz2oJMZUVhzF6bZJsTLxHwN8Hl2kQCFxsNZoiTvewXVxGbj29Q'
}

def crunchbase_test():
    with open("Meson_WebCrawler_Crunchbase_Output.html","w",encoding="utf-8") as file_html:
        response = requests.get("https://www.crunchbase.com/organization/meson-network/company_financials/investors", headers=headers)
        m_print("crunchbase_test -> response.status_code:", response.status_code)
        file_html.write(response.text)
        file_html.write("Finsihed")
        m_print("crunchbase_test: Finished")
# crunchbase_test()
# exit(0)

def domain_to_name(domain):
    name = domain.split('/')[-1]
    for i in range(len(name)):
        if name[i] == '-':
            name = name[:i] + ' ' + name[i+1:]
    return name

def domain_to_type(domain):
    name = domain.split('/')[-2]
    for i in range(len(name)):
        if name[i] == '-':
            name = name[:i] + ' ' + name[i+1:]
    return name

# append write
# step1: file to program
# step2: program keeps writing to file

def init():
    file_nodes = csv.reader(open("Meson_WebCrawler_Crunchbase_Nodes.csv", encoding="utf-8"))
    file_process_hid = open("Meson_WebCrawler_Crunchbase_Process_Hid.txt", "r", encoding="utf-8")
    for each_row in file_nodes:
        domain = each_row[0].strip()
        pname = domain_to_name(domain)
        ptype = domain_to_type(domain)
        # m_print("name = {0}, type = {1}".format(pname, ptype))
        if ptype == "organization":
            # m_print(pname, "is an organization")
            if domain in organization_dict:
                continue
            organization_dict[domain] = True
            process_list.append(domain)
        elif type == "person":
            # m_print(pname, "is a person")
            if domain in person_dict:
                continue
            person_dict[domain] = True

    global hid
    line = file_process_hid.read()
    hid = int(line) if line.isdigit() else 0
    file_process_hid.close()

    m_print("init -> len(process_list) = " + str(len(process_list)))
    m_print("process_list:", process_list)
    m_print("hid:", hid)

# main
# only run csv_to_txt() for the first time
init()

file_process_hid = open("Meson_WebCrawler_Crunchbase_Process_Hid.txt", "w", encoding="utf-8")
file_nodes = open("Meson_WebCrawler_Crunchbase_Nodes.csv","a",encoding="utf-8")
file_edges = open("Meson_WebCrawler_Crunchbase_Edges.csv","a",encoding="utf-8")

while hid < len(process_list):
    domain = process_list[hid]
    pname = domain_to_name(domain)
    ptype = domain_to_type(domain)
    m_print("from queue - domain:", domain)
    # m_print("name = {0}; type = {1}".format(pname, ptype))

    # type 1
    response = requests.get(domain + "/recent_investments", headers=headers)
    # type 2
    # response = requests.get(domain + "/company_financials/investors", headers=headers)
    # TODO: check different urls for different investment lists one by one
    print("response.status_code:", str(response.status_code))
    if response.status_code != 200:
        time.sleep(30)
        continue

    inv_str = '<div hoveroverelement="" class="identifier-label">'
    inv_list = [i.start() for i in re.finditer(inv_str, response.text)]
    print("len(inv_list):", len(inv_list))
    cnt = 0
    for pos in inv_list:
        cnt += 1
        if cnt % 2 == 0:
            continue
        start_pos = pos + 48
        while response.text[start_pos] != '>':
            start_pos += 1
        start_pos += 1
        end_pos = start_pos + 1
        while response.text[end_pos] != '<':
            end_pos += 1
        file_edges.write("{0}[{1}], {2}".format(pname, cnt // 2 + 1, response.text[start_pos:end_pos].strip()))
        # TODO: get the urls and add to the list, keep searching in th queue

    hid += 1
    file_process_hid.write(str(hid))
    time.sleep(10)

file_process_hid.close()
file_nodes.close()
file_edges.close()
print("Finished")
