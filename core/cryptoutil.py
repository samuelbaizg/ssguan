# -*- coding: utf-8 -*-

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
import md5
import rsa
from pydes import pyDes

MODE_ECB = pyDes.ECB
MODE_CBC = pyDes.CBC
# Modes of padding
PAD_NORMAL = pyDes.PAD_NORMAL
PAD_PKCS5 = pyDes.PAD_PKCS5


def rsa_gen_key_hex(bits):
    (pub_key, priv_key) = rsa.newkeys(bits)
    print pub_key
    print priv_key
    jd = {}
    jd['e'] = hex(pub_key.e)[2:].upper()
    jd['n'] = hex(pub_key.n)[2:-1].upper()
    jd['d'] = hex(priv_key.d)[2:-1].upper()
    jd['p'] = hex(priv_key.p)[2:-1].upper()
    jd['q'] = hex(priv_key.q)[2:-1].upper()
    print jd
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

def rsa_encrypt(data, rsa_key_hex):
    return rsa.encrypt(data, rsa_deg_key_hex(rsa_key_hex)[0])

def rsa_decrypt(data, rsa_key_hex):
    return rsa.decrypt(data, rsa_deg_key_hex(rsa_key_hex)[1])

def encypt_data(key, data, mode=None, IV=None, pad=None, padmode=None):
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


def decypt_data(key, data, mode=None, IV=None, pad=None, padmode=None):
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

def get_md5(content):
    md = md5.new()
    md.update(content)
    hd = md.hexdigest()
    return hd
