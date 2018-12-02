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

var NumberService = function() {

	var factory = {};
	factory.newCounter = function(uid, pace) {
		var cntclazz = {};
		uid = uid == undefined ? "Counter_" + rnd.intx(1, 9999) : "" + uid;
		cntclazz._uid = uid;
		cntclazz._i = 0;
		cntclazz.get = function() {
			cntclazz._i += pace ? pace : 1;
			return cntclazz._i;
		}
		return cntclazz;
	}
};

NumberService.$inject = [];