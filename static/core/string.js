'use strict';
//  Copyright 2015 www.suishouguan.com
//
//  Licensed under the Private License (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

var StringService = function() {

	var factory = {};

	factory.toLowerCapital = function(text) {
		var first = text.substring(0, 1);
		return first.toLowerCase() + text.substring(1);
	};

	factory.replaceAll = function(text, oldSub, newSub) {
		var i = text.indexOf(oldSub);
		while (i != -1) {
			text = text.replace(oldSub, newSub);
			i = text.indexOf(oldSub);
		}
		return text;
	};

	factory.trim = function(text) {
		text = text ? text : "";
		return text.replace(/(^\s*)|(\s*$)/g, "");
	};
	factory.lTrim = function(text) {
		text = text ? text : "";
		return text.replace(/(^\s*)/g, "");
	};
	factory.rTrim = function(text) {
		text = text ? text : "";
		return text.replace(/(\s*$)/g, "");
	};

	factory.isEmpty = function(text) {
		return text == null || factory.trim(text).length == 0;
	};

	factory.isTrue = function(value) {
		return value == "true" || value == true || value == '1' || value == 'y';
	};

	factory.isUChar = function(utchar) {
		return utchar > '~';
	};

	factory.ulength = function(text) {
		text = text == null ? "" : text;
		var len = 0;
		for (var i = 0; i < text.length; i++) {
			if (factory.isUChar(text.charAt(i))) {
				len += 2;
			} else {
				len++;
			}
		}
		return len;
	};

	factory.uinsert = function(text, len, insert) {
		text = text == null ? "" : text;
		insert = insert != undefined ? insert : "<br/>";
		var utlen = factory.ulength(text);
		if (utlen < len) {
			return text;
		}
		var str = '';
		utlen = 0;
		for (var i = 0; i < text.length; i++) {
			if (factory.isUChar(text.charAt(i))) {
				utlen += 2;
			} else {
				utlen += 1;
			}
			str += text.charAt(i);
			if (utlen >= len) {
				str += insert;
				utlen = 0;
			}
		}
		return str;
	};

	factory.usubstr = function(text, len, appendix) {
		text = text == null ? "" : text;
		appendix = appendix != undefined ? appendix : "...";
		var utlen = factory.ulength(text);
		if (utlen < len) {
			return text;
		}
		var str = '';
		utlen = 0;
		for (var i = 0; i < text.length; i++) {
			if (factory.isUChar(text.charAt(i))) {
				utlen += 2;
			} else {
				utlen += 1;
			}
			if (utlen <= len) {
				str += text.charAt(i);
			} else {
				break;
			}
		}
		str += appendix;
		return str;
	};

	factory.getTextWidth = function(text) {
		var obj = $("<div/>");
		obj.html(text);
		obj.hide();
		obj.appendTo($("body"));
		var width = obj.width() + 8;
		obj.remove();
		return width;
	};

	factory.outHtml = function(obj) {
		return $("<div/>").append(obj).html();
	};
	factory.outText = function(obj) {
		return $("<div/>").append(obj).text();
	};

	return factory;
};

StringService.$inject = [];

var USubstrFilter = function(string) {

	return function(text, length, appendix) {
		if (text == null) {
			return "";
		}
		return string.usubstr(text, length, appendix);
	};
};

USubstrFilter.$inject = [ 'string' ];

var UInsertFilter = function(string) {
	return function(text, length, insert) {
		if (text == null) {
			return "";
		}
		return string.uinsert(text, length, insert);
	};
};

UInsertFilter.$inject = [ 'string' ];

var HtmlToTextFilter = function(string) {
	return function(text) {
		if (text == null) {
			return "";
		}
		text = "<body>" + text + "</body>";
		return string.outText($(text));
	};
};

HtmlToTextFilter.$inject = [ 'string' ];
