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

# Get full dmesg after modprobe attempt
out, err = run("dmesg | tail -30 2>&1")
print("=== dmesg tail ===")
print(out)

# Check if x_tables is compiled into kernel
out, err = run("cat /proc/config.gz 2>&1 | gunzip 2>&1 | grep -i XTABLES 2>&1")
print("=== XTABLES config ===")
print(out[:300])

# Check sysfs for x_tables
out, err = run("ls /sys/module/ 2>&1 | grep -i x_table")
print("=== x_tables sysfs ===")
print(out[:200])

# Try to find exact insmod error
out, err = run("insmod /lib/modules/6.18.39/xt_NFQUEUE.ko 2>&1; echo STATUS:$?")
print("=== insmod ===")
print(out[:300])

# Check stderr from modprobe
_, stdout, stderr = ssh.exec_command("modprobe xt_NFQUEUE 2>&1")
print("=== modprobe stderr ===")
print(stderr.read().decode().strip()[:200])
print("=== modprobe stdout ===")
print(stdout.read().decode().strip()[:200])

ssh.close()
