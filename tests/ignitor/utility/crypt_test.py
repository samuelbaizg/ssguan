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

import unittest

import rsa

from ssguan.ignitor.utility import crypt, kind


class SecurityTest(unittest.TestCase):
    
    def test_rsa(self):
#         key = crypt.rsa_gen_key_hex(256)
        (pub_key, priv_key) = rsa.newkeys(256)
        orig = b'testw'
        encrypted = rsa.encrypt(orig,pub_key)
        decrypted = rsa.decrypt(encrypted, priv_key)
        self.assertEqual(orig, decrypted)
        orig = u'啊大法大法'
        orig = kind.unibytes(orig)
        encrypted = rsa.encrypt(orig,pub_key)
        decrypted = rsa.decrypt(encrypted, priv_key)
        self.assertEqual(orig, decrypted)
    
    def test_rsa_wrapper(self):
        key = crypt.rsa_gen_key_hex(256)
        orig = b'testw'
        encrypted = crypt.rsa_encrypt(orig, key)
        decrypted = crypt.rsa_decrypt(encrypted, key,safestr=False)
        self.assertEqual(orig, decrypted)
        orig = u'啊大法大法'
        encrypted = crypt.rsa_encrypt(orig, key)
        decrypted = crypt.rsa_decrypt(encrypted, key)
        decrypted = kind.safestr(decrypted)
        self.assertEqual(orig, decrypted)
