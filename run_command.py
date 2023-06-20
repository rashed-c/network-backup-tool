
# module name: pyaml
# module name: netmiko,futures


import os
import subprocess
import yaml
#import concurrent.futures as cf
from netmiko import ConnectHandler
from datetime import date
import logging.config
import time
import getpass
import threading
from pathlib import Path


def clear(): return os.system('cls')


clear()
print("--------------------------------------")
print("-   Backup Configuration Script      -")
print("-      By: Rashed Chowdhury          -")
print("--------------------------------------")

current_path = os.getcwd()


# Set logging parameters from the logging.yaml file

def setup_logging(
        default_path='logging.yaml',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


# Get credentials

def get_credential():
    site = "Acme United"
    # log = logging.getLogger("get_credential()")
    creds = []
    print("Enter credentials for site: {0}".format(site))
    username = [{'uname': input("Username: ")}]
    password = [{'pwd': getpass.getpass("Password: ")}]
    fgt_pwd = [{'fgt_pwd': getpass.getpass("Fortigate password: ")}]
    creds.append(username)
    creds.append(password)
    creds.append(fgt_pwd)
    return creds

# Read yaml file and return it.


def read_configfile(filename):
    # log = logging.getLogger("read_configfile()")
    with open(f"{current_path}\\configs\\{filename}", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    # log.info("Loaded config file from: {0}".format(ymlfile.name))
    return cfg

# Get list of files with device


def get_configfile():
    file_list = []
    for filename in os.listdir('configs'):
        if(filename != "desktop.ini"):
            file_list.append(filename)
    return (file_list)

# Get devices from the config file and return them in device_list variable.


def get_devices(creds, config_file):
    # log = logging.getLogger("get_devices()")
    device_list = []
    cfg = config_file
    site = cfg['site']
    try:
        # Check if backup flag is true on yaml file, skip if fals or doesn't exist
        backup = cfg['enable_backup']
        if backup:
            # log.info(
            # "Started backup process for site: {0}".format(cfg['site']))
            for device_category in cfg['DeviceList'].keys():
                if device_category == "Switch_List":
                    #log.info("Devices detected in: {0}".format(device_category))
                    for device in cfg['DeviceList'][device_category]:
                        # Add username to to device dictionary
                        cfg['DeviceList'][device_category][device]['username'] = creds[0][0]['uname']
                        cfg['DeviceList'][device_category][device]['password'] = creds[1][0]['pwd']
                        cfg['DeviceList'][device_category][device]['secret'] = "secret"
                        device_list.append(
                            cfg['DeviceList'][device_category][device])

                elif device_category == "Firewall_List":
                    # log.info("Devices detected in: {0}".format(device_category))
                    for device in cfg['DeviceList'][device_category]:
                        # Add username to to device dictionary
                        cfg['DeviceList'][device_category][device]['username'] = creds[0][0]['uname']
                        # Add fortigate password to dictionary
                        cfg['DeviceList'][device_category][device]['password'] = creds[2][0]['fgt_pwd']
                        device_list.append(
                            cfg['DeviceList'][device_category][device])
        else:
            pass
            # log.info("Skipping backup for site: {0}".format(cfg['site']))

    except:
        #     # log.info("Skipping backup for site: {0}".format(cfg['site']))
        pass

    return(device_list, site)


# Run backups
def run_backup(device, index):
    # log = logging.getLogger("run_backup()")
    today = date.today()  # hold todays date
    path = os.environ['userprofile']
    devices = device[index]
    site = device[index+1]
    # directory =  "{0}\\config backups\\{1}".format(path,site)
    # if not os.path.exists(directory):
    # 	os.makedirs(directory)
    # 	log.info("Backup path created for site: {0}".format(site))
    # 	log.info("Backup path created on: {0}".format(directory))
    # else:
    # 	log.info("Backup path located on: {0}".format(directory))
    for device in devices:
        if device['device_type'] == "brocade_fastiron":
            try:
                # log.info("Attempting to connect to switch IP: {0} ".format(device['ip']))
                net_connect = ConnectHandler(**device)
                output = net_connect.find_prompt()
                hostname = output[4:-1]
                # switch_dir = f"{directory}\\Switches"
                # Path(switch_dir).mkdir(parents=True, exist_ok=True)
                # text_file = open(f"{switch_dir}\\{hostname}.conf", "w")
                # log.info("Started config backup for Brocade device: {0} ".format(device['ip']))
                net_connect.enable()
                time.sleep(3)
                output = net_connect.send_command("show ver | include Serial")
                print(f'Hostname:{hostname}, serial: {output}')
                # text_file.write(net_connect.send_command("show run"))
                # text_file.close()
                # log.info("Device: {0}, backed up as {1}".format(device['ip'], text_file.name))

            except Exception as e:
                pass
                # log.error(e)

        # elif device['device_type'] == "cisco_ios":

        # 	try:
        # 		log.info("Attempting to connect to switch IP: {0} ".format(device['ip']))
        # 		net_connect = ConnectHandler(**device)
        # 		output = net_connect.find_prompt()
        # 		hostname = output[4:-1]
        # 		switch_dir = f"{directory}\\Switches"
        # 		Path(switch_dir).mkdir(parents=True, exist_ok=True)
        # 		text_file = open(f"{switch_dir}\\{hostname}.conf", "w")
        # 		log.info("Started config backup for Cisco device: {0} ".format(device['ip']))
        # 		net_connect.enable()
        # 		time.sleep(1)
        # 		text_file.write(net_connect.send_command("show run"))
        # 		text_file.close()
        # 		log.info("Device: {0}, backed up as {1}".format(device['ip'], text_file.name))

        # 	except Exception as e:
        # 		log.error(e)

        # elif device['device_type'] == "hp_procurve":
        # 	try:
        # 		log.info("Attempting to connect to HP switch IP: {0} ".format(device['ip']))
        # 		net_connect = ConnectHandler(**device)
        # 		output = net_connect.find_prompt()
        # 		hostname = output[4:-1]
        # 		switch_dir = f"{directory}\\Switches"
        # 		Path(switch_dir).mkdir(parents=True, exist_ok=True)
        # 		text_file = open(f"{switch_dir}\\{hostname}.conf", "w")
        # 		log.info("Started config backup for HP device: {0} ".format(device['ip']))
        # 		net_connect.enable()
        # 		time.sleep(1)
        # 		text_file.write(net_connect.send_command("show run"))
        # 		text_file.close()
        # 		log.info("Device: {0}, backed up as {1}".format(device['ip'], text_file.name))

        # 	except Exception as e:
        # 		log.error(e)

        elif device['device_type'] == "fortinet":
            pass
            # try:
            # 	log.info("Attempting to connect to firewall IP: {0} ".format(device['ip']))
            # 	net_connect = ConnectHandler(**device)
            # 	output = net_connect.find_prompt()
            # 	hostname = output[:-2]
            # 	firewall_dir = f"{directory}\\Firewalls"
            # 	Path(firewall_dir).mkdir(parents=True, exist_ok=True)
            # 	text_file = open(f"{firewall_dir}\\{hostname}.conf", "w")
            # 	log.info("Started config backup for device: {0} ".format(device['ip']))
            # 	text_file.write(net_connect.send_command("show full-configuration"))
            # 	text_file.close()
            # 	log.info("Device: {0}, backed up as {1}".format(device['ip'], text_file.name))

            # except Exception as e:
            # 	log.error(e)


def main():
    # setup_logging()
    device_type = ""

    config_files = get_configfile()
    creds = get_credential()

    devices_and_site = []
    # for config_file in config_files:
    #     devices_and_site += get_devices(creds, read_configfile(config_file))

    thread = {}
    for t in range(len(config_files)):
        devices_and_site += get_devices(creds,
                                        read_configfile(config_files[t]))
        thread = {t: threading.Thread(target=run_backup, args=(
            devices_and_site[devices], devices,))}
    print(thread)

    # thread[t].start()
    # thread[t].join()

    #t = threading.Thread(target=print_square, args=(10,))

    # run_backup(devices_and_site)
    '''
		# Multithread testing
		executor = cf.ThreadPoolExecutor(5)
		futures = [executor.submit(run_backup, devices_and_site)
		                           for device in devices_and_site]
		cf.wait(futures)

	try:
		print(directory)
		subprocess.Popen(r'explorer /select,"{0}"'.format(directory))
	except Exception as e:
		log.error(e)
	'''


# Script starting point.
if __name__ == '__main__':
    main()
