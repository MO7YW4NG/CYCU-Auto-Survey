import os
import requests
import getpass
import json
import threading

def login(session, id, pwd, headers):
    response = session.get(url=f"https://itouch.cycu.edu.tw/active_system/login/sso/login1.jsp?UserNm={id}&UserPasswd={pwd}&returnPath=https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.getAuth.jsp?success=true&failPath=https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.getAuth.jsp?fail=true", headers=headers)
    if "error" in response.url:
        print("登入失敗，請重新再試!")
        return False
    return True

def verify_session(session, headers):
    session.post(url="https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.checkSession.jsp", headers=headers)

def get_page_token(session, headers):
    response = session.post(url="https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/auth.initPageToken.jsp", headers=headers)
    return json.loads(response.text)["value"]

def get_survey_count(session, token, headers):
    response = session.post("https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method=TSTeacherListByStd&pageToken=" + str(token), headers=headers)
    return json.loads(response.text)["value"]["count"]

def get_survey_questions(session, token, index, headers):
    response = session.post(f"https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method=getTS_QUEST&pageToken=" + str(token), data=json.dumps({"selectItemIndex": index}), headers=headers)
    return json.loads(response.text)["value"]

def get_best_answer(session, token, index, headers, method):
    response = session.post(f"https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method={method}&pageToken=" + str(token), data=json.dumps({"selectItemIndex": index}), headers=headers)
    return json.loads(response.text)["value"]

def submit_answers(session, token, index, ans, headers):
    result = {"selectItemIndex": index, "postParameters": ans}
    session.post(f"https://itouch.cycu.edu.tw/active_project/cycu2000h_11/survey/jsp/SurveyMain3.jsp?method=add_TS&pageToken=" + str(token), data=json.dumps(result), headers=headers)

def handle_survey(session, token, index, headers):
    questions = get_survey_questions(session, token, index, headers)
    ans = {value["name"]: value["options"][0]["value"] for value in questions}
    
    for method in ["getTS_CS_CYCU_IDX_VIEW", "getTS_CS_DEPT_IDX_VIEW"]:
        value = get_best_answer(session, token, index, headers, method)
        needed = int(value["require_max"])
        if needed == 1:
            ans[value["name"]] = value["options"][0]["bitValue"]
        else:
            ans[value["name"]] = [value["options"][i]["bitValue"] for i in range(needed)]
    
    for i in range(1, 10):
        ans["a.2." + str(i)] = "5"
    ans["a.2.1"] = "A"
    ans["a.2.2"] = "C"
    ans["a.2.3"] = "C"
    ans["a.2.4"] = "C"
    
    ans["a.6.1"] = "同意"
    ans["a.6.2"] = None
    
    submit_answers(session, token, index, ans, headers)

def main():
    """Main function.
    """
    os.system("title CYCU-Auto-Survey")
    
    id = input("輸入您的學號：")
    pwd = getpass.getpass("輸入您的itouch密碼：")
    try:
        headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36 Edg/125.0.0.0"}
        session = requests.session()
        
        if not login(session, id, pwd, headers):
            return main()
        
        print("填答中...")
        
        verify_session(session, headers)
        token = get_page_token(session, headers)
        count = get_survey_count(session, token, headers)
        
        threads = []
        for index in range(count):
            thread = threading.Thread(target=handle_survey, args=(session, token, index, headers))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print("填答完成!")
        os.system("pause")
        return
    except Exception as e:
        print(e)
        os.system("pause")
    
if __name__ == '__main__':
    main()