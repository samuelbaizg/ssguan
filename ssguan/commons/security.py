# -*- coding: utf-8 -*-
import base64
from hashlib import md5, sha1, sha256

import pyDes
import rsa


#  Copyright 2015 www.suishouguan.com
#
#  Licensed under the Private License (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
def rsa_gen_key_hex(bits):
    (pub_key, priv_key) = rsa.newkeys(bits)
    jd = {}
    jd['e'] = hex(pub_key.e)[2:].upper()
    jd['n'] = hex(pub_key.n)[2:-1].upper()
    jd['d'] = hex(priv_key.d)[2:-1].upper()
    jd['p'] = hex(priv_key.p)[2:-1].upper()
    jd['q'] = hex(priv_key.q)[2:-1].upper()
    return jd
    
def rsa_deg_key_hex(rsa_key):
    e = int(rsa_key['e'], 16)
    n = int(rsa_key['n'], 16)
    d = int(rsa_key['d'], 16)
    p = int(rsa_key['p'], 16)
    q = int(rsa_key['q'], 16)
    pub_key = rsa.PublicKey(n=n, e=e)
    priv_key = rsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)
    return (pub_key, priv_key)

def rsa_encrypt(data, pubic_key):
    """
        public_key is a dict includes both e and n. 
    """
    e = int(pubic_key['e'], 16)
    n = int(pubic_key['n'], 16)
    pub_key = rsa.PublicKey(n=n, e=e)
    return rsa.encrypt(data, pub_key)

def rsa_decrypt(data, private_key):
    """
        public_key is a dict includes e, n, d, p and q. 
    """
    e = int(private_key['e'], 16)
    n = int(private_key['n'], 16)
    d = int(private_key['d'], 16)
    p = int(private_key['p'], 16)
    q = int(private_key['q'], 16)
    priv_key = rsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)
    return rsa.decrypt(data, priv_key)

def str_to_md5_hex(content):
    md = md5()
    md.update(content)
    hd = md.hexdigest()
    return hd

def str_to_sha1_hex(content):
    sha = sha1()
    sha.update(content)
    sha = sha.hexdigest()
    return sha

def str_to_sha256_hex(content):
    sha = sha256()
    sha.update(content)
    sha = sha.hexdigest()
    return sha

def file_to_md5_hex(file_path):
    md = md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md.update(chunk)
        f.close()
    md = md.hexdigest()
    return md

def file_to_sha1_hex(file_path):
    sha = sha1()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
        f.close()
    sha = sha.hexdigest()
    return sha

def file_to_sha256_hex(file_path):
    sha = sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
        f.close()
    sha = sha.hexdigest()
    return sha

DES_MODE_ECB = pyDes.ECB
DES_MODE_CBC = pyDes.CBC
# Modes of padding
DES_PAD_NORMAL = pyDes.PAD_NORMAL
DES_PAD_PKCS5 = pyDes.PAD_PKCS5

def des_encrypt(key, data, mode=None, IV=None, pad=None, padmode=None):
    if mode == None:
        mode = pyDes.ECB
    if padmode == None:
        padmode = pyDes.PAD_NORMAL
    if len(key) == 8:
        des = pyDes.des(key, model=mode, IV=IV)
    elif len(key) == 16 or len(key) == 24:
        des = pyDes.triple_des(key, mode=mode, IV=IV)
    else:
        raise Exception("the length of key only can be 8, 16 or 24.")
    
    return des.encrypt(data, pad=pad, padmode=padmode)

def des_decrypt(key, data, mode=None, IV=None, pad=None, padmode=None):
    if mode == None:
        mode = pyDes.ECB
    if padmode == None:
        padmode = pyDes.PAD_NORMAL
    if len(key) == 8:
        des = pyDes.des(key, model=mode, IV=IV)
    elif len(key) == 16 or len(key) == 24:
        des = pyDes.triple_des(key, mode=mode, IV=IV)
    else:
        raise Exception("the length of key only can be 8, 16 or 24.")
    return des.decrypt(data, pad=pad, padmode=padmode)

def str_to_base64(value, remove_cr=False, replace_cr=True):
    """
        remove_cr: True means the last CR character is removed.
        replace_cr: True means replace all CR with special characters 
    """
    val = base64.encodestring(value)    
    val = val if remove_cr is False else val[:-1]
    if replace_cr:
        val = val.replace("\n", "()")
    return val

def base64_to_str(value, append_cr=False, replace_cr=True):
    """
        append_cr: True means CR should be appended to value
        replace_cr: True means all CR are replaced with special characters in value. 
    """
    value = value + '\n' if append_cr else value
    value = value.replace("()", "\n") if replace_cr else value
    return base64.decodestring(value)   