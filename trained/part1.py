import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import json
from ultralytics import YOLO, solutions
from PIL import Image, ImageTk
import os

model = YOLO("trained/yolov8n-pose.pt")

# 读取 JSON 文件
def load_food_options():
    with open('food_options.json', 'r', encoding='utf-8') as file:
        return json.load(file)

food_data = load_food_options()

# BMR 计算函数
def calculate_bmr_tdee():
    try:
        age = float(age_entry.get())
        height = float(height_entry.get())
        weight = float(weight_entry.get())
        gender = gender_var.get()
        activity_level = activity_level_var.get()

        if gender == '男':
            bmr = (13.7 * weight) + (5 * height) - (6.8 * age) + 66
        else:
            bmr = (9.6 * weight) + (1.8 * height) - (4.7 * age) + 655

        activity_multipliers = {
            "無活動：久坐": 1.2,
            "輕量活動：每周運動1-3天(輕鬆)": 1.375,
            "中度活動量：站走稍多、每周運動3-5天（中強度）": 1.55,
            "高度活動量：站走為主、每周運動6-7天（高強度）": 1.725,
            "非常高度活動量": 1.9
        }
        tdee = bmr * activity_multipliers.get(activity_level, 1.9)

        bmr_var.set(f"BMR: {bmr:.2f}")
        tdee_var.set(f"TDEE: {tdee:.2f}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字")

# Activity calculation function
def cal(activity1, video1, activity2, video2, activity3, burn3 ):
    # Set default results for each activity
    result1 = 0.0
    result2 = 0.0
    result3 = 0.0

    if  activity1 and video1:
        # cap = cv2.VideoCapture(0)  # Open the default camera (source=0)
        cap = cv2.VideoCapture(video1)
        assert cap.isOpened(), "Error reading video file"
        
        w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
        #new_fps = 4 
        video_writer = cv2.VideoWriter("count_yolov8_v1.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)) 
       
        if '伏地挺身' in activity1 :
            gym_object = solutions.AIGym(
                line_thickness=2,
                view_img=True,
                pose_type="pushup",
                kpts_to_check=[6, 8, 10],
            )
            while cap.isOpened():
                success, im0 = cap.read()
                if not success:
                    print("Video frame is empty or video processing has been successfully completed.")
                    break
                results = model.track(im0, verbose=False)  # Tracking recommended
                # results = model.predict(im0)  # Prediction also supported
                im0 = gym_object.start_counting(im0, results)
                out_count = gym_object.count
                print(out_count)

                # Ensure the directory exists
                os.makedirs("json", exist_ok=True)
                try:
                    with open("json/save_data.json", "w") as f:
                         json.dump({"count": out_count}, f)
                    print("Results saved to JSON.") 
                except Exception as e:
                    print(f"Error saving JSON: {e}")
                video_writer.write(im0)
            cap.release()
            video_writer.release()
            
            # 讀取JSON檔案
            def load_result1():
                # 打開並讀取JSON文件
                    try:
                        with open('json/save_data.json', 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            count = data.get("count", 0)
                            # 如果 count 是列表，处理列表中的数据
                            if isinstance(count, list):
                                if len(count) == 0:
                                    raise ValueError("count list is empty")
                                else:
                                     # 这里我们假设要取列表的第一个元素
                                    count = count[0]
                                    print(f"count is a list, taking the first value: {count}")
             
                            # 确保 count 是数值类型，如果是字符串则尝试转换为浮点数
                            if isinstance(count, str):
                                try:
                                    count = float(count)
                                except ValueError:
                                    raise ValueError(f"Invalid string value for count: {count}")
                            elif not isinstance(count, (int, float)):
                                raise ValueError(f"Invalid data type for count: {type(count)}")
            
                            # 计算结果
                            result = 0.4 * count
                            return result
        
                    except Exception as e:
                        print(f"Error reading JSON: {e}")
                        return 0.0
            result1 = load_result1()
        else:
            result1 = 1000.0

        
    if activity2 and video2:
        result2 = 100.0  # Example value
    
    
     # 处理活动3和消耗热量
    if activity3 and burn3:
        # 将每行的输入分开，转换为浮点数，并计算总和
        activity_lines = [line.strip() for line in activity3.splitlines() if line.strip()]
        burn_lines = [line.strip() for line in burn3.splitlines() if line.strip()]

        if len(activity_lines) != len(burn_lines):
            raise ValueError("活动项和消耗热量的数量不匹配")  # 如果活动项和消耗热量数量不一致，抛出错误

        burn_values = []
        for burn in burn_lines:
            try:
                burn_value = float(burn)  # 转换消耗热量为浮点数
                burn_values.append(burn_value)
            except ValueError:
                print(f"Invalid burn value: {burn}")

        result3 = sum(burn_values) if burn_values else 0.0  # 计算总消耗热量

    return result3 
        

    total = result1 + result2 + result3 
    
    return round(result1, 2), round(result2, 2), round(result3, 2), round(total, 2)

def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)




# 食物计算函数
def calculate_food():
    try:
        total_have_float = float(tdee_var.get().split(":")[1].strip())  # 临时变量保存浮点值
        selected_meals = [meal for meal, var in meal_vars.items() if var.get()]
        selected_drinks = [drink for drink, var in drink_vars.items() if var.get()]

        cost = sum(food_data['meals'].get(meal, 0) for meal in selected_meals) + sum(food_data['drinks'].get(drink, 0) for drink in selected_drinks)

        less = total_have_float - cost
        total_have.set(f"一日消耗(kcal): {total_have_float:.2f}")
        cost_var.set(f"攝取卡路里(kcal): {cost:.2f}")
        less_var.set(f"剩下卡路里(kcal): {less:.2f}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字")

def create_checkbuttons(frame, options, columns= 8, var_dict=None):
    """
    在指定的 Frame 中创建 Checkbutton 组件，并根据固定列数进行排列。
    :param frame: 放置 Checkbutton 的 Frame
    :param options: Checkbutton 的选项列表
    :param columns: 每行的列数
    :param var_dict: 存储每个 Checkbutton 变量的字典
    """
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

# BMR/TDEE 部分

group1 = tk.LabelFrame(root, text='BMR/TDEE', padx=20, pady=20, background='#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'), relief = 'raised',bd = 2)
group1.grid(row=0, column=0)

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
tk.Label(group1, textvariable=bmr_var, bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=5, column=0, columnspan=2, sticky='w')
tdee_var = tk.StringVar(value="")
tk.Label(group1, textvariable=tdee_var, bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=6, column=0, columnspan=2, sticky='w')

tk.Button(group1, text="Calculate BMR/TDEE", bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'), command=calculate_bmr_tdee).grid(row=7, column=0, columnspan=2)


#Activity
group2 = tk.LabelFrame(root, text='Activity', padx=20, pady=20, background='#E7D4B5',fg = '#603F26', font=('Arial',9,'bold'), relief = 'raised',bd = 2)
group2.grid(row=1, column=0)

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
tk.Label(group2, text="運動3 /n(每行一項運動):", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=4, column=0)
activity3_entry = tk.Text(group2, height=4, width=30)  # 创建一个文本框用于输入运动项，每行一个
activity3_entry.grid(row=4, column=1)

tk.Label(group2, text="消耗熱量 /n(每行對應運動消耗):", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=5, column=0)
burn3_entry = tk.Text(group2, height=4, width=30)  # 创建一个文本框用于输入每项运动的消耗热量，每行一个
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

def calculate():
    activity1 = activity1_var.get()
    video1 = video1_entry.get()
    activity2 = activity2_var.get()
    video2 = video2_entry.get()
    activity3 = activity3_entry.get()
    burn3 = burn3_entry.get("1.0", tk.END).strip()
    
    result1, result2, result3, total = cal(activity1, video1, activity2, video2, activity3, burn3)
    
    result1_var.set(result1)
    result2_var.set(result2)
    result3_var.set(result3)
    total_var.set(total)

tk.Button(group2, text="Calculate", command=calculate, bg = '#E7D4B5',fg = '#603F26', font=('Arial',9,'bold')).grid(row=10, column=1)


# Food 部分
group3 = tk.LabelFrame(root, bg='#A0937D', text='Food', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2)
group3.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# 主餐部分
group3_1 = tk.LabelFrame(group3, text='主餐', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2)
group3_1.grid(row=0, column=0, padx=10, pady=10, sticky='w')

meal_vars = {}  # 存储主餐 Checkbutton 的变量

tk.Label(group3_1, text="主餐:", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w')
create_checkbuttons(group3_1, food_data["meals"], columns=8, var_dict=meal_vars)

# 饮料部分
group3_2 = tk.LabelFrame(group3, text='饮料', padx=20, pady=20, background='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), relief='raised', bd=2)
group3_2.grid(row=1, column=0, padx=10, pady=10, sticky='w')

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

tk.Button(group3, text="Calculate Food", bg='#E7D4B5', fg='#603F26', font=('Arial', 9, 'bold'), command=calculate_food).grid(row=4, column=0, columnspan=2)
root.mainloop()