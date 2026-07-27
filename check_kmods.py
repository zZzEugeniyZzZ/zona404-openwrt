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

# Check depmod location
out, err = run("which depmod; command -v depmod; ls /sbin/depmod /usr/sbin/depmod 2>&1; find /lib/modules/6.18.39/ -name modules.dep 2>&1")
print("depmod check:", out[:200])

# xt_NFQUEUE error details
out, err = run("modprobe xt_NFQUEUE 2>&1; echo EXIT:$?")
print("xt_NFQUEUE:", out[:200])

# Check module dependencies
out, err = run("modinfo xt_NFQUEUE 2>&1; echo ---; ls -la /lib/modules/6.18.39/xt_NFQUEUE.ko")
print("modinfo xt_NFQUEUE:", out[:300])

# Check x_tables dependency
out, err = run("lsmod | grep x_tables 2>&1")
print("x_tables:", out[:200])

# Try insmod directly with verbose
out, err = run("insmod /lib/modules/6.18.39/xt_NFQUEUE.ko 2>&1; echo EXIT:$?")
print("insmod xt_NFQUEUE:", out[:200])

# Check all available iptables modules
out, err = run("find /lib/modules/6.18.39/ -name '*.ko' | grep -i xt_ | sort")
print("xt modules:", out[:500])

ssh.close()
