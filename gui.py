from tkinter import *
from tkinter import messagebox as mb
from time import sleep, perf_counter
from guard import app
import threading
import subprocess
import re
import tkinter as tk

root = tk.Tk()

mainmenu = Menu(root) 
root.config(menu=mainmenu) 
 
helpmenu = Menu(mainmenu, tearoff=0)
helpmenu.add_command(label="Помощь")
helpmenu.add_command(label="О программе")
 
mainmenu.add_cascade(label="Справка",
                     menu=helpmenu)
                    

root.title("Программное средство")
root.geometry("395x100")
root.resizable(False, False)


def block_ip_button():


	def block():
		ip = source_entry.get()
		res = subprocess.run(['iptables', '-I', 'INPUT', '3', '-s', ip, '-j', 'DROP'])
		block_ip_window.destroy()
		block_ip_btn['state'] = 'normal'
		
		
	def unblock():
		ip = source_entry.get()
		res = subprocess.run(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'])
		block_ip_window.destroy()
		block_ip_btn['state'] = 'normal'


	block_ip_btn['state'] = 'disabled'
	block_ip_window = tk.Tk()
	block_ip_window.title("Блокировка IP")
	block_ip_window.geometry("305x100")
	
	source_label = tk.Label(block_ip_window, text="IP-адрес источника").grid(row=0, column=0)

	source_entry = tk.Entry(block_ip_window)
	source_entry.grid(row=0, column=1, columnspan=3, stick='we')

	btn = tk.Button(block_ip_window, text="Заблокировать", command=block).grid(row=1, column=0, columnspan=2, stick='we')
	btn = tk.Button(block_ip_window, text="Разблокировать", command=unblock).grid(row=1, column=2, columnspan=2, stick='we')
	

def block_TCP_MSS():
	if tcpmss_btn_text.get() == 'Включить фильтрацию mss':
		res = subprocess.run(['iptables', '-t', 'mangle', '-I', 'PREROUTING', '-p', 'tcp', '-m', 'tcp', '--dport', '80', '-m', 'state', '--state', 'NEW', '-m', 'tcpmss', '!', '--mss', '536:65535', '-j', 'DROP'])
		tcpmss_btn_text.set("Выключить фильтрацию mss")
	else:
			res = subprocess.run(['iptables', '-t', 'mangle', '-D', 'PREROUTING', '-p', 'tcp', '-m', 'tcp', '--dport', '80', '-m', 'state', '--state', 'NEW', '-m', 'tcpmss', '!', '--mss', '536:65535', '-j', 'DROP'])
			tcpmss_btn_text.set("Включить фильтрацию mss")
	
	
def block_icmp():
	if btn_icmp_text.get() == 'Заблокировать icmp':
		res = subprocess.run(['iptables', '-I', 'INPUT', '3', '-p', 'icmp', '-j', 'DROP'])
		btn_icmp_text.set("Разблокировать icmp")
	else:
		res = subprocess.run(['iptables', '-D', 'INPUT', '-p', 'icmp', '-j', 'DROP'])
		btn_icmp_text.set("Заблокировать icmp")
		
		
def block_tcp_pct_time():
	def change():
		pct_numb = pct_entry.get()
		time = time_entry.get()
		res = subprocess.check_output(['iptables', '-R', 'INPUT', '1', '-p', 'tcp', '-m', 'state', '--state', 'NEW', '-m', 'recent', '--update', '--seconds', time, '--hitcount', pct_numb, '-j', 'DROP'], encoding='utf-8')
		block_ip_window.destroy()
		limit_tcp_time_pct['state'] = 'normal'
		
		
	def close():
		block_ip_window.destroy()
		limit_tcp_time_pct['state'] = 'normal'


	limit_tcp_time_pct['state'] = 'disabled'
	block_ip_window = tk.Tk()
	block_ip_window.title("Ограничение пакетов tcp")
	block_ip_window.geometry("305x100")
	
	pct_label = tk.Label(block_ip_window, text="Число пакетов").grid(row=0, column=0)
	time_label = tk.Label(block_ip_window, text="Время, с").grid(row=1, column=0)

	pct_entry = tk.Entry(block_ip_window)
	time_entry = tk.Entry(block_ip_window)
	
	pct_entry.grid(row=0, column=1, columnspan=3, stick='we')
	time_entry.grid(row=1, column=1, columnspan=3, stick='we')

	btn_update = tk.Button(block_ip_window, text="Обновить", command=change).grid(row=2, column=0, columnspan=2, stick='we')
	btn_close = tk.Button(block_ip_window, text="Отмена", command=close).grid(row=2, column=2, columnspan=2, stick='we')

	# iptables -A INPUT -p tcp -m state --state NEW -m recent --update --seconds 60 --hitcount 20 -j DROP
	# iptables -A INPUT -p tcp -m state --state NEW -m recent --set -j ACCEPT


tcpmss_btn_text = tk.StringVar()
btn_icmp_text = tk.StringVar()

block_ip_btn = tk.Button(text="Заблокировать по IP", command=block_ip_button)
block_TCP_MSS = tk.Button(textvariable=tcpmss_btn_text, command=block_TCP_MSS)
block_icmp_packet = tk.Button(textvariable=btn_icmp_text, command=block_icmp)
limit_tcp_time_pct = tk.Button(text="Ограничить tcp пакеты", command=block_tcp_pct_time)

block_ip_btn.grid(row=0, column=0, columnspan=2, stick='we')
block_TCP_MSS.grid(row=0, column=2, columnspan=2, stick='we')
block_icmp_packet.grid(row=1, column=0, columnspan=2, stick='we')
limit_tcp_time_pct.grid(row=1, column=2, columnspan=2, stick='we')

tcpmss_btn_text.set("Включить фильтрацию mss")
btn_icmp_text.set("Заблокировать icmp")


run = True

global x
x = {}

def task():
	while run:
		x = app()	
		ip_check(x)
		print(x)
		t = 1
		sleep(t)
		

def ip_check(dct_ip):
	for ip in dct_ip.keys():
		for date in dct_ip[ip].keys():
			if dct_ip[ip][date] > 50:
				subprocess.run(['iptables', '-I', 'INPUT', '3', '-s', ip, '-j', 'DROP'])
				sleep(0.100)
				
				msg = f"Пользователь с IP:{ip} совершает атаку!!! Блокирую!"
				mb.showwarning("Предупреждение", msg)
				
				subprocess.run("cat /var/log/apache2/access.log > /var/log/apache2/temp_access.log", shell=True)
				subprocess.run("sudo bash -c 'echo > /var/log/apache2/access.log'", shell=True)
				
				break
		

thr1 = threading.Thread(target = task,).start()

root.mainloop()

run = False
