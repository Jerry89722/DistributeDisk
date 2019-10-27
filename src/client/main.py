import struct
import sys, socket

host = "www.huiwanit.cn"
port = 9001

if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print("host name could not be resolved")
        sys.exit()

    s.connect((remote_ip, port))
    payload_content = "hp"
    payload_size = len(payload_content)
    payload_type = 0  # HW_DATA_TYPE_LOGIN
    cid = 1
    data = struct.pack('HHI{}s'.format(payload_size), payload_size, payload_type, cid, payload_content.encode("ascii"))

    slen = s.send(data)

    print("send len: ", slen)

    buf = s.recv(4096)

    print(str(buf))






