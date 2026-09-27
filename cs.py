import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import requests , psutil , sys , jwt , pickle , json , binascii , time , urllib3 , base64 , datetime , re , socket , threading , ssl , pytz , aiohttp , uuid
from protobuf_decoder.protobuf_decoder import Parser
from xPARA import * ; from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2 , MajoRLoGinrEs_pb2 , PorTs_pb2 , MajoRLoGinrEq_pb2 , sQ_pb2 , Team_msg_pb2
from cfonts import render, say

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


Chat_Leave = False
joining_team = False

login_url , ob , version = AuToUpDaTE()

CS_LEVEL_FILE = "cs_levels.json"

def save_cs_level(uid, level, nickname="", region="BD", raw_uid=None):
    """
    Save level to cs_levels.json under MULTIPLE keys:
      - account_id (from login)
      - raw UID (what user typed in accounts.json)
    So master_controller can look up using EITHER key.
    """
    try:
        data = {}
        if os.path.exists(CS_LEVEL_FILE):
            try:
                with open(CS_LEVEL_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        entry = {
            "level": int(level),
            "nickname": nickname,
            "region": region,
            "updated_at": int(time.time())
        }
        # Save under account_id
        data[str(uid)] = entry
        # ⭐ ALSO save under raw UID so master can find it
        if raw_uid and str(raw_uid) != str(uid):
            data[str(raw_uid)] = dict(entry)
            data[str(raw_uid)]["account_id"] = str(uid)
        with open(CS_LEVEL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[CS-LEVEL] ✅ Saved level={level} under keys: {uid}" + (f" + {raw_uid}" if raw_uid else ""))
    except Exception as e:
        print(f"[CS-LEVEL] save error: {e}")


def extract_level_from_dict(dict_res):
    """Level is at protobuf field 6."""
    if not dict_res or not isinstance(dict_res, dict):
        return None

    def _get(d, key):
        if not d:
            return None
        if key in d:
            v = d[key].get("data")
            return v
        if str(key) in d:
            v = d[str(key)].get("data")
            return v
        return None

    for field_num in (6, "6"):
        v = _get(dict_res, field_num)
        if isinstance(v, int) and 0 < v < 200:
            return v

    for k, v in dict_res.items():
        if isinstance(v, dict):
            data = v.get("data")
            if isinstance(data, int) and 1 <= data <= 80:
                if str(k) in ("3", "4", "5", "6", "7"):
                    return data
    return None


Hr = {
    'User-Agent': "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
    'Accept': "*/*",
    'Accept-Encoding': "deflate, gzip",
    'X-Ga-Sv': "1789534056",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2022.3.47f1",
    'X-GA': "v1 1",
    'ReleaseVersion': ob}

def get_random_color():
    colors = ["[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]"]
    return random.choice(colors)

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    return cipher.encrypt(padded_message)

async def GeNeRaTeAccEss(uid , password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"}
    data = {
        "uid": uid, "password": password,
        "response_type": "token", "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=Hr, data=data) as response:
            if response.status != 200: return await response.read()
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)

async def EncryptMajorLogin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.open_id = open_id
    major_login.access_token = access_token
    major_login.client_version = version or "1.132.1"
    major_login.event_time = "2026-09-16 10:32:36"
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.system_software = "Android OS 10 / API-29 (QP1A.190711.020/V12.0.26.0.QCDINXM)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Ncell"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1600
    major_login.screen_height = 720
    major_login.screen_dpi = "320"
    major_login.processor_details = "ARMv7 VFPv3 NEON | 2001 | 8"
    major_login.memory = 3790
    major_login.gpu_renderer = "PowerVR Rogue GE8320"
    major_login.gpu_version = "OpenGL ES 3.2 build 1.11@5425693"
    major_login.unique_device_id = "Google|00000000-0000-0000-0000-000000000000"
    major_login.client_ip = "111.119.38.133"
    major_login.language = "en"
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    try:
        major_login.device_model = "Xiaomi M2006C3LII"
        major_login.country_code = "BD"
    except Exception: pass
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Ncell"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "1ac4b80ecf0478a44203bf8fac6120f5"
    major_login.external_storage_total = 53041
    major_login.external_storage_available = 7291
    major_login.internal_storage_total = 2176
    major_login.game_disk_storage_available = 7395
    major_login.game_disk_storage_total = 53041
    major_login.external_sdcard_avail_storage = 7395
    major_login.external_sdcard_total_storage = 53041
    try: major_login.field_70 = 4
    except Exception: pass
    major_login.login_by = 2
    major_login.library_path = "/data/app/com.dts.freefireth-yAPXAhp2RyIlrtNAM0VzKQ==/lib/arm"
    major_login.reg_avatar = 1
    major_login.library_token = "066a589fa3f5658377634fe7b1d88556|/data/app/com.dts.freefireth-yAPXAhp2RyIlrtNAM0VzKQ==/base.apk"
    major_login.channel_type = 6
    major_login.cpu_type = 1
    major_login.cpu_architecture = "32"
    major_login.client_version_code = "2019121227"
    try: major_login.field_85 = 3
    except Exception: pass
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 3071
    major_login.login_open_id_type = 4
    major_login.loading_time = 9329
    major_login.release_channel = "3rd_party"
    major_login.extra_info = "KqsHT3r+fXQIu/dyZrEa8fJBhbJ5uqDES7YsAUfu+Mck9A+Bly6lFfYk7Q7Nj68pqI8I3g4Oz3gLxWef6Eh/jKyzHug="
    major_login.android_engine_init_flag = 111207
    try: major_login.field_96 = json.dumps({"cur_rate": None, "support_etc2": False}, separators=(',', ':'))
    except Exception: pass
    major_login.if_push = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    try:
        major_login.field_102 = bytes.fromhex("42 54 4c 10 53 0e 5b 04 30")
        major_login.field_104 = 47591
        major_login.field_105 = 1
        major_login.field_106 = "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|1c2462939e53942fc995400436a3dc7b"
        major_login.field_107 = "c8e41b7a93f02d56e1a94c7b8203f5d1"
    except Exception: pass
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

async def MajorLogin(payload):
    url = f"https://loginbp.ppmainecoonghj.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization']= f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto_payload = MajoRLoGinResPonsE[64:] if len(MajoRLoGinResPonsE) > 64 else MajoRLoGinResPonsE
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(proto_payload)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def parse_proto_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {"wire_type": result.wire_type}
        if result.wire_type == "varint":
            field_data["data"] = result.data
        elif result.wire_type == "string":
            field_data["data"] = result.data
        elif result.wire_type == "bytes":
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            try:
                field_data["data"] = await parse_proto_results(result.data.results)
            except Exception:
                field_data["data"] = None
        result_dict[result.field] = field_data
    return result_dict

async def aes_encrypt(payload, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(payload, AES.block_size))

async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="BD", typ='OnLine'):
    uid_hex = f"{int(account_id):016x}"
    timestamp_hex = f"{int(server_time):08x}"
    encode_token = token.encode()
    encrypted_packet = (await aes_encrypt(encode_token, key, iv)).hex()
    encrypted_packet_length = f"{len(encrypted_packet) // 2:08x}"
    reg = str(region).upper() if region else "BD"
    if typ == 'OnLine':
        prefix = '7119' if reg == 'BD' else ('7114' if reg == 'IND' else '7115')
        return f"{prefix}{uid_hex}{timestamp_hex}00000000{encrypted_packet_length}{encrypted_packet}"
    else:
        prefix = '9219' if reg == 'BD' else ('9214' if reg == 'IND' else '9215')
        return f"{prefix}{uid_hex}{timestamp_hex}{encrypted_packet_length}{encrypted_packet}"

async def send_keep_alive(region="BD"):
    try:
        reg = str(region).upper() if region else "BD"
        ka_hex = "0219" if reg == "BD" else ("0214" if reg == "IND" else "0215")
        return bytes.fromhex(ka_hex)
    except Exception:
        return bytes.fromhex("0219")


async def CS_Solo_Start_Matchmaking_Packet(key, iv, region="BD"):
    raw_proto_hex = (
        "080112960b0a0101100f3a0a0a04494443311a0242443a0a0a04494443321a0242443a0a0a0449444333"
        "1a02424440014a0901090a0b1219202729580162a70a0a80013038464241333342343332324443323230"
        "323033323030313232323130303031303038453030303330303841303032344235383634394234313330"
        "324437423434363736323531343030303130343037653061306438343830653734386333663661613034"
        "39643430303030303066663038306130353031636163666131366410c6011ab9037e585c541303054d51"
        "000b5c545102560057050309525a0852070853030057550101545600000b051204014f7d5c4045491a05"
        "1d04191009034c01567c77025a6842627e7a63494477675b79770e7708647b007c7c081302447b5d6351"
        "74567c4f7f677f76565074744c5a7b515c5a5b515063450812535f5d4c1e63791d754541044c646a6640"
        "014346504b594564134b7849470b6c7e7d5b466a1e46090d11040249085950785761007e7e45067e410f"
        "5e0066567e427f520502734b000c130a494502601c5362621e6a0b71426f5a405343795a49197b1a5a48"
        "40790c13034c197349517642174051597f5c6f4342435e5a030008644a05435c790e1b084c606973791e"
        "40646217505d687b484c7f707a185269057943400005081302004d0700640a007370405d714943584261"
        "057a6655016c70797c6a7f7c0c16034f701a015563610475431b015e0558670553401a5a037413771b66"
        "000f160549564a7f50477b697304606c0541696876046346561e464a047f74750c1300054d4477051350"
        "59437e5579435e65674a434500074a7b0240597c4f700d12054e5a4746597b5e5f5b704250405c1e6474"
        "5041537b61451a08616a440522047b5f5d5d300c3a1a1101404b4202020201041511647b7163746e7c5b"
        "57725d5550534207312e3133322e38480650015ab105036262535136334c707a475133416456324b796f"
        "566c6646484e4861775a57523441737574496d41506233706a4666667465554a722b7a58592b466f2f43"
        "2f58304b526636765a7631747943545a6e77314f7a307a7a554532636561556f61552b41483563492b42"
        "4a6d4234556d654b54776f4c34656569657a5345536c79332b6a627163486b4f4156456a4b2b634c4776"
        "3141652b68773749586f4e785137344d55716f544b4450557a4971564e584c4635337641775636706f68"
        "4c47345738387a5132627739466773496a564a4b6a48397538796e55354f51305746632f434b764c2b6b"
        "31617a2b6977576e34397044386c4b775253453846714b6d6c5061395963474e456b646d55562f55446d"
        "643045334d74516c353230567a332b4c55754765344b5136653148336f69466f5647615058417a4a7547"
        "4c6b62734a48412b537676504d4144416842676a502b364f6f49362b31445a594664644371736a675467"
        "62436c5674555a466156726a3130617377584b793674436550373535396757444b65586c617074536949"
        "5a73636d3376667051467165436252316c552f686639495163313634594d373553695a6765346979516c"
        "36514933434571556e754a4b426e635855523739303635654951624674377773546b6f6737384552786e"
        "6f4c484756392b59336662656d50316e4a3650385252394f673532587746706f3759646265556a685466"
        "6c4c4c6a415a782b4a696375694a2f685234652f676c7674553533585849374a37346254377067776137"
        "7054766a66514b696530516a79654b466f72794b6255354f46386771616a333464435961626933545470"
        "4339435838326f36653462742f704a4a4458643855796a6757393075692b695a56434c70394477526173"
        "7a6e7a567858654f37346174644138714956477943524239467145575a77384b755a536339593da20105"
        "080310e802a201050804108703a201050805109c01a20105081d10cc01a2010408161076a20105080e10"
        "8b01a201020815"
    )
    reg = str(region).upper() if region else "BD"
    pkt_prefix = '0319' if reg == 'BD' else ('0314' if reg == 'IND' else '0315')
    packet_bytes = bytes.fromhex(raw_proto_hex)
    encrypted_packet = (await aes_encrypt(packet_bytes, key, iv)).hex()
    packet_length = len(encrypted_packet) // 2
    hex_length = f"{packet_length:08x}"
    return bytes.fromhex(pkt_prefix + hex_length + encrypted_packet)


# ==================== UDP MATCH ENGINE ====================
CRC7_TABLE = bytes([
    0, 9, 18, 27, 36, 45, 54, 63, 72, 65, 90, 83, 108, 101, 126, 119,
    25, 16, 11, 2, 61, 52, 47, 38, 81, 88, 67, 74, 117, 124, 103, 110,
    50, 59, 32, 41, 22, 31, 4, 13, 122, 115, 104, 97, 94, 87, 76, 69,
    43, 34, 57, 48, 15, 6, 29, 20, 99, 106, 113, 120, 71, 78, 85, 92,
    100, 109, 118, 127, 64, 73, 82, 91, 44, 37, 62, 55, 8, 1, 26, 19,
    125, 116, 111, 102, 89, 80, 75, 66, 53, 60, 39, 46, 17, 24, 3, 10,
    86, 95, 68, 77, 114, 123, 96, 105, 30, 23, 12, 5, 58, 51, 40, 33,
    79, 70, 93, 84, 107, 98, 121, 112, 7, 14, 21, 28, 35, 42, 49, 56,
    65, 72, 83, 90, 101, 108, 119, 126, 9, 0, 27, 18, 45, 36, 63, 54,
    88, 81, 74, 67, 124, 117, 110, 103, 16, 25, 2, 11, 52, 61, 38, 47,
    115, 122, 97, 104, 87, 94, 69, 76, 59, 50, 41, 32, 31, 22, 13, 4,
    106, 99, 120, 113, 78, 71, 92, 85, 34, 43, 48, 57, 6, 15, 20, 29,
    37, 44, 55, 62, 1, 8, 19, 26, 109, 100, 127, 118, 73, 64, 91, 82,
    60, 53, 46, 39, 24, 17, 10, 3, 116, 125, 102, 111, 80, 89, 66, 75,
    23, 30, 5, 12, 51, 58, 33, 40, 95, 86, 77, 68, 123, 114, 105, 96,
    14, 7, 28, 21, 42, 35, 56, 49, 70, 79, 84, 93, 98, 107, 112, 121,
])
_DELTA = 0x9E3779B9
_ROUNDS = 16
_FIELD_SIZES = {0: 1, 1: 2, 2: 2, 3: 1, 4: 2}
_FIELD_NAMES = {0: "sendOption", 1: "cmd", 2: "orderId", 3: "flags", 4: "length"}

try:
    from message_ids import MESSAGE_ID_TO_NAME
except Exception:
    MESSAGE_ID_TO_NAME = {1: "UDP_HELLO", 2: "UDP_ACK", 3: "UDP_PING", 10: "RUDP_JOIN_MATCH"}

def optimize_udp_socket(sock: socket.socket):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
    except Exception:
        pass

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf:
        c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while z >= 0x80:
        out.append((z & 0x7F) | 0x80)
        z >>= 7
    out.append(z)
    return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(_ROUNDS):
        s = (s + _DELTA) & 0xFFFFFFFF
        v0 = (v0 + (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_dec(v0, v1, k0, k1, k2, k3):
    s = (_DELTA * _ROUNDS) & 0xFFFFFFFF
    for _ in range(_ROUNDS):
        v1 = (v1 - (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v0 = (v0 - (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        s = (s - _DELTA) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key_bytes):
    import struct
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(padded))
    prev_cipher = bytearray(8)
    prev_intermediate = bytearray(8)
    for i in range(0, len(padded), 8):
        xored = bytearray(8)
        for j in range(8):
            xored[j] = padded[i + j] ^ prev_cipher[j]
        e0, e1 = await tea_enc(struct.unpack_from("<I", xored, 0)[0], struct.unpack_from("<I", xored, 4)[0], k0, k1, k2, k3)
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0)
        struct.pack_into("<I", enc, 4, e1)
        for j in range(8):
            out[i + j] = enc[j] ^ prev_intermediate[j]
        prev_cipher[:] = out[i:i + 8]
        prev_intermediate[:] = xored
        if i % 64 == 0:
            await asyncio.sleep(0)
    return bytes(out)

async def tea_cbc_decrypt(body, key_bytes):
    import struct
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(body))
    prev_intermediate = bytearray(8)
    prev_cipher = bytearray(8)
    xored = bytearray(8)
    dec = bytearray(8)
    for i in range(0, len(body), 8):
        for j in range(8):
            xored[j] = body[i + j] ^ prev_intermediate[j]
        d0, d1 = await tea_dec(struct.unpack_from("<I", xored, 0)[0], struct.unpack_from("<I", xored, 4)[0], k0, k1, k2, k3)
        struct.pack_into("<I", dec, 0, d0)
        struct.pack_into("<I", dec, 4, d1)
        for j in range(8):
            out[i + j] = dec[j] ^ prev_cipher[j]
        prev_cipher[:] = body[i:i + 8]
        prev_intermediate[:] = dec
        if i % 64 == 0:
            await asyncio.sleep(0)
    return bytes(out)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def oicq_unpad(padded):
    if not padded or len(padded) < 8:
        return None
    if not all(padded[-1 - i] == 0 for i in range(7)):
        return None
    pad_len = padded[0] & 0x07
    s = 3 + pad_len
    e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def encode_header(layout, send_option, cmd, order_id, flags, length, k, v80):
    out = bytearray()
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: length}[code]
        if _FIELD_SIZES[code] == 1:
            out.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF)
            out.append((v >> 8) & 0xFF)
    return bytes(out)

async def produce_xor_key(secret_key):
    k = secret_key[0] if secret_key and len(secret_key) > 0 else 10
    return k, ((k << 8) | k) & 0xFFFF

async def parse_layout(layout):
    if isinstance(layout, str):
        return [int(ch) for ch in layout.strip()]
    return list(layout)

async def layouts_from_mask(mask):
    ru = [int(c) for c in str(mask).strip()]
    nr = [c for c in ru if c != 2]
    return ru, nr

async def sv_frame(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0]) + await encode_header(layout, send_option, cmd, order_id, flags, len(body), k, v80)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_packet(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0])
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1:
            hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF)
            hdr.append((v >> 8) & 0xFF)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_hello_packet(text, key, layout):
    data = text.encode("utf-8")
    if len(data) > 25:
        data = data[:25]
    content = len(data).to_bytes(4, "little") + data + b"\x00" * (30 - 4 - len(data))
    k, v80 = await produce_xor_key(key)
    layout = await parse_layout(layout)
    padded = await build_padded(content)
    enc_body = await tea_cbc_encrypt(padded, key)
    header_bytes = await encode_header(layout, 1, 1, 0, 1, len(enc_body), k, v80)
    packet = bytearray([0x63, 0x00]) + header_bytes + enc_body
    packet[1] = await crc7_buff(0, packet[2:]) & 0x7F
    return bytes(packet).hex()

async def build_match_startup_packets(token, udp_key, match_code, account_id, block_val,
                                      server_ip="", region="BD", client_version="1.132.1",
                                      client_version_code="2019121227", access_token=""):
    token = token.strip()
    udp_key = bytes.fromhex(udp_key)
    match_code = [int(ch) for ch in str(match_code).strip()]
    encoded_token = token.encode() if isinstance(token, str) else token
    CHUNK_SIZE = 1060
    chunks = [encoded_token[i:i + CHUNK_SIZE] for i in range(0, len(encoded_token), CHUNK_SIZE)] or [b""]
    thunder_chunks = chunks[:-1]
    encoded_sharma_jwt = chunks[-1]
    thunder_packets = []
    for idx, chunk in enumerate(thunder_chunks):
        garena420 = await has_ssan_zig(len(chunk)) + chunk
        process = await sv_frame(0x5E, match_code, 2, 447, idx, 1, garena420, udp_key)
        thunder_packets.append(process.hex())
    reg = str(region).upper() if region else "BD"
    csoversea_block = bytes.fromhex(
        "ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f62696c652e636f6d"
        "3b302e302e302e303b33342e3132362e37362e34353b33342e38372e3137372e31343b33342e38372e"
        "3137302e3233303b33352e3138352e3138332e35370000010000000100000000000000000000000001"
        "00000000000100010000030100b0e5e4a487da8cdf110200"
    )
    mid = bytes.fromhex('0000000000000101060101') + await has_ssan_zig(len(reg)) + reg.encode()
    mid += bytes.fromhex('0001030001000004')
    mid += await has_ssan_zig(len(client_version)) + client_version.encode()
    mid += await has_ssan_zig(len(client_version_code)) + client_version_code.encode()
    mid += csoversea_block
    clean_ip = server_ip.split(':')[0] if server_ip else "0.0.0.0"
    mid += await has_ssan_zig(len(clean_ip)) + clean_ip.encode()
    clean_acc_tok = access_token.strip() if access_token else ""
    if clean_acc_tok:
        mid += await has_ssan_zig(len(clean_acc_tok)) + clean_acc_tok.encode()
    mid += await has_ssan_zig(len(encoded_sharma_jwt)) + encoded_sharma_jwt
    tg_garena420 = (
        await uleb_encode(int(account_id)) +
        await uleb_encode(int(block_val)) +
        await uleb_encode(1) +
        await uleb_encode(15) +
        await uleb_encode(int(block_val)) +
        await uleb_encode(1) +
        mid
    )
    loading = await sv_frame(0x5A, match_code, 2, 448, len(thunder_packets), 1, tg_garena420, udp_key)
    return thunder_packets, loading.hex()

async def classify(frame):
    cmd = frame["cmd"]
    msg_name = MESSAGE_ID_TO_NAME.get(cmd, f"UNKNOWN_{cmd}")
    if msg_name == "UDP_HELLO": return "HELLO"
    if msg_name == "UDP_ACK": return "ACK"
    if msg_name == "UDP_PING": return "PING"
    if msg_name == "RUDP_JOIN_MATCH": return "JOIN_MATCH"
    return "DATA"

async def reply_for(frame, key, mask, ack_key=0x68, ping_key=0x6D, hello_key=0x5B, ack_style="short"):
    ru, nr = await layouts_from_mask(mask)
    typ = await classify(frame)
    if typ == "HELLO":
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x01\x00", key)
    if typ == "ACK":
        content = frame["content"] if frame["content"] else b"\x01\x00"
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, content, key)
    if typ == "PING":
        c = frame["content"]
        counter = c[:4] if len(c) >= 4 else c
        return typ, await build_packet(ping_key, nr, 0, 3, None, 0, counter + b"\x00\x00\x00", key, encrypted=False)
    if typ == "JOIN_MATCH":
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x02\x00", key)
    return typ, None

async def keepalive_ping(sock, ip, port, key_bytes, mask, stop_event):
    import struct
    nr = (await layouts_from_mask(mask))[1]
    ping_keys = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]
    loop = asyncio.get_event_loop()
    i = 0
    while not stop_event.is_set():
        pk = ping_keys[i % len(ping_keys)]
        counter = int(time.time() * 1000) & 0xFFFFFFFF
        pkt = await build_packet(pk, nr, 0, 3, None, 0, struct.pack("<I", counter) + b"\x00\x00\x00", key_bytes, encrypted=False)
        try:
            await loop.sock_sendto(sock, pkt, (ip, port))
        except Exception:
            pass
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass

async def try_header(buf, layout, k, v80):
    off = 2
    out = {}
    for code in layout:
        size = _FIELD_SIZES[code]
        if off + size > len(buf):
            return None
        out[_FIELD_NAMES[code]] = (buf[off] ^ k) if size == 1 else ((buf[off] | (buf[off + 1] << 8)) ^ v80) & 0xFFFF
        off += size
    out["headerLen"] = off
    return out

async def decode_packet(packet, key, mask=None):
    import itertools
    data = bytes(packet) if isinstance(packet, bytes) else bytes.fromhex(packet)
    if len(data) < 8: return None
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    crc_ok = (data[1] & 0x7F) == await crc7_buff(0, data[2:])
    candidates = []
    if mask:
        ru, nr = await layouts_from_mask(mask)
        layouts = [("RUDP", ru), ("nonRUDP", nr)]
    else:
        layouts = [("RUDP", list(p)) for p in itertools.permutations([0, 1, 2, 3, 4])]
        layouts += [("nonRUDP", list(p)) for p in itertools.permutations([0, 1, 3, 4])]
    for kind, layout in layouts:
        await asyncio.sleep(0)
        f = await try_header(data, layout, k, v80)
        if not f or f["flags"] > 7 or f["sendOption"] > 7 or f["length"] != len(data) - f["headerLen"]:
            continue
        body = data[f["headerLen"]:f["headerLen"] + f["length"]]
        content = None
        padded = None
        if f["flags"] & 1:
            if len(body) < 8 or len(body) % 8 != 0: continue
            padded = await tea_cbc_decrypt(body, key)
            content = await oicq_unpad(padded)
            if content is None: continue
        else:
            content = body
        score = (1 if crc_ok else 0) + (1 if content is not None else 0)
        candidates.append({
            "kind": kind, "layout": layout, "headerLen": f["headerLen"],
            "msgKey": data[0], "cmd": f["cmd"], "flags": f["flags"],
            "sendOption": f["sendOption"], "orderId": f.get("orderId"),
            "length": f["length"], "content": content, "crcOk": crc_ok,
            "padded": padded, "score": score, "total": len(data),
        })
    if not candidates: return None
    candidates.sort(key=lambda c: (c["kind"] == "RUDP" or c["kind"] == "nonRUDP", c["score"]), reverse=True)
    return candidates[0]


async def play_game(server_ip_port, thunder, sharma, udp_key, match_code,
                    account_id, player_region, client_version, key, iv):
    match_start_time = time.time()
    ping_task = None
    sock = None
    ping_stop = asyncio.Event()

    try:
        ip, port = server_ip_port.split(":")
        port = int(port)
        resolved_ip = socket.gethostbyname(ip)
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        optimize_udp_socket(sock)
        sock.setblocking(False)
        udp_key_bytes = bytes.fromhex(udp_key)
        hello_text = f"{account_id}_2585"
        hello_packet = await build_hello_packet(hello_text, udp_key_bytes, match_code)
        await loop.sock_sendto(sock, bytes.fromhex(hello_packet), (resolved_ip, port))

        ack_state = "waiting_for_hello_reply"
        thunder_sent = False
        sharma_sent = False
        local_closed = False
        send_lock = asyncio.Lock()

        ping_task = asyncio.create_task(
            keepalive_ping(sock, resolved_ip, port, udp_key_bytes, match_code, ping_stop)
        )
        last_activity = time.time()
        print(f"\n[+] UDP Session Started -> {resolved_ip}:{port}")

        async def send_thunder_sharma():
            nonlocal ack_state, thunder_sent, sharma_sent
            if thunder_sent: return
            async with send_lock:
                if thunder_sent: return
                try:
                    for i, t_pkt in enumerate(thunder):
                        await loop.sock_sendto(sock, bytes.fromhex(t_pkt), (resolved_ip, port))
                        await asyncio.sleep(0.05)
                    thunder_sent = True
                    await asyncio.sleep(0.1)
                    prepare_ack = await build_packet(0x68, (await layouts_from_mask(match_code))[1], 0, 2, None, 1, b"\x01\x00", udp_key_bytes)
                    await loop.sock_sendto(sock, prepare_ack, (resolved_ip, port))
                    await asyncio.sleep(0.2)
                    await loop.sock_sendto(sock, bytes.fromhex(sharma), (resolved_ip, port))
                    sharma_sent = True
                    ack_state = "thunder_sharma_sent"
                    print(f"[+] Thunder ({len(thunder)} parts) + Sharma Loaded Successfully into Game Room!")
                except Exception as e:
                    print(f"[-] Send error: {e}")

        while not local_closed:
            if time.time() - match_start_time > 700: break
            try:
                response, server_addr = await asyncio.wait_for(loop.sock_recvfrom(sock, 65535), timeout=1.5)
                if response:
                    last_activity = time.time()
                    frame = await decode_packet(response, udp_key_bytes, match_code)
                    if frame:
                        cmd = frame.get('cmd')
                        order_id = frame.get('orderId')
                        flags = frame.get('flags', 0)
                        nr_layout = (await layouts_from_mask(match_code))[1]
                        if cmd in [103, 107]:
                            print(f"[+] Match Finished (Command: {cmd})")
                            local_closed = True
                            continue
                        if cmd == 130:
                            print(f"[+] JOIN_MATCH_FINISHED - Match Fully Loaded!")
                            try:
                                next_id = ((order_id or 0) + 1) & 0xFFFF
                                fin_ack = await build_packet(0x68, nr_layout, 0, 2, None, 1, next_id.to_bytes(2, "little"), udp_key_bytes)
                                await loop.sock_sendto(sock, fin_ack, server_addr)
                            except Exception: pass
                            continue
                        if (flags & 1) and order_id is not None:
                            try:
                                next_expected_id = (order_id + 1) & 0xFFFF
                                data_ack = await build_packet(0x68, nr_layout, 0, 2, None, 1, next_expected_id.to_bytes(2, "little"), udp_key_bytes)
                                await loop.sock_sendto(sock, data_ack, server_addr)
                            except Exception: pass
                        ptype = await classify(frame)
                        if ptype == "HELLO" and ack_state == "waiting_for_hello_reply":
                            _, reply = await reply_for(frame, udp_key_bytes, match_code, ack_style="short")
                            if reply:
                                await loop.sock_sendto(sock, reply, server_addr)
                            ack_state = "ready_to_send_thunder"
                        elif ptype == "ACK":
                            if ack_state in ["waiting_for_hello_reply", "ack_sent_waiting"]:
                                ack_state = "ready_to_send_thunder"
                        elif ptype == "PING":
                            _, reply = await reply_for(frame, udp_key_bytes, match_code)
                            if reply:
                                await loop.sock_sendto(sock, reply, server_addr)
            except asyncio.TimeoutError:
                if ack_state == "ready_to_send_thunder" and not thunder_sent:
                    await send_thunder_sharma()
                elif ack_state == "thunder_sharma_sent":
                    if (time.time() - last_activity) > 10.0:
                        print("[+] Finished naturally (Timeout)")
                        break
                continue
            except Exception:
                await asyncio.sleep(0.5)
            if ack_state == "ready_to_send_thunder" and not thunder_sent:
                await send_thunder_sharma()
    except Exception as e:
        print(f"[-] UDP Error: {e}")
    finally:
        ping_stop.set()
        if ping_task: ping_task.cancel()
        if sock:
            try: sock.close()
            except Exception: pass
        print(f"[+] UDP Closed. Socket cleaned up.")


class CLIENT:
    def __init__(self):
        self.whisper_writer = None
        self.online_writer = None
        self.data2 = None
        self.insquad = None
        self.ping_loop_started = False
        self.matches_played = 0
        self.current_level = 0
        self.shutdown_requested = False
        self.raw_uid = None       # UID user typed
        self.account_id = None    # UID from server
        self.access_token = None
        self.login_url = None
        self.login_token = None
        self.login_payload = None
        self.region = "BD"

    async def check_level_and_exit_if_done(self):
        """Re-fetch level. If >=3, request shutdown."""
        try:
            LoGinDaTa = await GetLoginData(self.login_url, self.login_payload, self.login_token)
            if not LoGinDaTa:
                return False
            parsed = Parser().parse(LoGinDaTa.hex())
            dict_res = await parse_proto_results(parsed)
            lvl = extract_level_from_dict(dict_res)
            if lvl is None:
                try:
                    proto = PorTs_pb2.GetLoginData()
                    proto.ParseFromString(LoGinDaTa)
                    for attr in ("level", "Level"):
                        v = getattr(proto, attr, None)
                        if v:
                            lvl = int(v)
                            break
                except Exception:
                    pass
            if lvl is not None:
                self.current_level = lvl
                save_cs_level(self.account_id, lvl, region=self.region, raw_uid=self.raw_uid)
                print(f"[CS-LEVEL] 🎯 Current level = {lvl}")
                if lvl >= 3:
                    print(f"[CS-LEVEL] ✅ Level {lvl} >= 3 → requesting shutdown")
                    self.shutdown_requested = True
                    return True
            return False
        except Exception as e:
            print(f"[CS-LEVEL] check error: {e}")
            return False

    async def TcPOnLine(self, ip, port, key, iv, AutHToKen, region="BD", reconnect_delay=0.5):
        while not self.shutdown_requested:
            try:
                reader, writer = await asyncio.open_connection(ip, int(port))
                self.online_writer = writer
                self.online_writer.write(bytes.fromhex(AutHToKen))
                await self.online_writer.drain()
                try:
                    init_ka = await send_keep_alive(region)
                    self.online_writer.write(init_ka)
                    await self.online_writer.drain()
                except Exception:
                    pass

                try:
                    await asyncio.sleep(1.0)
                    cs_pkt = await CS_Solo_Start_Matchmaking_Packet(key, iv, region=region)
                    self.online_writer.write(cs_pkt)
                    await self.online_writer.drain()
                    print(f"\n[+] CS Solo Matchmaking Packet Sent!")
                except Exception as e:
                    print(f"[-] Failed to send matchmaking packet: {e}")

                while not self.shutdown_requested:
                    try:
                        self.data2 = await asyncio.wait_for(reader.read(9999), timeout=2.0)
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        break
                    if not self.data2: break
                    hex_data = self.data2.hex()
                    match_idx = hex_data.find("0300")
                    if match_idx != -1 and (len(hex_data) - match_idx) >= 100:
                        try:
                            match_hex = hex_data[match_idx:]
                            decoded_match = await DeCode_PackEt(match_hex[10:])
                            if decoded_match:
                                res = json.loads(decoded_match)
                                match_code = None; server_ip_port = None; udp_key = None
                                match_token = None; block_val = None; match_account_id = None
                                if '42' in res and 'data' in res['42']:
                                    match_code = res['42']['data']
                                if '5' in res and 'data' in res['5']:
                                    res_field5 = res['5']['data']
                                    server_ip_port = res_field5.get('2', {}).get('data')
                                    udp_key = res_field5.get('3', {}).get('data')
                                    match_token = res_field5.get('4', {}).get('data')
                                    if '42' in res_field5:
                                        match_code = res_field5['42']['data']
                                    block_val = res_field5.get('1', {}).get('data')
                                if '1' in res and 'data' in res['1']:
                                    match_account_id = res['1']['data']
                                effective_acc_id = match_account_id or self.account_id
                                cur_region = self.region or "BD"
                                if match_token and udp_key and match_code and server_ip_port:
                                    print("\n" + "=" * 55)
                                    print(f"[+] MATCH ALLOTMENT DETECTED!")
                                    print(f"[+] Server: {server_ip_port} | Match Code: {match_code}")
                                    print("=" * 55)
                                    thunder, sharma = await build_match_startup_packets(
                                        match_token, udp_key, match_code, effective_acc_id, block_val or 0,
                                        server_ip=server_ip_port, region=cur_region,
                                        client_version=version,
                                        access_token=self.access_token or ""
                                    )
                                    await play_game(
                                        server_ip_port, thunder, sharma, udp_key, match_code,
                                        effective_acc_id, cur_region, version, key, iv
                                    )
                                    self.matches_played += 1
                                    print(f"[CS] Match #{self.matches_played} done. Checking level...")

                                    try:
                                        await self.check_level_and_exit_if_done()
                                    except Exception as e:
                                        print(f"[CS-LEVEL] post-match error: {e}")

                                    if self.shutdown_requested:
                                        print("[CS] Shutdown requested → break TCP")
                                        break

                                    try:
                                        await asyncio.sleep(1.0)
                                        cs_pkt = await CS_Solo_Start_Matchmaking_Packet(key, iv, region=region)
                                        self.online_writer.write(cs_pkt)
                                        await self.online_writer.drain()
                                        print(f"[+] Next match matchmaking sent")
                                    except Exception as e:
                                        print(f"[-] Failed to re-send: {e}")
                        except Exception as e:
                            print(f"[-] Match packet parsing error: {e}")

                if self.online_writer is not None:
                    try:
                        self.online_writer.close()
                        await self.online_writer.wait_closed()
                    except Exception: pass
                    finally: self.online_writer = None
                if self.whisper_writer is not None:
                    try:
                        self.whisper_writer.close()
                        await self.whisper_writer.wait_closed()
                    except Exception: pass
                    finally: self.whisper_writer = None
                self.insquad = None
            except Exception as e:
                print(f"- ErroR With {ip}:{port} - {e}")
                self.online_writer = None
            if self.shutdown_requested:
                break
            await asyncio.sleep(reconnect_delay)

    async def TcPChaT(self, ip, port, AutHToKen, key, iv, ready_event, region="BD", reconnect_delay=0.5):
        while not self.shutdown_requested:
            try:
                reader, writer = await asyncio.open_connection(ip, int(port))
                self.whisper_writer = writer
                self.whisper_writer.write(bytes.fromhex(AutHToKen))
                await self.whisper_writer.drain()
                try:
                    init_ka = await send_keep_alive(region)
                    self.whisper_writer.write(init_ka)
                    await self.whisper_writer.drain()
                except Exception:
                    pass
                ready_event.set()

                while not self.shutdown_requested:
                    try:
                        data = await asyncio.wait_for(reader.read(9999), timeout=2.0)
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        break
                    if not data: break

                if self.whisper_writer is not None:
                    try:
                        self.whisper_writer.close()
                        await self.whisper_writer.wait_closed()
                    except Exception: pass
                    finally: self.whisper_writer = None
            except Exception as e:
                print(f"ChaT ErroR {ip}:{port} - {e}")
                self.whisper_writer = None
            if self.shutdown_requested:
                break
            await asyncio.sleep(reconnect_delay)

    async def MaiiiinE(self, custom_uid=None, custom_pwd=None):
        Uid = custom_uid or (sys.argv[1] if len(sys.argv) > 1 else '7952270350')
        Pw = custom_pwd or (sys.argv[2] if len(sys.argv) > 2 else '')
        self.raw_uid = str(Uid)
        print(f"[+] Starting engine for UID: {Uid}")

        open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
        if not open_id or not access_token:
            print("ErroR - InvaLid AccounT"); return None
        self.access_token = access_token

        PyL = await EncryptMajorLogin(open_id, access_token)
        self.login_payload = PyL

        MajoRLoGinResPonsE = await MajorLogin(PyL)
        if not MajoRLoGinResPonsE:
            print("TarGeT => BannEd / NoT ReGisTeReD !"); return None
        MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
        UrL = MajoRLoGinauTh.url
        ToKen = MajoRLoGinauTh.token
        self.login_url = UrL
        self.login_token = ToKen
        TarGeT = MajoRLoGinauTh.account_uid
        self.account_id = str(TarGeT)
        key = MajoRLoGinauTh.key
        iv = MajoRLoGinauTh.iv
        timestamp = MajoRLoGinauTh.timestamp

        LoGinDaTa = await GetLoginData(UrL, PyL, ToKen)
        if not LoGinDaTa:
            print("ErroR - GeTinG PorTs !"); return None

        # ⭐ Parse level and save under BOTH keys
        try:
            parsed = Parser().parse(LoGinDaTa.hex())
            dict_res = await parse_proto_results(parsed)
            lvl = extract_level_from_dict(dict_res)
            if lvl is not None:
                save_cs_level(self.account_id, lvl, region="BD", raw_uid=self.raw_uid)
                print(f"[CS-LEVEL] 🎯 UID {self.account_id} level = {lvl}")
                self.current_level = lvl
                if lvl >= 3:
                    print(f"[CS-LEVEL] ✅ Level {lvl} >= 3 → exiting cs.py")
                    self.shutdown_requested = True
                    return None
            else:
                print(f"[CS-LEVEL] ⚠️ Could not extract level")
        except Exception as e:
            print(f"[CS-LEVEL] parse error: {e}")

        LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
        ReGioN = LoGinDaTaUncRypTinG.Region
        self.region = ReGioN
        AccountName = LoGinDaTaUncRypTinG.AccountName
        OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
        ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
        OnLineiP, OnLineporT = OnLinePorTs.split(":")
        ChaTiP, ChaTporT = ChaTPorTs.split(":")

        auth_chat = await build_tcp_startup_packet(int(TarGeT), ToKen, int(timestamp), key, iv, region=ReGioN, typ='ChaT')
        auth_online = await build_tcp_startup_packet(int(TarGeT), ToKen, int(timestamp), key, iv, region=ReGioN, typ='OnLine')
        ready_event = asyncio.Event()

        task1 = asyncio.create_task(self.TcPChaT(ChaTiP, ChaTporT, auth_chat, key, iv, ready_event, region=ReGioN))
        await ready_event.wait()
        await asyncio.sleep(0.5)
        task2 = asyncio.create_task(self.TcPOnLine(OnLineiP, OnLineporT, key, iv, auth_online, region=ReGioN))

        print(render('REDZED', colors=['white', 'red'], align='center'))
        print(f" - SerVeR LoGiN UrL => {login_url} | SerVer Url => {UrL}\n")
        print(f" - GaMe sTaTus > Good | OB => {ob} | Version => {version}\n")
        print(f" - BoT STarTinG on TarGet : {AccountName} , UiD : {TarGeT} | ReGioN => {ReGioN}\n")
        print(f" - BoT STarTing Match Engine...\n")

        while not self.shutdown_requested:
            await asyncio.sleep(1)

        print("[CS] Shutdown requested → cancelling tasks")
        task1.cancel()
        task2.cancel()
        try:
            await asyncio.gather(task1, task2, return_exceptions=True)
        except Exception:
            pass
        print("[CS] Exiting cs.py cleanly")
        return None


client = CLIENT()

async def StarTinG():
    target_uid = sys.argv[1] if len(sys.argv) > 1 else None
    target_pwd = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        await client.MaiiiinE(target_uid, target_pwd)
    except Exception as e:
        import traceback
        print(f"[-] Error: {e}")
        traceback.print_exc()
    finally:
        print("[CS] Main exited. Returning control to master.")
        sys.exit(0)

if __name__ == '__main__':
    asyncio.run(StarTinG())