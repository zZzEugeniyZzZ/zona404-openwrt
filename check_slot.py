import paramiko, warnings
warnings.filterwarnings("ignore")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.1', port=222, username='root', password='keenetic',
            look_for_keys=False, allow_agent=False, timeout=30)

cmds = [
    "cat /proc/cmdline",
    "hexdump -C /dev/mtd11 2>/dev/null | head -5",
    "mount | head -10",
    "df / 2>/dev/null",
    "cat /proc/mounts | head -10",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"=== {cmd} ===")
    print(out[:300])
    if err:
        print(f"ERR: {err}")
    print()

ssh.close()
