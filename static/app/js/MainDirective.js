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

var MainDirective = function($location, $rootScope) {

	function randomPath(path) {
		return path + "?" + $rootScope.G_VERSION;
	}

	function initializeMain() {
		var template = conf.TEMPLATEs[$location.path()];
		$rootScope.shortcuts = template.shortcuts;
		if (template.sidebar != undefined) {
			$rootScope.sidebarHeadTmpl = randomPath(template.sidebar.sidebarHeadPath);
			$rootScope.sidebarBodyTmpl = randomPath(template.sidebar.sidebarBodyPath);
		} else {
			$rootScope.sidebarHeadTmpl = null;
			$rootScope.sidebarBodyTmpl = null;
		}

		if (!template.sidebar
				|| (template.sidebar && template.sidebar.defaultOpen != true)) {
			$(".sidebar").hide();

		}

		$("#wsLeftCol").addClass(template.wsLeftCol.widthClass);
		if (template.wsLeftCol.headPath != undefined) {
			$rootScope.wsLeftColHeadTmpl = randomPath(template.wsLeftCol.headPath);
		} else {
			$rootScope.wsLeftColHeadTmpl = null;
		}
		$rootScope.wsLeftColBodyTmpl = randomPath(template.wsLeftCol.bodyPath);

		if (template.wsRightCol != undefined) {
			$("#wsRightCol").addClass(template.wsRightCol.widthClass);
			if (template.wsRightCol.headPath != undefined) {
				$rootScope.wsRightColHeadTmpl = randomPath(template.wsRightCol.headPath);
			} else {
				$("#wsRightCol>.wscol-head").hide();
			}
			$rootScope.wsRightColBodyTmpl = randomPath(template.wsRightCol.bodyPath);
			if (template.wsRightCol.defaultOpen) {
				$rootScope.showWsRightCol(false);
			} else {
				$rootScope.showWsRightCol(true);
			}

		} else {
			$("#wsRightCol").hide();
			$rootScope.wsRightColHeadTmpl = null;
			$rootScope.wsRightColBodyTmpl = null;
		}

	}

	function resizeMain() {
		$rootScope.resizeSidebar();
		$rootScope.resizeWsLeftCol();
		$rootScope.resizeWsRightCol();
	}

	$rootScope.resizeSidebar = function() {
		var screenHeight = $(window).height();
		var siblingHeight = 0;
		siblingHeight += $("#sidebar>.sidebar-head").actual("outerHeight");
		if ($(".nav-left").is(":hidden")) {
			siblingHeight += $("#navbar").actual("outerHeight");
		}
		var template = conf.TEMPLATEs[$location.path()];
		var adjustHeight = 20;
		$("#sidebar>.sidebar-body").height(
				screenHeight - siblingHeight - adjustHeight);

		$(".sidebar-shadow").height(screenHeight);
		$(".sidebar-shadow>i").css("margin-top", screenHeight / 2);
		$(".sidebar-shadow>i").css("margin-left",
				$(".sidebar-shadow").width() / 2);
		$rootScope.$emit("EVENT_RESIZE_SIDEBAR");
	}

	$rootScope.resizeWsLeftCol = function() {
		var template = conf.TEMPLATEs[$location.path()];
		var screenHeight = $(window).height();
		var siblingHeight = 0;
		if (template.wsLeftCol.headPath != undefined) {
			siblingHeight += $("#wsLeftCol>.wscol-head").outerHeight();
		}
		var adjustHeight = 20;
		$("#wsLeftCol>div>.wscol-body").height(
				screenHeight - siblingHeight - adjustHeight);
		$rootScope.$emit("EVENT_RESIZE_WSLEFTCOL");
	}

	$rootScope.resizeWsRightCol = function() {
		var template = conf.TEMPLATEs[$location.path()];
		if (template.wsRightCol == undefined) {
			return;
		}
		var screenHeight = $(window).height();
		var siblingHeight = 0;
		if (template.wsLeftCol.headPath != undefined) {
			siblingHeight += $("#wsRightCol>.wscol-head").outerHeight();
		}
		var adjustHeight = 20;
		$("#wsRightCol>div>.wscol-body").height(
				screenHeight - siblingHeight - adjustHeight);
		$rootScope.$emit("EVENT_RESIZE_WSRIGHTCOL");
	}

	$rootScope.showSidebar = function(hidden) {
		var template = conf.TEMPLATEs[$location.path()];
		if (template.sidebar) {
			if (hidden) {
				$(".sidebar").hide();
			} else {
				$(".sidebar").show();
			}
		}
	}

	$rootScope.showWsRightCol = function(hidden) {
		var template = conf.TEMPLATEs[$location.path()];
		var wsLeftCol = $("#wsLeftCol");
		var wsRightCol = $("#wsRightCol");
		if (hidden) {
			wsLeftCol.removeClass(template.wsLeftCol.widthClass);
			wsLeftCol.addClass(template.wsLeftCol.maxWidthClass);
			wsRightCol.hide();
			wsLeftCol.show();
		} else {
			wsLeftCol.removeClass(template.wsLeftCol.maxWidthClass);
			wsLeftCol.addClass(template.wsLeftCol.widthClass);
			wsRightCol.show();
			if ($(".nav-left").is(":hidden")) {
				wsLeftCol.hide();
			} else {
				wsLeftCol.show();
			}
		}
	}

	$rootScope.closeWsRightCol = function() {
		$rootScope.$broadcast("EVENT_CLOSE_WSRIGHTCOL");
	}

	$rootScope.shortcutClick = function(eventName) {
		$rootScope.$broadcast(eventName);
	}

	return {
		restrict : 'A',
		link : function($scope, elmt) {
			initializeMain();
			$(window).resize(function() {
				resizeMain();
			});
		}
	};
};
MainDirective.$inject = [ '$location', '$rootScope' ];
