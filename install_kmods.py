import paramiko, warnings
warnings.filterwarnings("ignore")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.1.1", port=22, username="root", password="!LoL-eSports",
            look_for_keys=False, allow_agent=False, timeout=15)

def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

out, err = run("depmod -a 2>&1; echo DEPMOD_EXIT:$?")
print(out)

out, err = run("modprobe nfnetlink 2>&1; echo EXIT:$?")
print(out)

out, err = run("modprobe nfnetlink_queue 2>&1; echo EXIT:$?")
print(out)

out, err = run("modprobe xt_NFQUEUE 2>&1; echo EXIT:$?")
print(out)

out, err = run("lsmod 2>&1")
for line in out.split("\n"):
    if "nfnetlink" in line or "nfqueue" in line or "NFQUEUE" in line or "conn" in line:
        print("  " + line)

out, err = run("apk list-installed 2>&1 | grep -i nfqws")
print("nfqws packages:", out or "not installed")

ssh.close()
