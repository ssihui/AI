import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import json
from ultralytics import YOLO, solutions

model = YOLO("trained/yolov8n-pose.pt")

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

# 活动计算函数
def calculate_activity():
    # 处理视频和活动
    result1 = 0.0
    result2 = 0.0
    result3 = 0.0
    
    # Placeholder for video processing logic
    # For example purposes, we are not implementing the actual video processing here
    
    # Assuming results from video processing are obtained
    result1 = 100.0  # Replace with actual processing result
    result2 = 50.0   # Replace with actual processing result
    result3 = 30.0   # Replace with actual processing result

    total_result = result1 + result2 + result3
    result1_var.set(f"結果 1: {result1:.2f}")
    result2_var.set(f"結果 2: {result2:.2f}")
    result3_var.set(f"結果 3: {result3:.2f}")
    total_result_var.set(f"運動消耗卡路里(kcal): {total_result:.2f}")

# 食物计算函数
def calculate_food():
    try:
        total_have = float(tdee_var.get().split(":")[1].strip())
        cost = 0.0
        # Placeholder for food and drinks calculation
        # For example purposes, we are not implementing the actual calculation here
        cost = 200.0  # Replace with actual calculation result
        less = total_have - cost
        cost_var.set(f"攝取卡路里(kcal): {cost:.2f}")
        less_var.set(f"剩下卡路里(kcal): {less:.2f}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字")

# 创建主窗口
root = tk.Tk()
root.title("卡路里計算器")

# BMR/TDEE 部分

group1 = tk.LabelFrame(root, text='test', padx=10, pady=10)
tk.Label(group1, text="年齡(歲):").grid(row=0, column=0)
age_entry = tk.Entry(group1)
age_entry.grid(row=0, column=1)

tk.Label(group1, text="身高(公分):").grid(row=1, column=0)
height_entry = tk.Entry(group1)
height_entry.grid(row=1, column=1)

tk.Label(group1, text="體重(公斤):").grid(row=2, column=0)
weight_entry = tk.Entry(group1)
weight_entry.grid(row=2, column=1)

tk.Label(group1, text="性別:").grid(row=3, column=0)
gender_var = tk.StringVar(value="男")
tk.Radiobutton(group1, text="男", variable=gender_var, value="男").grid(row=3, column=1)
tk.Radiobutton(group1, text="女", variable=gender_var, value="女").grid(row=3, column=2)

tk.Label(group1, text="活動量:").grid(row=4, column=0)
activity_level_var = tk.StringVar(value="無活動：久坐")
activity_level_menu = tk.OptionMenu(group1, activity_level_var, "無活動：久坐", "輕量活動：每周運動1-3天(輕鬆)", "中度活動量：站走稍多、每周運動3-5天（中強度）", "高度活動量：站走為主、每周運動6-7天（高強度）", "非常高度活動量")
activity_level_menu.grid(row=4, column=1)

bmr_var = tk.StringVar(value="")
tk.Label(group1, textvariable=bmr_var).grid(row=5, column=0, columnspan=2)
tdee_var = tk.StringVar(value="")
tk.Label(group1, textvariable=tdee_var).grid(row=6, column=0, columnspan=2)

tk.Button(group1, text="Calculate BMR/TDEE", command=calculate_bmr_tdee).grid(row=7, column=0, columnspan=2)

# Activity 部分
tk.Label(root, text="活動1:").grid(row=8, column=0)
activity1_var = tk.StringVar(value="跳繩")
activity1_menu = tk.OptionMenu(root, activity1_var, "跳繩", "跳舞", "深蹲有氧", "開合跳", "仰臥起坐", "伏地挺身")
activity1_menu.grid(row=8, column=1)

tk.Label(root, text="上传视频1:").grid(row=9, column=0)
video1_button = tk.Button(root, text="选择视频", command=lambda: filedialog.askopenfilename())
video1_button.grid(row=9, column=1)

tk.Label(root, text="活动2:").grid(row=10, column=0)
activity2_var = tk.StringVar(value="跳繩")
activity2_menu = tk.OptionMenu(root, activity2_var, "跳繩", "跳舞", "深蹲有氧", "開合跳", "仰臥起坐", "伏地挺身")
activity2_menu.grid(row=10, column=1)

tk.Label(root, text="上传视频2:").grid(row=11, column=0)
video2_button = tk.Button(root, text="选择视频", command=lambda: filedialog.askopenfilename())
video2_button.grid(row=11, column=1)

tk.Label(root, text="活动3:").grid(row=12, column=0)
activity3_entry = tk.Entry(root)
activity3_entry.grid(row=12, column=1)

tk.Label(root, text="消耗热量:").grid(row=13, column=0)
burn3_entry = tk.Entry(root)
burn3_entry.grid(row=13, column=1)

tk.Label(root, text="结果 1:").grid(row=14, column=0)
result1_var = tk.StringVar(value="0.0")
tk.Label(root, textvariable=result1_var).grid(row=14, column=1)

tk.Label(root, text="结果 2:").grid(row=15, column=0)
result2_var = tk.StringVar(value="0.0")
tk.Label(root, textvariable=result2_var).grid(row=15, column=1)

tk.Label(root, text="结果 3:").grid(row=16, column=0)
result3_var = tk.StringVar(value="0.0")
tk.Label(root, textvariable=result3_var).grid(row=16, column=1)

tk.Label(root, text="运动消耗卡路里(kcal):").grid(row=17, column=0)
total_result_var = tk.StringVar(value="0.0")
tk.Label(root, textvariable=total_result_var).grid(row=17, column=1)

tk.Button(root, text="Calculate Activity", command=calculate_activity).grid(row=18, column=0, columnspan=2)

# Food 部分
tk.Label(root, text="主餐:").grid(row=19, column=0)
selected_options_1 = tk.Listbox(root, selectmode=tk.MULTIPLE)
selected_options_1.grid(row=19, column=1)

tk.Label(root, text="饮料:").grid(row=20, column=0)
selected_options_2 = tk.Listbox(root, selectmode=tk)

root.mainloop()