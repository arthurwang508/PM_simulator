import streamlit as st
from firebase import firebase
import firebase_admin 
from firebase_admin import db, credentials
import pandas as pd
import numpy as np
import datetime
import random
import time
import pytz


url = "https://pm-boardgame-default-rtdb.asia-southeast1.firebasedatabase.app/"
fdb = firebase.FirebaseApplication(url, None)

cred = firebase_admin.credentials.Certificate("pm-boardgame-firebase-adminsdk-g06vf-b08ad57d71.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': url
    })

#Define database reference
ref = db.reference('/')
user_ref = ref.child('user_pw')
board_ref = ref.child('board')
workspace_ref = ref.child('workspace')

st.title("Product Management Simulator")
st.markdown("V2.2.3 Developed by 王彥成")

team_list = ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6", "Team 7", "Team 8", "Team 9", "Team 10"]

identity = st.selectbox("Select ID", ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6", "Team 7", "Team 8", "Team 9", "Team 10", "Admin"])

freeze_default = False

if identity == "Admin":
    admin_pw = st.text_input("Enter Password", type="password")
    if admin_pw:
        if str(admin_pw) == "1688":
            st.text("Successfully Logged In")
            
            #Game control
            st.markdown("# Game Control")
            if st.button("Start Game"):
                user_ref.update({"admin":"Game start"})
                #fdb.post('/user',{"admin":"Game start"})
                st.text(fdb.get('/user_pw','admin'))
                # st.text(fdb.get('/',"user_pw"))

            #Reset Game
            if st.button("Reset Game"):
                fdb.delete('/','user_pw')
                fdb.delete('/','board')
                fdb.delete('/','workspace')
                st.text("Game Reset")
            
            if st.checkbox("Freeze game"):
                user_ref.update({"admin":"Game frozen"})
                st.text("Game frozen")
            else:
                user_ref.update({"admin":"Game start"})
            
            #Set default points
            st.markdown("# Set Default Points")
            df_point = st.text_input("Enter Default Points")
            if df_point:
                df_point = int(df_point)
                if st.button("Set Default Points"):
                    for team in team_list:
                        if team in fdb.get('/', 'user_pw').keys():
                            score_ref = board_ref.child(team)
                            score_ref.update({"points":df_point})
                                
            #Leaderboard
            st.markdown("# Leaderboard")
            registered_team = fdb.get('/', 'board')
            if registered_team:
                df_leaderboard = pd.DataFrame(registered_team)
                st.dataframe(df_leaderboard)
            else:
                st.warning("No team has registered yet")
            st.button("Refresh")
            
            #workspace
            workspace_name = identity + "_workspace"
            
            #Event generator
            event_dict = {"駭客攻擊":1,
                          "系統升級":2,
                          "蠢蛋實習生":3,
                          "黑色星期五":4,
                          "金宣虎見面會":5,
                          "基金會拜訪":6,
                          "天使降臨":7,
                          "聯合國來訪":8,
                          "凜冬將至":9,
                          "老大來了":10}
            st.markdown("# Event Generator")
            # event = st.selectbox("Select Event", event_dict)
            
            #path setting
            team_workspace_ref = workspace_ref.child(workspace_name)
            
            task_path = "/workspace/"+workspace_name
            team_tasks = fdb.get(task_path, 'tasks')
            
            
            if 'clicked' not in st.session_state:
                st.session_state.clicked = False
                    
            def click_button():
                st.session_state.clicked = True
            
            choose_event = st.button("Random Event")
            # if choose_event:
            #     click_button()
            
            
            # if st.session_state.clicked == True:
            #     event = random.choice(list(event_dict.keys()))
            #     st.text(event)
            #     if st.button("Confirm"):
            #         event_list.append(event)
            #         st.session_state.clicked = False
            #         pass
            if st.checkbox("Meteor Fall Activate"):
                event_dict["隕石降落"] = 11
                st.text("Meteor Fall Activated")
            else:
                if "隕石降落" in event_dict.keys():
                    del event_dict["隕石降落"]
                else:
                    pass
            
            if choose_event:
                event = random.choice(list(event_dict.keys()))
                st.text(event)
            
        else:
            st.error("Incorrect Password")
        #############################Team code below################################
else:
    if fdb.get('/user_pw','admin') == None:
        st.error("Admin has not started the game yet")
    elif fdb.get('/user_pw','admin') == "Game frozen":
        st.warning("Game is frozen, please wait a minute")
        st.markdown("# Leaderboard")
        #Leaderboard
        registered_team = fdb.get('/', 'board')
        if registered_team:
            df_leaderboard = pd.DataFrame(registered_team)
            st.dataframe(df_leaderboard)
            st.button("Refresh", key= "pm_leaderboard")
        else:
            st.warning("No team has registered yet")
            
        #path setting
        workspace_name = identity + "_workspace"
        team_workspace_ref = workspace_ref.child(workspace_name)
        score_ref = board_ref.child(identity)
        
        task_path = "/workspace/"+workspace_name
        team_tasks = fdb.get(task_path, 'tasks')
        
        st.markdown("# Product Tasks")
        st.button("Refresh", key = "product_task")
        if team_tasks:
            task_dataframe = pd.DataFrame(team_tasks)
            st.dataframe(task_dataframe)
        else:
            st.text("No tasks")
        
        
        #
    elif fdb.get('/user_pw', identity) == None:
        rg_team_pw = st.text_input("Register your password", type="password")
        if rg_team_pw:
            user_ref.update({str(identity):str(rg_team_pw)})
            #fdb.post('/user',{str(identity):str(rg_team_pw)})
            score_ref = board_ref.child(identity)
            score_ref.update({"points":0})
    elif fdb.get('/user_pw', identity):
        team_pw = st.text_input("Enter Password", type="password")
        if team_pw:
            if team_pw == fdb.get('/user_pw', identity):
                st.text("Successfully Logged In")
                
                #Leaderboard
                st.markdown("# Leaderboard")
                registered_team = fdb.get('/', 'board')
                if registered_team:
                    df_leaderboard = pd.DataFrame(registered_team)
                    st.dataframe(df_leaderboard)
                    st.button("Refresh", key= "pm_leaderboard")
                else:
                    st.warning("No team has registered yet")
                
                role = st.selectbox("Select your role", ["Product Manager", "Developer", "UI/UX Designer"])

                if role == "Product Manager":
                    
                    #path setting
                    workspace_name = identity + "_workspace"
                    team_workspace_ref = workspace_ref.child(workspace_name)
                    score_ref = board_ref.child(identity)
                    
                    task_path = "/workspace/"+workspace_name
                    team_tasks = fdb.get(task_path, 'tasks')
                    
                    #Define user story
                    st.markdown("# Define your user story")
                    st.markdown("As a **<type of user>**, I want **<some goal>** so that **<some reason>**")
                    st.markdown("Example: As a **manager**, I want to **be able to understand my colleagues progress**, so I can **better report our sucess and failures.** ")
                    user_story = st.text_input("Enter your user story")
                    if st.button("Submit"):
                        if user_story:
                            user_story_ref = team_workspace_ref.child("user_story")
                            user_story_ref.update({"user story":user_story})
                        else:
                            st.warning("Please enter your user story")
                    user_story = fdb.get(task_path, 'user_story')
                    if user_story:
                        st.markdown("##### Your user story: "+str(list(user_story.values())[0]))
                    
                    #Product task
                    st.markdown("# Product Tasks")
                    st.button("Refresh", key = "product_task")
                    if team_tasks:
                        task_dataframe = pd.DataFrame(team_tasks)
                        st.dataframe(task_dataframe)
                    else:
                        st.text("No tasks")
                        
                    placeholder = st.empty()
                    
                    if 'clicked' not in st.session_state:
                        st.session_state.clicked = False
                    
                    def click_button():
                        st.session_state.clicked = True
                    
                    if st.session_state.clicked == True and fdb.get('/board', identity+"/points")<5:
                        st.warning("You don't have enough points to create a task")
                        time.sleep(2)
                        st.session_state.clicked = False
                    elif st.session_state.clicked == True:
                        task_name = st.text_input("Task name")
                        task_des = st.text_input("Task description")
                        must_or_want = st.selectbox("Must or Want", ["Must", "Want"])
                        try:
                            story_points = int(st.text_input("Story points"))
                        except:
                            st.warning("Enter wrong format, story point set to zero point")
                            story_points = 0
                        if story_points > 10:
                            story_points = 10
                        elif story_points < 0:
                            story_points = 0
                        else:
                            pass
                        assign = st.text_input("Assignee")
                        if st.button("Create"):
                            if team_tasks != None:
                                # task_count = len(admin_tasks)+1
                                task_count = int(str(list(team_tasks.keys())[-1])[-1])+1
                            else:
                                task_count = 1
                            task_ref = team_workspace_ref.child("tasks/task%d"%(task_count))
                            task_ref.update({"Feature name":task_name})
                            task_ref.update({"Task description":task_des})
                            task_ref.update({"Must or Want":must_or_want})
                            task_ref.update({"Story points (Please enter a number between 0~10)":str(story_points)})
                            task_ref.update({"Task assignee":assign})
                            task_ref.update({"Task status":"To do"})
                            task_ref.update({"code":""})
                            current_score = fdb.get('/board', identity+"/points")
                            current_score -= int(story_points)
                            score_ref.update({"points":current_score})
                            
                            placeholder.empty()
                            st.session_state.clicked = False
                        else:
                            pass
                    else:
                        # add_task = placeholder.button("Add Task", on_click=click_button)
                        add_task = placeholder.button("Add Task")
                        if add_task:
                            click_button()
                    
                    # cancel tasks
                    if team_tasks != None:
                        st.markdown("**請選擇欲取消的任務（如果不想要任務被刪光光拜託按一次就好了）**")
                        delete_task = st.selectbox("Select Task", team_tasks)
                    
                        if st.button("Delete"):
                            fdb.delete(task_path+'/tasks',delete_task)
                    
                        st.markdown("**清除所有任務**")
                        if st.button("Clear all tasks"):
                            fdb.delete('/workspace',workspace_name)
                elif role == "Developer":
                    
                    workspace_name = identity + "_workspace"
                    team_workspace_ref = workspace_ref.child(workspace_name)
                    task_path = "/workspace/"+workspace_name
                    team_tasks = fdb.get(task_path, 'tasks')
                    
                    st.markdown("# Developer")
                    st.button("Refresh")
                    
                    backlog, log_board = st.columns(2)
                    
                    with backlog:
                        st.markdown("## Backlog")
                        if team_tasks:
                            task_dataframe = pd.DataFrame(team_tasks)
                            st.dataframe(task_dataframe)
                    
                    with log_board:
                        st.markdown("## Log History")
                        code_history = fdb.get(task_path, 'code_history')
                        if code_history:
                            code_history_dataframe = pd.DataFrame(code_history, index = ["code"]).transpose()
                            st.dataframe(code_history_dataframe)
                        
                    if team_tasks:
                        
                        if 'clicked' not in st.session_state:
                            st.session_state.clicked = False
                        
                        def click_button():
                            st.session_state.clicked = True
                        
                    
                        st.markdown("#### Code Rule:")
                        st.markdown(" def <**feature_name**>(): -> page_list = <**feature_name**>")
                        st.markdown("return function")
                        st.markdown("def set_buttons(<**base_page**>): -> buttons = <**feature_name**>")
                        st.markdown("return function")
                        st.markdown("def <**function_name**>(): -> description = <**description**>")
                        st.markdown("return function")
                        
                        st.markdown("**請選擇欲執行的任務**")
                        select_task = st.selectbox("Select Task", team_tasks, key = "select task")
                        code_placeholder = st.empty()
                        
                        select_task_button = code_placeholder.button("Select")
                        status = fdb.get(task_path, 'tasks/%s/Task status'%(select_task))
                        
                        if select_task_button:
                            status_ref = team_workspace_ref.child("tasks/%s"%(select_task))
                            if status == "To do":
                                status_ref.update({"Task status":"In progress"})
                            click_button()
                        
                        if st.session_state.clicked == True and status != "Done":
                            area_default_value = fdb.get(task_path, 'tasks/%s/code'%(select_task))
                            code_area = st.text_area("Enter text", height = 275, value = area_default_value)
                            submit_code = st.button("Submit")
                            
                            
                            
                            if submit_code:
                                code_ref = team_workspace_ref.child("tasks/%s"%(select_task))
                                
                                # code_ref.update({"code at %s"%(time_stamp):code_area})
                                code_ref.update({"code":code_area})
                                
                                #check code
                                if fdb.get(task_path+"/tasks/",select_task+"/code").startswith("def") and fdb.get(task_path+"/tasks/",select_task+"/code").endswith("return function"):
                                    code_ref.update({"Task status":"Done"})
                                    st.text("success")
                                    current_score = fdb.get('/board', identity+"/points")
                                    current_score = int(current_score+1.5*int(fdb.get(task_path+"/tasks/",select_task+"/Story points (Please enter a number between 0~10)")))
                                    score_ref = board_ref.child(identity)
                                    score_ref.update({"points":current_score})

                                #code history
                                time_now = datetime.datetime.now(pytz.timezone('Asia/Taipei'))
                                time_stamp = str(time_now.hour)+":"+str(time_now.minute)+":"+str(time_now.second)
                                code_with_time_ref = team_workspace_ref.child("code_history")
                                code_with_time_ref.update({"code at %s"%(time_stamp):code_area})

                                code_placeholder.empty()
                                st.session_state.clicked = False


                        elif st.session_state.clicked == True and status == "Done":
                            st.warning("Task has been completed")
                            st.session_state.clicked = False
                elif role == "UI/UX Designer":
                    # A/B Testing
                    st.markdown("# A/B Testing")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("## Demo A")
                        option_a = st.file_uploader("Upload file", type = ["png", "jpg", "jpeg"], key="a")
                        if option_a:
                            st.image(option_a)
                    with col2:
                        st.markdown("## Demo B")
                        option_b = st.file_uploader("Upload file", type = ["png", "jpg", "jpeg"], key = "b")
                        if option_b:
                            st.image(option_b)
                    
                    if option_a and option_b:
                        st.markdown("## Result")
                        
                        #Map
                        st.markdown("Geographical distribution")
                        map_df = pd.DataFrame({
                            "latitude": [random.randint(random.randint(0, 30), random.randint(30, 60)) for i in range(100)],
                            "longitude": [random.randint(random.randint(0, 90), random.randint(90, 120)) for i in range(100)],
                            "size": [random.randint(0, 30) for i in range(100)],
                        })

                        st.map(map_df)
                        
                        #Report
                        data_a = [random.randint(0, 100), 
                                  random.randint(0, 65), 
                                  random.randint(0, 50), 
                                  random.randint(10, 70), 
                                  random.randint(0, 100)]
                        data_b = [random.randint(0, 100), 
                                  random.randint(0, 75), 
                                  random.randint(10, 60), 
                                  random.randint(15, 65), 
                                  random.randint(0, 100)]
                        result = pd.DataFrame({"Prototype A":data_a, "Prototype B":data_b}, index = ["Click-through rate (%)","Conversion rate (%)", "Average order value (USD)", "Average user age (years)", "Gender ratio (Male %)"])
                        st.table(result)
                        
                        report_csv = result.to_csv("Report.csv",index = True)
                        
                        @st.cache
                        def convert_df_to_csv(df):
                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                            return df.to_csv().encode('utf-8')
                        custom_filename = st.text_input("Filename")
                        st.download_button("Download Report", data = convert_df_to_csv(result), file_name = str("Report "+identity+" - "+custom_filename+".csv"), mime = "text/csv")
                            
                    else:
                        st.warning("Please upload both files")
            else:
                st.error("Incorrect Password")
    
