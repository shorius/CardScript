# -*- coding: utf-8 -*-
import paramiko
from pathlib import Path



with open(os.path.join(dir, "host_cfg.json"), "r") as fp:
    sql_cfg = json.loads(fp.read())


def upLoadTestFile(host_name):
    global sql_cfg
    # 本機檔案路徑
    local_dir = (Path().absolute() / 'Testfile' / 'TestScript.json')
    sub_local = str(local_dir).replace('\\', '/')
    if local_dir.exists() == False:
        return False

    user_name = sql_cfg['name']
    password = sql_cfg['password']
    port = sql_cfg['port']

    # 連線遠端伺服器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允許連線不在know_hosts檔案中的主機
    ssh.connect(hostname=host_name, port=port, username=user_name, password=password)
    stdin, stdout, stderr = ssh.exec_command("ls")  # 遠端執行shell命令
    # remote_name = stdout.readlines()[1].strip()

    # 取得回傳子目錄路徑名稱
    # remote_name = stdout.readlines()[1].strip()
    remote_name = ''
    for i in stdout.readlines():
        if 'docker-compose' not in i and 'jenkis' not in i:
            remote_name = i.strip()
            break
    print(f'remote_name{remote_name}')
    if len(remote_name) == 0:
        return False

    # 遠端檔案路徑
    sub_remote = sql_cfg['path']

    # 新建一個SFTPClient物件，該物件複用之前的SSH連線
    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    try:
        print(sftp.put(sub_local, sub_remote, confirm=True))
    # sftp.get(sub_remote, sub_local)
    except Exception as e:
        print(e)
        return False

    ssh.close()
    sftp.close()
    return True
