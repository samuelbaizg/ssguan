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

var AutoSaveDirective = function($timeout) {

	return {
		restrict : 'A',
		scope : true,
		link : function($scope, elmt, attrs) {

			var lastTime = 0;
			var saveTimer = null;
			$(elmt).on("focus", function(e) {
				lastTime = (new Date()).getTime();
			});

			var autoevent = attrs.autoevent == null ? "keyup" : attrs.autoevent;

			$(elmt).on(autoevent, function(e) {
				if (attrs.autosave != null) {
					_autosave();
				}
			});

			function _autosave() {
				var preferedInterval = attrs.interval ? attrs.interval : 2000;
				var now = (new Date()).getTime();
				var interval = now - lastTime;
				lastTime = now;
				if (interval > preferedInterval) {
					$scope.$apply(attrs.autosave);
				} else {
					if (saveTimer != null) {
						$timeout.cancel(saveTimer);
						saveTimer = null;
					}
					saveTimer = $timeout(function() {
						$scope.$apply(attrs.autosave);
					}, preferedInterval);
				}
			}
		}
	}
};

AutoSaveDirective.$inject = [ '$timeout' ];