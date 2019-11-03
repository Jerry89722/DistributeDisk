import struct
from settings import *


class Protocol:
    @staticmethod
    def login_payload_pack(self, pld_type: int, payload, size: int):
        if type == HW_DATA_TYPE_LOGIN or type == HW_DATA_TYPE_CMD:
            data = struct.pack('HHI{}s'.format(size), size, type, CLNT_ID, payload.encode("ascii"))
            return data
