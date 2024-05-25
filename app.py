import os
import requests
import getpass
import json

def main():
    """Main function.
    """
    os.system("title CYCU-Auto-Survey")
    
    id = input("輸入您的學號：")
    pwd = getpass.getpass("輸入您的itouch密碼：")
    try:
        headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36 Edg/125.0.0.0"}
        session = requests.session()
        
        # Session Login
        response = session.get(url=f"https://itouch.cycu.edu.tw/active_system/login/sso/login1.jsp?UserNm={id}&UserPasswd={pwd}&returnPath=https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.getAuth.jsp?success=true&failPath=https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.getAuth.jsp?fail=true",headers=headers)
        
        if "error" in response.url:
            print("登入失敗，請重新再試!")
            return main()
        
        print("填答中...")
        
        # Session verify
        session.post(url="https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.checkSession.jsp",headers=headers)
        
        # Retrieve page token
        response = session.post(url="https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.initPageToken.jsp",headers=headers)
        token = json.loads(response.text)["value"]
        
        # Retrieve survey index
        response = session.post("https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method=TSTeacherListByStd&pageToken=" + str(token),headers=headers)
        count = json.loads(response.text)["value"]["count"]
        
        for index in range(count):
            # Retrieve survey questions
            response = session.post(f"https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method=getTS_QUEST&pageToken=" + str(token), data=json.dumps({"selectItemIndex": index}),headers=headers)
            # Retrieve best answer
            ans = dict()
            
            for value in json.loads(response.text)["value"]:
                ans[value["name"]] = value["options"][0]["value"]
            
            for method in ["getTS_CS_CYCU_IDX_VIEW","getTS_CS_DEPT_IDX_VIEW"]:
                response = session.post(f"https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method={method}&pageToken=" + str(token), data=json.dumps({"selectItemIndex": index}),headers=headers)
                value = json.loads(response.text)["value"]
                needed = int(value["require_max"])
                if needed == 1:
                    ans[value["name"]] = value["options"][0]["bitValue"]
                else:
                    list = []
                    for i in range(needed):
                        list.append(value["options"][i]["bitValue"])
                    ans[value["name"]] = list
            
            for i in range(1,10):
                ans["a.2." + str(i)] = "5"
            ans["a.2.1"] = "A"
            ans["a.2.2"] = "C"
            ans["a.2.3"] = "C"
            ans["a.2.4"] = "C"
            
            ans["a.6.1"] = "同意"
            ans["a.6.2"] = None
            
            # Send answer
            result = {"selectItemIndex": index, "postParameters": ans}
            response = session.post(f"https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method=add_TS&pageToken=" + str(token), data=json.dumps(result),headers=headers)
        
        print("填答完成!")
        os.system("pause")
        return
    except Exception as e:
        print(e)
        os.system("pause")
    
if __name__ == '__main__':
    main()