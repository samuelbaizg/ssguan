//'use strict';
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

var RandomService = function () {
	var factory = {};
	
	factory.intx = function(min, max) {
		minbit = Math.pow(10, min.toString().length);
		maxbit = Math.pow(10, max.toString().length);
		var i = 0;
		while (true) {
			i += 1;
			rand = Math.floor(this.floatx() * maxbit + 1);
			if (rand < min) {
				rand = minbit + rand;
			}
			if (rand > max) {
				rand = maxbit - rand;
			}
			if (rand >= min && rand <= max) {
				return rand;
			} else {
				if (i > 500) {
					return min;
				}
			}
		}
	},

	factory.floatx = function() {
		var today = new Date();
		seed = today.getTime();
		seed = (seed * 9301 + 49297) % 233280;
		return seed / 233280.0;
	},

	factory.arraysort = function(arr) {
		arr.sort(function() {
			return Math.random() > 0.5 ? -1 : 1;
		});
		return arr;
	},

	factory.arraysortx = function(arr) {
		arrLen = arr.length;
		var rArr = new Array(arrLen);
		for (var i = 0; i < arrLen; i++) {
			rArr[i] = Math.random();
		}
		var iArr = new Array(arrLen);
		for (var i = 0; i < arrLen; i++) {
			iArr[i] = i;
			var t = rArr[i];
			for (var j = 0; j < arrLen; j++) {
				if (rArr[j] < t) {
					iArr[i] = j;
					t = rArr[j];
				}
			}
			delete t;
			rArr[iArr[i]] = 1;
		}
		var tArr = arr.slice();
		arr.length = 0;
		for (var i = 0; i < arrLen; i++) {
			arr[i] = tArr[iArr[i]];
		}
		return arr;
	};
	return factory;

};

RandomService.$inject = [];

