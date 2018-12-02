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

var StorageService = function() {
	var factory = {};

	factory.newStorage = function(id) {
		var stclazz = {};
		id = id == undefined ? rnd.intx(1, 9999) : id;
		stclazz._uid = id;
		stclazz._stclazz = {};
		stclazz._key = function(key) {
			return "" + this._uid + "_" + key;
		};
		stclazz.push = function(key, value) {
			this._stclazz[this._key(key)] = value;
		};
		stclazz.pop = function(key) {
			return this._stclazz[this._key(key)];
		};
		stclazz.flush = function() {
			if (localStorage) {
				for ( var key in this._stclazz) {
					localStorage[key] = this._stclazz[key];
				}
			}
		};
		stclazz.clear = function() {
			if (localStorage) {
				for ( var key in this._stclazz) {
					localStorage[key] = "";
				}
			}
			this._stclazz = {};
		};
		return stclazz;
	};
	return factory;
};

StorageService.$inject = [];