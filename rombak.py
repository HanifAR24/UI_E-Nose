#!/usr/bin/env python3
import serial
import time
# Import the GPIO module compatible with Raspberry Pi and Windows
# import gpiozero
# import RPi.GPIO as GPIO
import platform
# from fake_rpi.RPi import GPIO

# Periksa apakah platform adalah Raspberry Pi atau Windows
# if platform.system() == "Linux":
#     import RPi.GPIO as GPIO
# else:
#     # Impor fake_rpi untuk Windows
#     from fake_rpi.RPi import GPIO
# import tkinter as Tk
# from tkinter import PhotoImage
# import my_module
import logging
from datetime import datetime
#import joblib
#from sklearn import preprocessing
#from sklearn.preprocessing import MinMaxScaler
#from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import requests
import json
import os
import threading
running = False

dir_path = os.path.dirname(os.path.realpath(__file__))
global df
#df = pd.DataFrame(columns=['MQ135','MQ5','MQ8','Humidity','Temperature'])
df = pd.DataFrame(columns=['MQ3','TGS822','TGS2602','MQ5','MQ138','Humidity','Temperature'])
global status_sampling
#status = 'Not connected'

#Port Serial
port = 'COM11'
status_sampling = False

#model_file1 = dir_path+'/model/e-nose_meat_classification_model.sav'
#global classifier
#classifier = joblib.load(model_file1)

#model_file2 = dir_path+'/model/e-nose_meat_regression_model.sav'
#global regressor
#regressor = joblib.load(model_file2)

from tkinter import *
import tkinter as tk

ser = serial.Serial('COM5', 9600)

def inhale():
    ser.write(bytes('1', 'utf-8'))
   
def exhale():
    ser.write(bytes('2', 'utf-8'))

def stop():
    ser.write(bytes('3', 'utf-8'))
    
def restart():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)

def shutdown():
    command = "/usr/bin/sudo /sbin/shutdown now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)

def connect_serial(port):
    try:
        if __name__ == '__main__':
            global status
            global ser
            ser = serial.Serial(port, 9600, timeout=1)
            ser.reset_input_buffer()
            status = 'Connected'
    except:
        status = 'Not connected'

connect_serial(port)
print(status)

# def relay_manual(action, gpio_port):
#     # Selecting which GPIO to target
#     GPIO_CONTROL = gpio_port

#     if action == "on":

#         # Sleeping for a second
#         time.sleep(1)

#         # We will be using the BCM GPIO numbering
#         GPIO.setmode(GPIO.BOARD)

#         # Set CONTROL to OUTPUT mode
#         GPIO.setup(GPIO_CONTROL, GPIO.OUT)

#         #Starting the relay
#         GPIO.output(GPIO_CONTROL, False)

#         #Logging the event
#         logging.basicConfig(format='%(asctime)s %(message)s', filename='events.log', level=logging.INFO)
#         logging.info('Relay has been manually switched on, from functions.py')

#     elif action == "off":

#         try:
#             #Stopping the relay
#             GPIO.output(GPIO_CONTROL, False)

#         except:
#             # We will be using the BCM GPIO numbering
#             GPIO.setmode(GPIO.BOARD)

#             # Set CONTROL to OUTPUT mode
#             GPIO.setup(GPIO_CONTROL, GPIO.OUT)

#             #Starting the relay
#             GPIO.output(GPIO_CONTROL, False)
#         finally:
#            GPIO.cleanup() # cleanup all GPIO 

#         #Logging the event
#         logging.basicConfig(format='%(asctime)s %(message)s', filename='events.log', level=logging.INFO)
#         logging.info('Relay has been manually switched off, from functions.py')

def getTime():
    # datetime object containing current date and time
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H-%M-%S") 
    return dt_string

def getLabel(x):
    if(x==1):
        res='excellent'
    elif(x==2):
        res='good'
    elif(x==3):
        res='acceptable'
    else:
        res='spoiled'
    return res

def getSensorData(text):
    mq3=0
    tgs822=0
    tgs2602=0
    mq5=0
    mq138=0
    humidity=0
    temperature=0
    tgs2620 = 0
    
    x = text.split('@')
    #print(x)
    for i in x:
        #print(i)
        y = i.split(':')
        #print(y)
        if y[0]=='Rs_mq3':
            mq3 = float(y[1])
        elif y[0]=='Rs_tgs822':
            tgs822 = float(y[1])
        elif y[0]=='Rs_tgs2602':
            tgs2602 = float(y[1])
        elif y[0]=='Rs_mq5':
            mq5 = float(y[1])
        elif y[0]=='Rs_mq138':
            mq138 = float(y[1])
        elif y[0]=='Humidity':
            humidity = float(y[1])
        elif y[0]=='Temperature':
            temperature = float(y[1])
        elif y[0]=='Rs_tgs2620':
            tgs2620 = float(y[1])
    #print(mq135)
    #print(mq5)
    #print(mq8)
    
    #data = {'MQ135':[mq135],'MQ5':[mq5],'MQ8':[mq8], 'Humidity':[humidity], 'Temperature':[temperature]}
    
    #masih perlu diganti karena sensor belum lengkap 
    data = {'MQ3':[mq3],'TGS822':[tgs822],'TGS2602':[tgs2602],'MQ5':[mq5], 'MQ138':[mq138], 'TGS2620':[tgs2620]}

    #temp = [mq135,mq5,mq8]
    df = pd.DataFrame(data)
    return df

def sinkronisasi_tvc(kelas, tvc):
    if kelas=='excellent':
        if tvc > 3:
            tvc = 2.99
    elif kelas=='good':
        if tvc < 3 or tvc > 4:
            tvc = 3.99
    elif kelas=='acceptable':
        if tvc < 4 or tvc > 5:
            tvc = 4.99
    elif kelas == 'spoiled':
        if tvc < 5:
            tvc = 5.0
    return tvc
        
def predicting():
    status_sample["text"] = 'loading...'
    tvc["text"] = 'loading...'
    sysLog.insert(0.0,'mulai predicting - '+getTime()+'\n')
    status_sampling = True
    #relay_manual("off",16)
    #relay_manual("off",18)

    sysLog.insert(0.0,'menyedot gas - '+getTime()+'\n')
    
    #relay_manual("on",16)
    time.sleep(30)
    #relay_manual("off",16)
    print("step 1 finished - suck air sample")
    time.sleep(10)
    pred = prediction()
    print("pred:",pred)
    sysLog.insert(0.0,'membersihkan gas - '+getTime()+'\n')
    
    #relay_manual("on",18)
    time.sleep(30)
    #relay_manual("off",18)
    
    print("step 2 finished - flush air")
    sysLog.insert(0.0,'akhir sampling - '+getTime()+'\n')
    status_sampling = False

def flushing():
    #status_sample["text"] = 'loading...'
    #tvc["text"] = 'loading...'
    global running
    running = True
    sysLog.insert(0.0,'mulai flushing - '+getTime()+'\n')
    sysLog.insert(0.0,'menyedot gas - '+getTime()+'\n')
    inhale()
    time.sleep(60)
    sysLog.insert(0.0,'membersihkan gas - '+getTime()+'\n')
    exhale()
    time.sleep(60)
    print("step 2 finished - flush air")
    stop()
    time.sleep(10)
    sysLog.insert(0.0,'akhir flushing - '+getTime()+'\n')
    running = False

def testing():
    print("testing")
    
def prediction():
    # load the model from disk
    # klasifikasi
    #model_file = dir_path+'/model/e-nose_meat_classification_model.sav'
    #data_file = pd.read_csv(dir_path+'/dataset/dataset.csv')

    #Label(leftFrame, text='                      ', font=("Arial", 15),fg="#0000FF")
    #Label(leftFrame, text='-', font=("Arial", 15),fg="#0000FF")
    #status_sample.grid(row=2, column=0, padx=10, pady=2)

    #Label(leftFrame, text="Prediksi Nilai TVC:", font=("Arial", 15)).grid(row=3, column=0, padx=10, pady=2)
    #tvc = Label(leftFrame, text='                      ', font=("Arial", 15),fg="#0000FF")
    #tvc = Label(leftFrame, text='-', font=("Arial", 15),fg="#0000FF")
    #tvc.grid(row=4, column=0, padx=10, pady=2)

    status_sample.pack_forget()
    tvc.pack_forget()
    
    global line
    #df = pd.DataFrame(columns=['MQ135','MQ5','MQ8','Humidity','Temperature'])
    df = pd.DataFrame(columns=['MQ136','MQ137','MQ5','MQ8','Humidity','Temperature'])
    if(ser):
        sysLog.insert(0.0,'Membaca data sensor...'+'\n')
        count = 0
        while (count<=60):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                #print(line)
                #if not status_sampling:
                    #sysLog.insert(0.0,'read sensors data - '+getTime()+'\n')
                    #sysLog.insert(0.0,line+'\n')
                df = df.append(getSensorData(line), ignore_index=True)
                print('df:',df)
                data = line.split('@')
                #sysLog.insert(0.0,data[1]+','+data[2]+','+data[3]+','+data[4]+','+data[5]+'\n')
                #sysLog.insert(0.0,'Membaca data sensor '+str(count)+'\n')
                #print(data[1],'-',data[2])
                Label(rightFrame, text=data[1], font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=2)
                Label(rightFrame, text=data[2], font=("Arial", 12)).grid(row=1, column=1, padx=10, pady=2)
                Label(rightFrame, text='Last data: '
                      +getTime()
                      ,font=("Arial", 10)).grid(row=2, column=0, columnspan=2, padx=10, pady=2)
                #vhumid["text"] = str(data[1])
                #vtempe["text"] = str(data[2])
                #vlastdata["text"] = 'Last data:'+getTime()
                count=count+1
                root.update()
    df = df.iloc[1: , :]
    #df = df.iloc[-1:] 
    #print('df:',df)
    #mq135=df['MQ135'].mean(axis=0)
    mq136=df['MQ136'].mean(axis=0)
    mq137=df['MQ137'].mean(axis=0)
    mq5=df['MQ5'].mean(axis=0)
    mq8=df['MQ8'].mean(axis=0)
    humidity=df['Humidity'].mean(axis=0)
    temperature=df['Temperature'].mean(axis=0)
    #data = {'MQ135':[mq135],'MQ5':[mq5],'MQ8':[mq8], 'Humidity':[humidity], 'Temperature':[temperature]}
    data = {'MQ136':[mq136],'MQ137':[mq137],'MQ5':[mq5],'MQ8':[mq8], 'Humidity':[humidity], 'Temperature':[temperature]}
    data_file = pd.DataFrame(data)
    #print('data_file:',data_file)
    #features = data_file.loc[:,{'MQ135','MQ5','MQ8'}]
    
    endpoint = 'https://ais-research.telkomuniversity.ac.id:8080/enose_seafood'
    features = data_file.loc[:,['MQ136','MQ137','MQ5','MQ8']]
    
    x_new = (features.loc[:, ['MQ136','MQ137','MQ5','MQ8']])
    x_new=x_new.values.tolist()
    # Convert the array to a serializable list in a JSON document
    input_json = json.dumps({"data": x_new})
    headers = {'Content-Type':'application/json', 'x-access-token':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiI5OTRlZmIxNi01N2Y3LTQwZmItYTgyZi1kYmFhNGZiYTUwODEiLCJleHAiOjE2NjA5NzIyNjF9.oKQl5BMeQq1RGsHvqG2ROBn0Qb3iYyNpphOGZpG0oKk'}

    predictions = requests.post(endpoint, input_json, headers = headers)
    if predictions.ok:
        hasil = predictions.json()
        #print('respon hasil prediksi:',hasil)
        df_hasil = pd.DataFrame.from_dict(hasil, orient="index")
        print('Tabel hasil:')
        print(df_hasil)
        #df_hasil.to_excel('hasil_prediksi_endpoint.xlsx')
    else:
        print('gagal')
    #label = data_file['class']
    #print(features)


    # melakukan feature scaling
    #scaled_feature = StandardScaler().fit_transform(df.loc[:,{'MQ135','MQ5','MQ8'}])
    #scaled_feature = MinMaxScaler(feature_range=(0, 10)).fit_transform(df.loc[:,{'MQ135','MQ5','MQ8'}])
    #scaler = preprocessing.MinMaxScaler(feature_range=(0, 10)).fit(df.loc[:,{'MQ135','MQ5','MQ8'}])
    #scaled_feature = scaler.transform(features)
    #print('scaled_feature',scaled_feature)

    #print(features)
    #classifier = joblib.load(model_file)
    #print('model',loaded_model)
    
    #result1 = classifier.predict(scaled_feature)
    #result1 = pd.DataFrame(result1, columns=['class'])
    #result2 = np.round(regressor.predict(scaled_feature),decimals=2)
    #result2 = pd.DataFrame(result2, columns=['TVC'])
    
    #hasil = pd.concat([result1,result2], axis = 1)
    hasil=df_hasil
    print('hasil=',hasil)
    
    #status_sample = Label(leftFrame, text='                      ', font=("Arial", 15),fg="#0000FF")
    #status_sample = Label(leftFrame, text=getLabel(hasil['class'].iloc[-1]), font=("Arial", 15),fg="#0000FF")
    #status_sample.grid(row=2, column=0, padx=10, pady=2)
    #status_sample["text"] = getLabel(hasil['class'].iloc[-1])
    status_sample["text"] = hasil['class'].iloc[-1]


    #Label(leftFrame, text="Prediksi Nilai TVC:", font=("Arial", 15)).grid(row=3, column=0, padx=10, pady=2)
    #tvc = Label(leftFrame, text='                      ', font=("Arial", 15),fg="#0000FF")
    #tvc = Label(leftFrame, text=hasil['TVC'].iloc[-1], font=("Arial", 15),fg="#0000FF")
    #tvc.grid(row=4, column=0, padx=10, pady=2)
    #tvc["text"] = hasil['TVC'].iloc[-1]
    tvc["text"] = sinkronisasi_tvc(status_sample["text"],hasil['TVC'].iloc[-1])
    
    print(hasil)
    hasil.to_csv(dir_path+'/hasil.csv')
    #print(label)
    return hasil

#print('hasil:',prediction())
#Windows
#port = 'COM5'

def sample():
    status_sample.pack_forget()
    tvc.pack_forget()
    
    global line
    #df = pd.DataFrame(columns=['MQ135','MQ5','MQ8','Humidity','Temperature'])
    df = pd.DataFrame(columns=['MQ3','TGS822','TGS2602','MQ5','MQ138','TGS2620'])
    if(ser):
        sysLog.insert(0.0,'Membaca data sensor...'+'\n')
        count = 0
        while (count<=60):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                #print(line)
                #if not status_sampling:
                    #sysLog.insert(0.0,'read sensors data - '+getTime()+'\n')
                    #sysLog.insert(0.0,line+'\n')
                df = df.append(getSensorData(line), ignore_index=True)
                #print('df:',df)
                data = line.split('@')
                #sysLog.insert(0.0,data[1]+','+data[2]+','+data[3]+','+data[4]+','+data[5]+'\n')
                #sysLog.insert(0.0,'Membaca data sensor '+str(count)+'\n')
                #print(data[1],'-',data[2])
                Label(rightFrame, text=data[0], font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=2)
                Label(rightFrame, text=data[1], font=("Arial", 12)).grid(row=1, column=1, padx=10, pady=2)
                Label(rightFrame, text='Last data: '
                      +getTime()
                      ,font=("Arial", 10)).grid(row=2, column=0, columnspan=2, padx=10, pady=2)
                #vhumid["text"] = str(data[1])
                #vtempe["text"] = str(data[2])
                #vlastdata["text"] = 'Last data:'+getTime()
                count=count+1
                root.update()
    df = df.iloc[1: , :]
    return df

def batal():
    status_sampling = False
def start():
    if not running:
        threading.Thread(target=sampling, daemon=True).start()
def btnflush():
    if not running:
        threading.Thread(target=flushing, daemon=True).start()

def sampling():
    import datetime
    global running
    running = True
    #interval = int(samplingInterval.get("1.0","end"))*60
    status_sample["text"] = '-'
    tvc["text"] = '-'
    sysLog.insert(0.0,'mulai sampling - '+getTime()+'\n')
    status_sampling = True
    stop()
    #relay_manual("off",16)
    #relay_manual("off",18)
    time.sleep(3)
    sysLog.insert(0.0,'menyedot gas - '+getTime()+'\n')
    inhale()
        #relay_manual("on",16)
    time.sleep(60)
        #relay_manual("off",16)
    stop()
    print("step 1 finished - suck air sample")
    time.sleep(20)
        
    sysLog.insert(0.0,'mengambil data - '+getTime()+'\n')
    count = 0
    while (count<=20):
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        count += 1
        time.sleep(1)
    sampling = sample()
    #sampling.to_csv(dir_path+'\sampling_'+str(datetime.datetime.now())+'.csv')
    #sampling.to_csv('sampling_'+str(datetime.datetime.now())+'.csv')
    sampling.to_csv('sampling_'+getTime()+'.csv')
    time.sleep(5)
    sysLog.insert(0.0,'membersihkan gas - '+getTime()+'\n')

    exhale()    
    time.sleep(70)
    stop()
    running = False
        
    print("step 2 finished - flush air")
    sysLog.insert(0.0,'akhir sampling - '+getTime()+'\n')
    if status_sampling == False:
        sysLog.insert(0.0,'sampling dibatalkan - '+getTime()+'\n')
        stop()
        running = False
        #time.sleep(interval)


root = Tk() #Makes the window
stop()
root.wm_title("TNOSE") #Makes the title that will appear in the top left
#root.config(background = "#666699")
root.geometry("1024x600")
#root.geometry("1024x768")
root.resizable(0, 0) #Don't allow resizing in the x or y direction
root.grid_columnconfigure(0,weight=1)
root.attributes('-fullscreen', False)

back = tk.Frame(master=root)
back.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
#back.pack(fill=tk.BOTH, expand=1) #Expand the frame to fill the root window

def Close():
    stop()
    root.destroy()

#Top Frame and its contents
#topFrame = Frame(root, width=100, height=40, bg="#58F")
#topFrame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
#Label(topFrame, text="Top:").grid(row=0, column=0, padx=10, pady=2)

#relay_manual("off",16)
#relay_manual("off",18)

#Left Frame and its contents
leftFrame = Frame(root, width=150, height = 500)
leftFrame.grid(row=0, column=0, padx=5, pady=2, sticky='ew')
Label(leftFrame, text="Prediksi Sampel:", font=("Arial", 13)).grid(row=1, column=0, padx=10, pady=2)
Label(leftFrame, text="Nilai TVC Terakhir:", font=("Arial", 13)).grid(row=3, column=0, padx=10, pady=2)

#status_sample = Label(leftFrame, text='                      ', font=("Arial", 15),fg="#0000FF")
status_sample = Label(leftFrame, text='-', font=("Arial", 13),fg="#0000FF")
status_sample.grid(row=2, column=0, padx=10, pady=2)

#Label(leftFrame, text="Prediksi Nilai TVC:", font=("Arial", 15)).grid(row=3, column=0, padx=10, pady=2)
#tvc = Label(leftFrame, text='                      ', font=("Arial", 15),fg="#0000FF")
tvc = Label(leftFrame, text='-', font=("Arial", 13),fg="#0000FF")
tvc.grid(row=4, column=0, padx=10, pady=2)

Label(leftFrame, text="Sampling Interval (menit):", font=("Arial", 10)).grid(row=5, column=0, padx=1, pady=2)
samplingInterval = Text(leftFrame, width = 5, height = 1, takefocus=0, bg="white", fg="blue")
samplingInterval.grid(row=6, column=0, padx=1, pady=2)
samplingInterval.insert(0.0, "2")

#print(samplingInterval.get("1.0","end"))

rightFrame = Frame(root, width=600, height=480)
rightFrame.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
try:
    sysLog = Text(rightFrame, width = 50, height = 17, takefocus=0, bg="white", fg="blue")
    sysLog.grid(row=3, column=0, padx=5, pady=2, columnspan=2)
    imageEx = PhotoImage(file = dir_path+'/image/t-nose.gif')
    Label(leftFrame, image=imageEx).grid(row=0, column=0, padx=10, pady=2)
except:
    sysLog.insert(0.0, "Gambar tidak ditemukan")
    
#status_sample = Label(leftFrame, text="Excellent\n", font=("Arial", 15),fg="#0000FF")
#status_sample.grid(row=2, column=0, padx=10, pady=2)


##Label(leftFrame, text="Nilai TVC Terakhir:", font=("Arial", 15)).grid(row=3, column=0, padx=10, pady=2)
##tvc = Label(leftFrame, text="3.45", font=("Arial", 15),fg="#0000FF")
##tvc.grid(row=4, column=0, padx=10, pady=2)

#Right Frame and its contents
rightFrame = Frame(root, width=600, height = 480)
rightFrame.grid(row=0, column=1, padx=5, pady=2, sticky='ew')


#circleCanvas = Canvas(rightFrame, width=100, height=100, bg='white')
#circleCanvas.grid(row=0, column=0, padx=10, pady=2)

Label(rightFrame, text="System Status:"+status, font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=2, columnspan=1)
#Label(rightFrame, text=status, font=("Arial", 15)).grid(row=1, column=0, padx=10, pady=2, columnspan=2)
##Label(rightFrame, text="Suhu:", font=("Arial", 15)).grid(row=1, column=0, padx=10, pady=2)
##Label(rightFrame, text="Kelembaban:", font=("Arial", 15)).grid(row=1, column=1, padx=10, pady=2)
btnFrame = Frame(root, width=1000, height = 200)
btnFrame.grid(row=3, column=0, padx=5, pady=2, columnspan=2)

vhumid = Label(rightFrame, text='Humidity: -', font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=2)
vtempe = Label(rightFrame, text='Temperature: -', font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=2)
vlastdata = Label(rightFrame, text='Last data:',font=("Arial", 10)).grid(row=3, column=0, columnspan=2, padx=10, pady=2)



#predictingBtn = Button(btnFrame, text="Predicting", command=predicting, height=3)
#predictingBtn.grid(row=0, column=0, padx=5, pady=2)
#settingBtn.pack(side=TOP, anchor=W, fill=X, expand=YES)

samplingBtn = Button(leftFrame, text="Sampling", command=sampling, height=3)
samplingBtn.grid(row=8, column=0, padx=1    , pady=2)
#settingBtn.pack(side=TOP, anchor=W, fill=X, expand=YES)

#restartBtn = Button(btnFrame, text="Restart", command=restart, height=3)
#restartBtn.grid(row=0, column=2, padx=5, pady=2)
#restartBtn.pack(side=TOP, anchor=W, fill=X, expand=YES)

#shutdownBtn = Button(btnFrame, text="Shutdown", command=shutdown, height=3)
#shutdownBtn.grid(row=0, column=3, padx=5, pady=2)
#shutdownBtn.pack(side=TOP, anchor=W, fill=X, expand=YES)

closebutton = Button(leftFrame, text="Close", command=Close, height=3)
closebutton.grid(row=9, column=4, columnspan=3, padx=5, pady=2)

flushingbutton = Button(leftFrame, text="Flushing", command=flushing, height=3)
flushingbutton.grid(row=8, column=1, padx=1, pady=2)

testingbutton = Button(leftFrame, text="Testing", command=testing, height=3)
testingbutton.grid(row=8, column=2, padx=1, pady=2)


sysLog = Text(rightFrame, width = 50, height = 17, takefocus=0, bg="white", fg="blue")
sysLog.grid(row=3, column=0, padx=5, pady=2, columnspan=2)

if status=='Connected':
    sysLog.insert(0.0,'system ready - '+getTime()+'\n')
else:
    sysLog.insert(0.0,'system not ready - '+getTime()+'\n')
#Label(rightFrame, text="Message:").grid(row=1, column=0, padx=10, pady=2)


root.mainloop() #start monitoring and updating the GUI
