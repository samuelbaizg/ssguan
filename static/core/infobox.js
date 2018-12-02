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

(function(root, factory) {
	if (typeof define === "function" && define.amd) {
		define([ "jquery" ], factory);
	} else if (typeof exports === "object") {
		module.exports = factory(require("jquery"));
	} else {
		root.infobox = factory(root.jQuery);
	}
}
		(
				this,
				function init($, undefined) {
					var templates = {
						dialog : "<div class='bootbox modal' tabindex='-1' role='dialog'>"
								+ "<div class='modal-dialog'>"
								+ "<div class='modal-content'>"
								+ "<div class='modal-body'><div class='bootbox-body'></div></div>"
								+ "</div>" + "</div>" + "</div>",
						header : "<div class='modal-header'>"
								+ "<h4 class='modal-title'></h4>" + "</div>",
						footer : "<div class='modal-footer'></div>",
						closeButton : "<button type='button' class='bootbox-close-button close' data-dismiss='modal' aria-hidden='true'>&times;</button>",
						form : "<form class='bootbox-form'></form>",
						inputs : {
							text : "<input class='bootbox-input bootbox-input-text form-control' autocomplete=off type=text />",
							textarea : "<textarea class='bootbox-input bootbox-input-textarea form-control'></textarea>",
							email : "<input class='bootbox-input bootbox-input-email form-control' autocomplete='off' type='email' />",
							select : "<select class='bootbox-input bootbox-input-select form-control'></select>",
							checkbox : "<div class='checkbox'><label><input class='bootbox-input bootbox-input-checkbox' type='checkbox' /></label></div>",
							date : "<input class='bootbox-input bootbox-input-date form-control' autocomplete=off type='date' />",
							time : "<input class='bootbox-input bootbox-input-time form-control' autocomplete=off type='time' />",
							number : "<input class='bootbox-input bootbox-input-number form-control' autocomplete=off type='number' />",
							password : "<input class='bootbox-input bootbox-input-password form-control' autocomplete='off' type='password' />"
						}
					};
					var defaults = {
						locale : "en",
						backdrop : true,
						animate : true,
						className : null,
						closeButton : true,
						show : true,
						container : "body"
					};

					function _t(key) {
						var locale = locales[defaults.locale];
						return locale ? locale[key] : locales.en[key];
					}

					function processCallback(e, dialog, callback) {
						e.stopPropagation();
						e.preventDefault();
						var preserveDialog = $.isFunction(callback)
								&& callback(e) === false;
						if (!preserveDialog) {
							dialog.modal("hide");
						}
					}

					function each(collection, iterator) {
						var index = 0;
						$.each(collection, function(key, value) {
							iterator(key, value, index++);
						});
					}

					function sanitize(options) {
						if (typeof options !== "object") {
							throw new Error(
									"Please supply an object of options");
						}
						options = $.extend({}, defaults, options);
						options.title = options.title == undefined ? _t('TITLE')
								: options.title;
						if (!options.buttons) {
							options.buttons = {};
						}
						options.backdrop = options.backdrop ? "static" : false;
						var buttons = options.buttons;
						var total = Object.keys(buttons).length;
						each(buttons, function(key, button, index) {
							if ($.isFunction(button)) {
								button = buttons[key] = {
									callback : button
								};
							}
							if ($.type(button) !== "object") {
								throw new Error("button with key " + key
										+ " must be an object");
							}
							if (!button.label) {
								button.label = key;
							}
							if (!button.className) {
								if (total <= 2 && index === total - 1) {
									button.className = "btn-primary";
								} else {
									button.className = "btn-default";
								}
							}
						});
						return options;
					}

					function mapArguments(args, properties) {
						var argn = args.length;
						var options = {};

						if (argn < 1 || argn > 2) {
							throw new Error("Invalid argument length");
						}

						if (argn === 2 || typeof args[0] === "string") {
							options[properties[0]] = args[0];
							options[properties[1]] = args[1];
						} else {
							options = args[0];
						}

						return options;
					}

					function mergeArguments(defaults, args, properties) {
						return $.extend(true, {}, defaults, mapArguments(args,
								properties));
					}

					function mergeDialogOptions(className, labels, properties,
							args) {
						var baseOptions = {
							className : className,
							buttons : createLabels.apply(null, labels)
						};

						return validateButtons(mergeArguments(baseOptions,
								args, properties), labels);
					}
					function createLabels() {
						var buttons = {};
						for (var i = 0, j = arguments.length; i < j; i++) {
							var argument = arguments[i];
							var key = argument.toLowerCase();
							var value = argument.toUpperCase();
							buttons[key] = {
								label : _t(value)
							};
						}
						return buttons;
					}

					function validateButtons(options, buttons) {
						var allowedButtons = {};
						each(buttons, function(key, value) {
							allowedButtons[value] = true;
						});

						each(options.buttons, function(key) {
							if (allowedButtons[key] === undefined) {
								throw new Error("button key " + key
										+ " is not allowed (options are "
										+ buttons.join("\n") + ")");
							}
						});
						return options;
					}

					var exports = {};

					exports.dialog = function(options) {
						options = sanitize(options);
						var dialog = $(templates.dialog);
						var innerDialog = dialog.find(".modal-dialog");
						var body = dialog.find(".modal-body");
						var buttons = options.buttons;
						var buttonStr = "";
						var callbacks = {
							onEscape : options.onEscape
						};

						each(buttons, function(key, button) {
							buttonStr += "<button data-bb-handler='" + key
									+ "' type='button' class='btn "
									+ button.className + "'>" + button.label
									+ "</button>";
							callbacks[key] = button.callback;
						});

						body.find(".bootbox-body").html(options.message);

						if (options.title) {
							body.before(templates.header);
						}

						if (options.closeButton) {
							var closeButton = $(templates.closeButton);

							if (options.title) {
								dialog.find(".modal-header").prepend(
										closeButton);
							} else {
								closeButton.css("margin-top", "-10px")
										.prependTo(body);
							}
						}
						if (options.title) {
							dialog.find(".modal-title").html(options.title);
						}

						if (buttonStr.length) {
							body.after(templates.footer);
							dialog.find(".modal-footer").html(buttonStr);
						}

						dialog.on("hidden.bs.modal", function(e) {
							if (e.target === this) {
								dialog.remove();
							}
						});

						dialog.on("shown.bs.modal", function() {
							dialog.find(".btn-primary:first").focus();
						});

						dialog.on("escape.close.bb", function(e) {
							if (callbacks.onEscape) {
								processCallback(e, dialog, callbacks.onEscape);
							}
						});

						dialog.on("click", ".modal-footer button", function(e) {
							var callbackKey = $(this).data("bb-handler");
							processCallback(e, dialog, callbacks[callbackKey]);
						});

						dialog.on("click", ".bootbox-close-button",
								function(e) {
									processCallback(e, dialog,
											callbacks.onEscape);
								});

						dialog.on("keyup", function(e) {
							if (e.which === 27) {
								dialog.trigger("escape.close.bb");
							}
						});

						$(options.container).append(dialog);

						dialog.modal({
							backdrop : options.backdrop,
							keyboard : false,
							show : false
						});
						if (options.show) {
							dialog.modal("show");
						}
						return dialog;
					};

					exports.alert = function() {
						var options;

						options = mergeDialogOptions("alert", [ "ok" ], [
								"message", "callback" ], arguments);

						if (options.callback && !$.isFunction(options.callback)) {
							throw new Error(
									"alert requires callback property to be a function when provided");
						}

						options.buttons.ok.callback = options.onEscape = function() {
							if ($.isFunction(options.callback)) {
								return options.callback();
							}
							return true;
						};

						return exports.dialog(options);
					};

					exports.confirm = function() {
						var options;

						options = mergeDialogOptions("confirm", [ "cancel",
								"confirm" ], [ "message", "callback" ],
								arguments);

						options.buttons.cancel.callback = options.onEscape = function() {
							return options.callback(false);
						};

						options.buttons.confirm.callback = function() {
							return options.callback(true);
						};

						if (!$.isFunction(options.callback)) {
							throw new Error("confirm requires a callback");
						}

						return exports.dialog(options);
					};

					exports.setDefaults = function() {
						var values = {};

						if (arguments.length === 2) {
							values[arguments[0]] = arguments[1];
						} else {
							values = arguments[0];
						}
						$.extend(defaults, values);
					};

					var locales = {
						en : {
							OK : "OK",
							CANCEL : "Cancel",
							CONFIRM : "OK",
							TITLE : "Info"
						},
						zh_CN : {
							OK : "OK",
							CANCEL : "取消",
							CONFIRM : "确认",
							TITLE : "提示"
						}
					};

					exports.init = function(_$) {
						return init(_$ || $);
					};
					return exports;
				}));
