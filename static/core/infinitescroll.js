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

var InfiniteScrollDirective = function($rootScope) {

	return {
		restrict : 'A',
		scope : false,
		link : function(scope, elmt, attrs) {
			var raw = elmt[0];
			elmt.bind('scroll', function() {
				if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
					scope.$apply(attrs.infinitescroll);
				}
			});
		}
	}
};

InfiniteScrollDirective.$inject = [ '$rootScope' ];
