#!/usr/bin/env python
# tools/intent_sign.py — Ed25519 包签名（P3b）
#
# 心学为体：签名是包的立言凭证——谁发布、内容有没有被动过，一验便知。
# 禅道为翼：不依赖外部工具链（openssl/GPG 不是每家都有），
#           纯标准库自持最小 Ed25519（RFC 8032），换台机器就能验。
# 马哲为用：签名对象是「文件清单摘要」而非整包字节——
#           先验后装，与包格式（.intentp/P4）解耦。
#
# 诚实边界（spec §6 限制 28）：
#   - RFC 8032 最小参考实现（工具/教学级），不做侧信道防护；
#   - 签名/密钥格式为自持 base64，不与 minisign 二进制互操作；
#   - 自证正确性：selftest 用 RFC 8032 §7.1 测试向量 1 逐字节比对。
#
# 用法（库）：
#   import intent_sign
#   sk, pk = intent_sign.generate_keypair()
#   sig = intent_sign.sign(manifest_bytes, sk)
#   ok  = intent_sign.verify(manifest_bytes, sig, pk)
#   digest = intent_sign.manifest({'a.intent': '...', 'intent.toml': '...'})
#
# 用法（CLI）：
#   python tools/intent_sign.py keygen --out DIR   生成 sk.key / pk.pub
#   python tools/intent_sign.py --selftest         RFC 8032 向量自检

import base64
import hashlib
import os
import sys

# ── Ed25519 最小实现（RFC 8032 参考算法，纯标准库）──────────

b = 256
q = 2 ** 255 - 19
_l = 2 ** 252 + 27742317777372353535851937790883648493


def _H(m):
    return hashlib.sha512(m).digest()


def _expmod(b_, e, m):
    if e == 0:
        return 1
    t = _expmod(b_, e // 2, m) ** 2 % m
    if e & 1:
        t = (t * b_) % m
    return t


def _inv(x):
    return _expmod(x, q - 2, q)


_d = -121665 * _inv(121666) % q
_I = _expmod(2, (q - 1) // 4, q)


def _bit(h, i):
    return (h[i // 8] >> (i % 8)) & 1


def _xrecover(y):
    xx = (y * y - 1) * _inv(_d * y * y + 1)
    x = _expmod(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * _I) % q
    if x % 2 != 0:
        x = q - x
    return x


_By = 4 * _inv(5) % q
_Bx = _xrecover(_By)
_B = (_Bx % q, _By % q)


def _edwards(P, Q):
    x1, y1 = P
    x2, y2 = Q
    k = _d * x1 * x2 * y1 * y2
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + k)
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - k)
    return (x3 % q, y3 % q)


def _scalarmult(P, e):
    if e == 0:
        return (0, 1)
    Q = _scalarmult(P, e // 2)
    Q = _edwards(Q, Q)
    if e & 1:
        Q = _edwards(Q, P)
    return Q


def _encodeint(y):
    return bytes((y >> (8 * i)) & 0xff for i in range(b // 8))


def _encodepoint(P):
    x, y = P
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8))
                 for i in range(b // 8))


def _bit_unpack(h):
    return sum(2 ** i * _bit(h, i) for i in range(b - 1))


def _clamp_a(h):
    """RFC 8032 §5.1.5 私钥标量钳位: 清低 3 位 / 清 bit255 / 置 bit254

    漏了这一步的签名实现能自洽(自己签自己验)，但公钥对不上标准向量 —
    自证正确性的价值就在这: 用 RFC 向量逼出实现偏差。
    """
    return 2 ** 254 + sum(2 ** i * _bit(h, i) for i in range(3, 254))


def _Hint(m):
    return int.from_bytes(_H(m), 'little') % _l


def _decodeint(s):
    return int.from_bytes(s, 'little')


def _decodepoint(s):
    y = _decodeint(s) & ((1 << 255) - 1)
    x = _xrecover(y)
    if x & 1 != _bit(s, 255):
        x = q - x
    P = (x, y)
    if not _isedwards(P):
        raise ValueError("非法点编码")
    return P


def _isedwards(P):
    x, y = P
    return (-x * x + y * y - 1 - _d * x * x * y * y) % q == 0


def publickey(sk: bytes) -> bytes:
    h = _H(sk)
    a = _clamp_a(h[:32])
    return _encodepoint(_scalarmult(_B, a))


def sign(msg: bytes, sk: bytes, pk: bytes = None) -> bytes:
    if pk is None:
        pk = publickey(sk)
    h = _H(sk)
    a = _clamp_a(h[:32])
    r = _Hint(h[32:64] + msg)
    R = _scalarmult(_B, r)
    S = (r + _Hint(_encodepoint(R) + pk + msg) * a) % _l
    return _encodepoint(R) + _encodeint(S)


def verify(msg: bytes, sig: bytes, pk: bytes) -> bool:
    if len(sig) != 64 or len(pk) != 32:
        return False
    try:
        R = _decodepoint(sig[:32])
        A = _decodepoint(pk)
    except Exception:
        return False
    S = _decodeint(sig[32:])
    h = _Hint(_encodepoint(R) + _encodepoint(A) + msg)
    return _scalarmult(_B, S) == _edwards(R, _scalarmult(A, h))


# ── 包签名服务层 ────────────────────────────────────────

def generate_keypair():
    """生成密钥对：私钥 32 字节种子（os.urandom），公钥 32 字节"""
    sk = os.urandom(32)
    return sk, publickey(sk)


def manifest(files: dict) -> bytes:
    """文件清单摘要 — 签名与验证共用的唯一字节串

    files: {relpath: bytes|str} → b"rel:sha256hex\\n..." (按 relpath 排序)。
    签名覆盖「文件集合 + 每个文件内容」，增/删/改任一文件都会改变摘要。
    """
    lines = []
    for rel in sorted(files):
        content = files[rel]
        if isinstance(content, str):
            content = content.encode('utf-8')
        lines.append(f"{rel}:{hashlib.sha256(content).hexdigest()}")
    return "\n".join(lines).encode('utf-8')


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')


def unb64(text: str) -> bytes:
    return base64.b64decode(text)


def sign_manifest(files: dict, sk: bytes):
    """对文件清单签名 → (signature_b64, pubkey_b64)"""
    pk = publickey(sk)
    sig = sign(manifest(files), sk, pk)
    return b64(sig), b64(pk)


def verify_manifest(files: dict, sig_b64: str, pk_b64: str) -> bool:
    try:
        return verify(manifest(files), unb64(sig_b64), unb64(pk_b64))
    except Exception:
        return False


# ── CLI ─────────────────────────────────────────────────

USAGE = """用法:
  python tools/intent_sign.py keygen --out DIR   生成 sk.key / pk.pub
  python tools/intent_sign.py --selftest         RFC 8032 向量自检
"""


def _selftest() -> int:
    # RFC 8032 §7.1 TEST 1（空消息）——逐字节比对
    sk = bytes.fromhex(
        '9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
    want_pk = bytes.fromhex(
        'd75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
    want_sig = bytes.fromhex(
        'e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e0652249015'
        '55fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
    pk = publickey(sk)
    if pk != want_pk:
        print("❌ selftest: RFC 8032 公钥不匹配")
        return 1
    sig = sign(b'', sk, pk)
    if sig != want_sig:
        print("❌ selftest: RFC 8032 签名不匹配")
        return 1
    if not verify(b'', sig, pk):
        print("❌ selftest: 验签失败")
        return 1
    if verify(b'x', sig, pk):
        print("❌ selftest: 篡改消息未被拒绝")
        return 1
    # 清单摘要：增/删/改任一文件都要变
    m1 = manifest({'a.intent': 'def f() { return 1; }', 'intent.toml': 'x'})
    m2 = manifest({'a.intent': 'def f() { return 2; }', 'intent.toml': 'x'})
    m3 = manifest({'a.intent': 'def f() { return 1; }'})
    if m1 == m2 or m1 == m3:
        print("❌ selftest: 清单摘要对内容/文件集合不敏感")
        return 1
    print("✅ Ed25519 selftest 全通（RFC 8032 向量 1 + 篡改拒绝 + 清单敏感性）")
    return 0


def _keygen(out_dir: str) -> int:
    sk, pk = generate_keypair()
    os.makedirs(out_dir, exist_ok=True)
    sk_path = os.path.join(out_dir, 'sk.key')
    pk_path = os.path.join(out_dir, 'pk.pub')
    with open(sk_path, 'w', encoding='ascii') as f:
        f.write(b64(sk) + "\n")
    with open(pk_path, 'w', encoding='ascii') as f:
        f.write(b64(pk) + "\n")
    print(f"✅ 密钥对已生成:\n   私钥(勿外传): {sk_path}\n   公钥: {pk_path}")
    return 0


def main(argv) -> int:
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(USAGE)
        return 0 if argv else 2
    if argv[0] == '--selftest':
        return _selftest()
    if argv[0] == 'keygen':
        out = '.'
        if '--out' in argv:
            i = argv.index('--out')
            out = argv[i + 1]
        return _keygen(out)
    print(f"❌ 未知命令: {argv[0]}")
    print(USAGE)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
