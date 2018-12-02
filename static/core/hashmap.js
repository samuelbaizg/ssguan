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

var HashmapService = function() {
	var factory = {};

	factory.newHashmap = function(id) {
		var hmclazz = {};
		id = id == undefined ? rnd.intx(1, 9999) : id;
		hmclazz._uid = id;
		hmclazz._hmclazz = {};
		hmclazz._key = function(key) {
			return "" + this._uid + "_" + key;
		};
		hmclazz.push = function(key, value) {
			this._hmclazz[this._key(key)] = value;
		};
		hmclazz.get = function(key) {
			return this._hmclazz[this._key(key)];
		};
		hmclazz.contain = function(key) {
			return this.get(key) == null ? false : true;
		};
		hmclazz.remove = function(key) {
			delete this._hmclazz[this._key(key)];
		}
		hmclazz.clear = function() {
			this._hmclazz = {};
		};
		return hmclazz;
	};
	
	return factory;

};

HashmapService.$inject = [];
