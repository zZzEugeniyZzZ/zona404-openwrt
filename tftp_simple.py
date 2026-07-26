# Simple TFTP Server for Netcraze NC-1812 recovery
import socket, struct, os, sys

FW_FILE = r"E:\OpenWRT\openwrt-mediatek-filogic-netcraze_nc-1812-squashfs-factory.bin"
BACKUP_FW = r"E:\AI\Projects\Zona 404\backup\firmware_1.bin"

if not os.path.exists(FW_FILE):
    print(f"ERROR: firmware not found: {FW_FILE}")
    sys.exit(1)

fw_size = os.path.getsize(FW_FILE)
print(f"Firmware: {FW_FILE} ({fw_size/1024/1024:.1f} MB)")

with open(FW_FILE, "rb") as f:
    fw_data = f.read()

def handle_rrq(data, addr, sock):
    """Handle TFTP Read Request"""
    try:
        # Parse filename (null-terminated after opcode)
        null1 = data.index(b'\x00', 2)
        filename = data[2:null1].decode('ascii', errors='replace')
        null2 = data.index(b'\x00', null1 + 1)
        mode = data[null1+1:null2].decode('ascii', errors='replace')
        
        print(f"\nRRQ: '{filename}' mode='{mode}' from {addr[0]}:{addr[1]}")
        
        # Serve our firmware regardless of requested filename
        block_size = 512
        blocks = (fw_size + block_size - 1) // block_size
        
        print(f"Sending {blocks} blocks ({fw_size} bytes) to {addr[0]}:{addr[1]}")
        
        for block_num in range(blocks):
            offset = block_num * block_size
            chunk = fw_data[offset:offset + block_size]
            
            # DATA packet: opcode(2) + block(2) + data
            pkt = struct.pack("!HH", 3, (block_num + 1) & 0xFFFF) + chunk
            
            # Send with retries
            for attempt in range(10):
                sock.sendto(pkt, addr)
                try:
                    sock.settimeout(3)
                    ack, _ = sock.recvfrom(1024)
                    if len(ack) >= 4:
                        ack_op = struct.unpack("!H", ack[:2])[0]
                        ack_num = struct.unpack("!H", ack[2:4])[0]
                        if ack_op == 4 and ack_num == ((block_num + 1) & 0xFFFF):
                            break
                except socket.timeout:
                    if attempt == 9:
                        print(f"Block {block_num+1} failed (no ACK)")
                        return
            else:
                continue  # inner break didn't happen
            
            if (block_num + 1) % 100 == 0:
                print(f"  {block_num+1}/{blocks} blocks ({100*(block_num+1)//blocks}%)")
        
        print(f"Transfer complete!")
        
    except Exception as e:
        print(f"Error: {e}")

# Main server loop
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Note: port 69 requires admin on Windows. Use port 1069 as fallback
PORT = 69
try:
    sock.bind(("0.0.0.0", PORT))
    print(f"TFTP server on udp/{PORT}")
except PermissionError:
    PORT = 1069
    sock.bind(("0.0.0.0", PORT))
    print(f"Port 69 requires admin. Using port {PORT} instead.")
    tf = open(r"E:\AI\Projects\Zona 404\tftp_port.txt", "w")
    tf.write(str(PORT))
    tf.close()

sock.settimeout(1)
print("Waiting for bootloader request ...")

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if len(data) >= 2:
                opcode = struct.unpack("!H", data[:2])[0]
                if opcode == 1:  # RRQ
                    handle_rrq(data, addr, sock)
                elif opcode == 2:  # WRQ
                    print(f"WRQ from {addr[0]} - ignoring")
        except socket.timeout:
            pass
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    sock.close()
