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

# Check kernel vermagic
out, err = run("cat /proc/version 2>&1")
print("Kernel:", out[:200])

# Check vermagic of an existing module vs our new one
out, err = run("modinfo /lib/modules/6.18.39/nf_conntrack.ko 2>&1 | grep vermagic")
print("Existing module vermagic:", out[:200])

out, err = run("modinfo /lib/modules/6.18.39/nfnetlink.ko 2>&1 | grep vermagic")
print("Our nfnetlink vermagic:", out[:200])

out, err = run("modinfo /lib/modules/6.18.39/xt_NFQUEUE.ko 2>&1 | grep vermagic")
print("Our xt_NFQUEUE vermagic:", out[:200])

# Check if x_tables is in kernel (check /proc/kallsyms or sysfs)
out, err = run("cat /proc/kallsyms 2>&1 | grep -c x_tables")
print("x_tables symbols:", out[:100])

# Try loading xt_NFQUEUE directly with insmod and see full error
out, err = run("insmod /lib/modules/6.18.39/xt_NFQUEUE.ko 2>&1; echo EXIT:$?")
print("insmod result:", out[:300])

# Check dmesg for errors
out, err = run("dmesg | tail -20 2>&1")
print("dmesg:", out[:500])

# Check if there's an x_tables module already in the running kernel
out, err = run("lsmod | grep -c x_tables")
print("x_tables lsmod:", out[:100])

# Check if x_tables is the issue - what about iptable_filter?
out, err = run("modinfo /lib/modules/6.18.39/iptable_filter.ko 2>&1 | head -10; echo ---; lsmod | grep iptable")
print("iptable_filter:", out[:300])

ssh.close()
