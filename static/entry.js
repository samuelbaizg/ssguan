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

(function() {

	var CSSES = [], JSES = [];

	// ==========================================================================//

	addCSS('contrib/fontawesome/css/font-awesome.css');

	
	addJS('contrib/crypto/rsa/jsbn.js');
	addJS('contrib/crypto/rsa/prng4.js');
	addJS('contrib/crypto/rsa/rng.js');
	addJS('contrib/crypto/rsa/rsa.js');
	addJS('contrib/crypto/base64/base64.js');
	
	addJS('contrib/angular/angular.js');
	// addJS('contrib/angular/angular-resource.js');
	addJS('contrib/angular/angular-route.js');
	// addJS('contrib/angular/angular-cookies.js');
	addJS('contrib/angular/angular-sanitize.js');
	// addJS('contrib/angular/angular-touch.js');
	// addJS('contrib/angular/angular-animate.js');
	addJS('contrib/angular-translate/angular-translate.js');
	addJS('contrib/jquery/jquery-1.11.1.js');
	addJS('contrib/jquery-actual/jquery-actual.js');
	addJS('contrib/jquery-hotkeys/jquery-hotkeys.js');
	addCSS('contrib/bootstrap/css/bootstrap.css');
	addJS('contrib/bootstrap/js/bootstrap.js');
	addJS('contrib/bootstrap/js/bootstrap-angular.js');

	addCSS('contrib/jqplot/css/jquery.jqplot.min.css');
	addJS('contrib/jqplot/jquery.jqplot.min.js');
	addJS('contrib/jqplot/plugins/jqplot.highlighter.min.js');
	addJS('contrib/jqplot/plugins/jqplot.cursor.min.js');
	addJS('contrib/jqplot/plugins/jqplot.dateAxisRenderer.min.js');
	addJS('contrib/jqplot/plugins/jqplot.enhancedLegendRenderer.min.js');
	addJS('contrib/jqplot/plugins/jqplot.categoryAxisRenderer.min.js');
	addJS('contrib/jqplot/plugins/jqplot.barRenderer.min.js');
	addJS('contrib/jqplot/plugins/jqplot.pointLabels.min.js');

	addCSS('contrib/bootstrap-wysiwyg/bootstrap-wysiwyg.css');
	addJS('contrib/bootstrap-wysiwyg/bootstrap-wysiwyg.js');
	addJS('contrib/bootstrap-wysiwyg/locales/bootstrap-wysiwyg.zh_CN.js');
	addJS('contrib/bootstrap-wysiwyg/bootstrap-wysiwyg-angular.js');

	addCSS('contrib/bootstrap-datetimepicker/bootstrap-datetimepicker.css');
	addJS('contrib/bootstrap-datetimepicker/bootstrap-datetimepicker.js');
	addJS('contrib/bootstrap-datetimepicker/locales/bootstrap-datetimepicker.zh-CN.js');
	addJS('contrib/bootstrap-datetimepicker/bootstrap-datetimepicker-angular.js');
	addJS('contrib/bootstrap-typeahead/bootstrap3-typeahead.js');
	addJS('contrib/bootstrap-typeahead/bootstrap3-typeahead-angular.js');
	addCSS('contrib/bootstrap-tagsinput/bootstrap-tagsinput.css');
	addJS('contrib/bootstrap-tagsinput/bootstrap-tagsinput.js');
	addJS('contrib/bootstrap-tagsinput/bootstrap-tagsinput-angular.js');

	addJS('core/string.js');
	addJS('core/random.js');
	addJS('core/number.js');
	addJS('core/hashmap.js');
	addJS('core/storage.js');
	addJS('core/datastore.js');
	addJS('core/infobox.js');
	addJS('core/infinitescroll.js');
	addJS('core/autosave.js');

	addCSS('app/css/App.css');
	addJS('app/js/MainDirective.js');
	addJS('app/js/NavbarDirective.js');

	addCSS('user/css/User.css');
	addJS('user/js/UserService.js');
	addJS('user/js/SettingsService.js');
	addJS('user/js/LoginController.js');
	addJS('user/js/SettingsController.js');

	addCSS('note/css/Note.css');
	addJS('note/js/NoteService.js');
	addJS('note/js/NoteController.js');

	addCSS('contact/css/Contact.css');
	addJS('contact/js/ContactService.js');
	addJS('contact/js/ContactController.js');

	addCSS('task/css/Task.css');
	addJS('task/js/TaskService.js');
	addJS('task/js/TaskController.js');

	addCSS('report/css/Report.css');
	addJS('report/js/ReportService.js');
	addJS('report/js/ReportController.js');

	addJS('app/js/conf.js');
	addJS('app/js/app.js');

	// BUILD PLACEHOLDER

	// IE Start
	if (lessIE9()) {
		addJS('contrib/html5shiv/html5shiv.min.js');
		addJS('contrib/respond/respond.min.js');
	}
	// IE End

	// ==========================================================================//

	function lessIE9() {
		var b = document.createElement('b')
		b.innerHTML = '<!--[if lt IE 9]><i></i><![endif]-->'
		return b.getElementsByTagName('i').length === 1
	}

	function addCSS(css) {
		CSSES.push(css);
	}

	function addJS(js) {
		JSES.push(js);
	}

	var baseUrl = '', sync = true;

	addTag('base', {
		href : baseUrl
	});
	for (var i = 0; i < CSSES.length; i++) {
		addTag('link', {
			rel : 'stylesheet',
			href : CSSES[i] + "?" + G_VERSION,
			type : 'text/css'
		}, sync);
	}
	for (var i = 0; i < JSES.length; i++) {
		addTag('script', {
			src : JSES[i] + "?" + G_VERSION
		}, sync);
	}

	function addTag(name, attributes, sync) {
		var el = document.createElement(name), attrName;
		for (attrName in attributes) {
			el.setAttribute(attrName, attributes[attrName]);
		}
		var headEl = document.getElementsByTagName('head')[0];
		sync ? document.write(outerHTML(el)) : headEl.appendChild(el);
	}

	function outerHTML(node) {
		// if IE, Chrome take the internal method otherwise build one
		return node.outerHTML || (function(n) {
			var div = document.createElement('div'), h;
			div.appendChild(n);
			h = div.innerHTML;
			div = null;
			return h;
		})(node);
	}
})();

// force page reload when new update is available
window.applicationCache
		&& window.applicationCache
				.addEventListener(
						'updateready',
						function(e) {
							if (window.applicationCache.status == window.applicationCache.UPDATEREADY) {
								window.applicationCache.swapCache();
								window.location.reload();
							}
						}, false);

(function() {
	'use strict';
	if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
		var msViewportStyle = document.createElement('style')
		msViewportStyle.appendChild(document
				.createTextNode('@-ms-viewport{width:auto!important}'))
		document.querySelector('head').appendChild(msViewportStyle)
	}
})();
