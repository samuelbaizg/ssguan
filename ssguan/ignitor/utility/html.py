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

import re

import chardet

def decode_html(html, encodings=['utf-8', 'gbk']):
    """
        Decode the html with the encoding defined in html by <meta charset>.
        :param html|str: html string
        :param encodings|list: if decoding is wrong through <meta charset> try to decode by these encodings.
        :rtype str: the html being converted.
    """
    def decode(html, encoding):
        try:
            result = html.decode(encoding)
            return result
        except UnicodeDecodeError:
            return None
    charset = re.compile('charset="?([A-Za-z0-9-]+)"?>');
    encoding = charset.search(str(html))
    if encoding is not None:
        encoding = encoding.group(1);
    encoding = 'utf-8' if encoding is None else encoding
    result = decode(html, encoding)
    if result is None:
        encodings.remove(encoding.lower()) 
        for code in encodings:
            result = decode(html, code)
            if result is not None:
                return result
            else:
                continue
    code = chardet.detect(html)['encoding']
    result = html.decode(code, errors='ignore');
    return result



