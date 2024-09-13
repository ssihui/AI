import tkinter as tk
from tkinter import filedialog
import cv2
import json
from ultralytics import YOLO, solutions
from PIL import Image, ImageTk
import os
from tkinter import  messagebox
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


model = YOLO("trained/yolov8n-pose.pt")

# 读取 JSON 文件
def load_food_options():
    with open('C:\\Users\\User\\Downloads\\cal\\food_options.json', 'r', encoding='utf-8') as file:
        return json.load(file)

food_data = load_food_options()

# 计算BMR和TDEE的函数
def calculate_bmr_tdee():
    try:
        # 获取用户输入的年龄、身高和体重
        age = float(age_entry.get())
        height = float(height_entry.get())
        weight = float(weight_entry.get())
        gender = gender_var.get()
        activity_level = activity_level_var.get()

        # 计算BMR（基础代谢率）
        if gender == '男':
            bmr = (13.7 * weight) + (5 * height) - (6.8 * age) + 66
        else:
            bmr = (9.6 * weight) + (1.8 * height) - (4.7 * age) + 655

        # 活动水平的系数
        activity_multipliers = {
            "無活動：久坐": 1.2,
            "輕量活動：每周運動1-3天(輕鬆)": 1.375,
            "中度活動量：站走稍多、每周運動3-5天（中強度）": 1.55,
            "高度活動量：站走為主、每周運動6-7天（高強度）": 1.725,
            "非常高度活動量": 1.9
        }

                # 确保活动水平被正确选择
        if activity_level not in activity_multipliers:
            raise ValueError("請選擇有效的活動水平")
        
        # 计算TDEE（总每日能量消耗）
        tdee = bmr * activity_multipliers.get(activity_level, 1.9)

        # 显示计算结果
        bmr_var.set(f"BMR: {bmr:.2f} kcal")
        tdee_var.set(f"TDEE: {tdee:.2f} kcal")
        root.update()
        group1.update()

    except ValueError:
        # 错误处理：输入值无效
        messagebox.showerror("錯誤", "請輸入有效的數字")

# Activity calculation function

# 更新主窗口的界面，加入两个标签用于展示video1、video2的YOLOv8影片
# 该函数用于更新视频帧，持续读取并显示视频的每一帧

def play_fixed_video(video_path, label):
    # 打开固定路径的视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    def update_frame():
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return

        # 转换帧为 Tkinter 可用的格式
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)

        # 更新标签以显示新帧
        label.config(image=photo)
        label.image = photo
        # 继续更新帧
        label.after(30, update_frame)  # 每30ms更新一次帧

    update_frame()

# 计算活动卡路里和总卡路里
def calculate_activities(activity1, video1, activity2, video2, activity3_text, burn3_text):
    # Set default results for each activity
    result1 = 0.0
    result2 = 0.0
    result3 = 0.0
    def calculate_1(activity1, video1):
        if  activity1 and video1:
            # cap = cv2.VideoCapture(0)  # Open the default camera (source=0)
            cap = cv2.VideoCapture(video1)
            assert cap.isOpened(), "Error reading video file"
        
            w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
            #new_fps = 30 
            video_writer = cv2.VideoWriter("count_yolov8_v1.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)) 
       
            def calculate_angle(a,b,c):
                a = np.array(a) # First
                b = np.array(b) # Mid
                c = np.array(c) # End
    
                radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                angle = np.abs(radians*180.0/np.pi)
    
                if angle >180.0:
                    angle = 360-angle
                return angle 

            # Curl counter variables
            counter = 0 
            stage = None

            ## Setup mediapipe instance
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        print("无法读取视频帧或视频流已结束")
                        break 
                    # Recolor image to RGB
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
      
                    # Make detection
                    results = pose.process(image)
    
                    # Recolor back to BGR
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
                    # Extract landmarks
                    try:
                        landmarks = results.pose_landmarks.landmark
            
                        # Get coordinates
                        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
 
                        # Calculate angle # elbow
                        # target = elbow            
                        # angle = calculate_angle(shoulder, target, wrist)

                        # Calculate angle # hip
                        target = shoulder
                        angle = calculate_angle(hip, target, elbow)

                        # Curl counter logic
                        if angle > 70:
                            stage = "up"
                        if angle < 30 and stage =='up':
                            stage="down"
                            counter +=1
                            print(counter)

                        # Visualize angle
                        # Adjust text color based on angle
                        if angle > 90:
                            color = (0, 0, 255)  # Red for large angles
                        else:
                            color = (120, 120, 120)  # Grey for smaller angles
                        cv2.putText(image, str(angle), 
                                        tuple(np.multiply(target, [640, 480]).astype(int)), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA
                                            )

                        # # Curl counter logic
                        # if angle > 160:
                        #     stage = "down"
                        # if angle < 30 and stage =='down':
                        #     stage="up"
                        #     counter +=1
                        #     print(counter)
 
                    except:
                        pass
        
                    # Render curl counter
                    # Setup status box
                    cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        
                    # Rep data
                    cv2.putText(image, 'REPS', (15,12), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(counter), 
                                (10,60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
                    # Stage data
                    cv2.putText(image, 'STAGE', (120,12), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, stage, 
                                (120,60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

        
                    # Render detections (Adjust drawing position)
                    mp_drawing.draw_landmarks(
                                        image, 
                                        results.pose_landmarks, 
                                        mp_pose.POSE_CONNECTIONS,  # 连接线
                                        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),  # 关键点样式
                                        connection_drawing_spec=mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)  # 连接线样式
                                    )
                
                    cv2.imshow('Mediapipe Feed', image)
                    video_writer.write(image)

                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break

            cap.release()
            video_writer.release()
            cv2.destroyAllWindows()

        
            result1 = counter * 0.4
            return result1 

        else:
            result1 = 0.0

    def calculate_2(activity2, video2):    
        if activity2 and video2:
            result2 = 100.0  # Example value
            return result2
        else:
            result2 = 0.0
    
    
     # 处理活动3和消耗热量

    def calculate_activity3_and_burn(activity3_text, burn3_text):
        # 获取用户输入的运动项
        #activity3 = activity3_entry.get("1.0", "end-1c")  # 获取从第1行第0个字符开始到末尾的输入内容，去除最后的换行符
        #burn3 = burn3_entry.get("1.0", "end-1c")  # 获取对应的消耗热量

        # 分行处理输入数据
        activity_lines = [line.strip() for line in activity3_text.splitlines() if line.strip()]
        burn_lines = [line.strip() for line in burn3_text.splitlines() if line.strip()]

        # 检查运动项和消耗热量的数量是否一致
        if len(activity_lines) != len(burn_lines):
            tk.messagebox.showerror("Error", "運動項目和消耗熱量的數量不匹配！")
            return 0.0
    
        burn_values = []

        for burn in burn_lines:
            try:
                burn_value = float(burn)  # 转换消耗热量为浮点数
                burn_values.append(burn_value)
            except ValueError:
                print(f"無效的熱量數值: {burn}")

        # 计算总消耗热量
        result3  = sum(burn_values) if burn_values else 0.0

        # 显示计算结果
        print(f"總消耗熱量: {result3 }")
        #tk.messagebox.showinfo("計算結果", f"總消耗熱量: {result3 } kcal")
        return result3
    
    result1 = calculate_1(activity1, video1)
    result2 = calculate_2(activity2, video2)
    result3 = calculate_activity3_and_burn(activity3_text, burn3_text)
    total = result1 + result2 + result3 
    
    return round(result1, 2), round(result2, 2), round(result3, 2), round(total, 2)

def cal_button_clicked():
    activity1 = activity1_var.get()
    video1 = video1_entry.get()
    activity2 = activity2_var.get()
    video2 = video2_entry.get()
    activity3_text = activity3_entry.get("1.0", tk.END).strip()
    burn3_text = burn3_entry.get("1.0", tk.END).strip()
    
    result1, result2, result3, total = calculate_activities(activity1, video1, activity2, video2, activity3_text, burn3_text)
    
    result1_var.set(result1)
    result2_var.set(result2)
    result3_var.set(result3)
    total_var.set(total)

def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)




# 食物计算函数
def calculate_food():
    try:
        tdee_float = float(tdee_var.get().split(":")[1].split()[0])  # 临时变量保存浮点值
        total_str = total_var.get()
        total_float = float(total_str)
        selected_meals = [meal for meal, var in meal_vars.items() if var.get()]
        selected_drinks = [drink for drink, var in drink_vars.items() if var.get()]

        cost = sum(food_data['meals'].get(meal, 0) for meal in selected_meals) + sum(food_data['drinks'].get(drink, 0) for drink in selected_drinks)

        total_have = tdee_float + total_float 
        less = total_have - cost
        
        total_have.set(f"一日消耗(kcal): {total_have:.2f}")
        cost_var.set(f"攝取卡路里(kcal): {cost:.2f}")
        less_var.set(f"剩下卡路里(kcal): {less:.2f}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字")

def create_checkbuttons(frame, options, columns= 8, var_dict=None):

    for index, option in enumerate(options):
        row = index // columns  # 计算行数
        column = index % columns  # 计算列数
        var = tk.BooleanVar()
        if var_dict is not None:
            var_dict[option] = var
        tk.Checkbutton(frame, text=option, variable=var, bg='#E7D4B5', fg='#603F26', font=('Arial', 9)).grid(row=row, column=column, padx=5, pady=5, sticky='w')


# 创建主窗口
root = tk.Tk()
root.title("卡路里計算器")
root.configure(background='#A0937D')

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 设置窗口宽度为屏幕宽度的 2/3，窗口高度为全屏高度
window_width = int(screen_width * 2 / 3)
window_height = screen_height

# 设置窗口大小与屏幕大小相同
root.geometry(f"{screen_width}x{screen_height}+0+0")


# 设置行和列的权重，使窗口可以自动调整大小
root.grid_rowconfigure(0, weight=1)  # 第一行权重为1
root.grid_rowconfigure(1, weight=1)  # 第二行权重为1
root.grid_columnconfigure(0, weight=1)  # 第一列权重为1
root.grid_columnconfigure(1, weight=1)  # 第二列权重为1


# BMR/TDEE 部分

group1 = tk.LabelFrame(root, text='BMR/TDEE', padx=20, pady=20, background='#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'), relief = 'raised',bd = 2, width = screen_width/2 , height =  screen_height/2)
group1.grid(row=0, column=0, sticky='nsew')



tk.Label(group1, text="年齡(歲):", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=0, column=0, sticky='w')
age_entry = tk.Entry(group1)
age_entry.grid(row=0, column=1)

tk.Label(group1, text="身高(公分):", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=1, column=0, sticky='w')
height_entry = tk.Entry(group1)
height_entry.grid(row=1, column=1)

tk.Label(group1, text="體重(公斤):", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=2, column=0, sticky='w')
weight_entry = tk.Entry(group1)
weight_entry.grid(row=2, column=1)

tk.Label(group1, text="性別:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=3, column=0, sticky='w')
gender_var = tk.StringVar(value="男")
tk.Radiobutton(group1, text="男", bg = '#E7D4B5',fg = '#603F26', font= ('Arial',9,'bold'), variable=gender_var, value="男",anchor = 'w').grid(row=3, column=1, sticky = 'w')
tk.Radiobutton(group1, text="女", bg = '#E7D4B5',fg = '#603F26', font= ('Arial',9,'bold'), variable=gender_var, value="女",anchor = 'w').grid(row=3, column=2, sticky = 'w')

tk.Label(group1, text="活動量:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=4, column=0, sticky='w')
activity_level_var = tk.StringVar(value="無活動：久坐")
activity_level_menu = tk.OptionMenu(group1, activity_level_var, "無活動：久坐", "輕量活動：每周運動1-3天(輕鬆)", "中度活動量：站走稍多、每周運動3-5天（中強度）", "高度活動量：站走為主、每周運動6-7天（高強度）", "非常高度活動量") 
activity_level_menu.config  (bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'))
activity_level_menu.grid(row=4, column=1, sticky='w')

bmr_var = tk.StringVar(value="")
tk.Label(group1, textvariable=bmr_var, bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=5, column=0, columnspan=2, sticky='w')

tdee_var = tk.StringVar(value="")
tk.Label(group1, textvariable=tdee_var, bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=6, column=0, columnspan=2, sticky='w')

tk.Button(group1, text="Calculate BMR/TDEE", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), command=calculate_bmr_tdee).grid(row=9, column=0, columnspan=2)



# 创建用于显示视频的LabelFrame（带边框的容器）
group_videos = tk.LabelFrame(root, text='影像回顧', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2, width = screen_width/2 , height =  screen_height/2)
group_videos.grid(row=1, column=1, sticky='nsew')  # 布局，放置在网格的第2行，第0列

# 创建视频2的标签及显示区域
tk.Label(group_videos, text="YOLOv8 Video1 :", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=0, column=0)
video1_label = tk.Label(group_videos)  # 用于显示视频1的帧
video1_label.grid(row=0, column=1)  # 放置在网格的第1行，第0列

# 播放固定视频
fixed_video_path_1 = 'count_yolov8_v1.avi'  # 替换为你的固定视频路径
tk.Button(group_videos, text="Play Fixed Video 1", command=lambda: play_fixed_video(fixed_video_path_1, video1_label), bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=1, column=1, sticky='e')

fixed_video_path_2 = 'count_yolov8_v1.avi'  # 替换为你的固定视频路径
tk.Button(group_videos, text="Play Fixed Video 2", command=lambda: play_fixed_video(fixed_video_path_2, video1_label), bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=1, column=2, sticky='e')



#Activity
group2 = tk.LabelFrame(root, text='Activity', padx=20, pady=20, background='#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'), relief = 'raised',bd = 2, width = screen_width/2 , height =  screen_height/2)
group2.grid(row=1, column=0, sticky='nsew')

# 初始化变量
tdee_var = tk.StringVar()
total_have = tk.StringVar(value="一日消耗(kcal): 0")
cost_var = tk.StringVar(value="攝取卡路里(kcal): 0")
less_var = tk.StringVar(value="剩下卡路里(kcal): 0")

exercise_entries = []  # 存储所有运动的输入框
# Activity 1
tk.Label(group2, text="運動1:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=0, column=0)
activity1_var = tk.StringVar()
activity1_menu = tk.OptionMenu(group2, activity1_var, "跳繩", "跳舞", "深蹲有氧", "開合跳", "仰臥起坐", "伏地挺身")
activity1_menu.config  (bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'))
activity1_menu.grid(row=0, column=1)

tk.Label(group2, text="Video 1:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=1, column=0)
video1_entry = tk.Entry(group2)
video1_entry.grid(row=1, column=1)
tk.Button(group2, text="Browse", command=lambda: browse_file(video1_entry), bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=1, column=2)

# Activity 2
tk.Label(group2, text="運動2:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=2, column=0)
activity2_var = tk.StringVar()
activity2_menu = tk.OptionMenu(group2, activity2_var, "跳繩", "跳舞", "深蹲有氧", "開合跳", "仰臥起坐", "伏地挺身")
activity1_menu.config  (bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'))
activity2_menu.grid(row=2, column=1)

tk.Label(group2, text="Video 2:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=3, column=0)
video2_entry = tk.Entry(group2)
video2_entry.grid(row=3, column=1)
tk.Button(group2, text="Browse", command=lambda: browse_file(video2_entry), bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=3, column=2)

# Activity 3
tk.Label(group2, text="運動3(每行一項運動):", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=4, column=0)
activity3_entry = tk.Text(group2, height=4, width=20)  # 创建一个文本框用于输入运动项，每行一个
activity3_entry.grid(row=4, column=1)

tk.Label(group2, text="消耗熱量(每行對應運動消耗):", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=5, column=0)
burn3_entry = tk.Text(group2, height=4, width=20)  # 创建一个文本框用于输入每项运动的消耗热量，每行一个
burn3_entry.grid(row=5, column=1)

# Results
result1_var = tk.StringVar()
tk.Label(group2, text="結果 1:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=6, column=0)
tk.Entry(group2, textvariable=result1_var).grid(row=6, column=1)

result2_var = tk.StringVar()
tk.Label(group2, text="結果 2:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=7, column=0)
tk.Entry(group2, textvariable=result2_var).grid(row=7, column=1)

result3_var = tk.StringVar()
tk.Label(group2, text="結果 3:", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=8, column=0)
tk.Entry(group2, textvariable=result3_var).grid(row=8, column=1)

total_var = tk.StringVar()
tk.Label(group2, text="運動消耗卡路里(kcal):", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=9, column=0)
tk.Entry(group2, textvariable=total_var).grid(row=9, column=1)


tk.Button(group2, text="Calculate", command=cal_button_clicked, bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=10, column=1)


# Food 部分
group3 = tk.LabelFrame(root, bg='#A0937D', text='Food', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2, width = screen_width/2 , height =  screen_height/2)
group3.grid(row=0, column=1, sticky='nsew')

# 主餐部分
group3_1 = tk.LabelFrame(group3, text='主餐', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2)
group3_1.grid(row=0, column=0, padx=10, pady=10, sticky='w')

meal_vars = {}  # 存储主餐 Checkbutton 的变量

tk.Label(group3_1, text="主餐:", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w')
create_checkbuttons(group3_1, food_data["meals"], columns=3, var_dict=meal_vars)

# 饮料部分
group3_2 = tk.LabelFrame(group3, text='饮料', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2)
group3_2.grid(row=0, column=1, padx=10, pady=10, sticky='w')

drink_vars = {}
for drink in food_data["drinks"]:
    var = tk.BooleanVar()
    tk.Checkbutton(group3_2, text=drink, variable=var, bg='#E7D4B5', fg='#603F26', font=('Arial', 9)).pack(anchor='w')
    drink_vars[drink] = var


total_have = tk.StringVar(value="")
tk.Label(group3, textvariable=total_have, bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=2, column=0, columnspan=2, sticky='w')
cost_var = tk.StringVar(value="")
tk.Label(group3, textvariable=cost_var, bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=2, column=0, columnspan=2, sticky='w')
less_var = tk.StringVar(value="")
tk.Label(group3, textvariable=less_var, bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=3, column=0, columnspan=2, sticky='w')

tk.Button(group3, text="Calculate Food", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), command=calculate_food).grid(row=0, column=2, columnspan=2)
root.mainloop()

