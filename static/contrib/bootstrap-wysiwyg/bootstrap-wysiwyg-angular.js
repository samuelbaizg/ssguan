'use strict';
(function($) {
	if ($.fn.wysiwyg.locales == undefined) {
		$.fn.wysiwyg.locales = {};
	}
	$.fn.wysiwyg.locales['en'] = {
		"fontfamily" : "Font Family",
		"fontsize" : "Font Sizes",
		"bold" : "Bold",
		"italic" : "Italic",
		"strikethrough" : "Strike-through",
		"underline" : "Underline",
		"insertunorderlist" : "Bullet list",
		"insertorderedlist" : "Numbered list",
		"outdent" : "Decrease indent",
		"indent" : "Increase indent",
		"justifyleft" : "Align left",
		"justifycenter" : "Align centre",
		"justifyright" : "Align right",
		"justifyfull" : "Justify",
		"undo" : "Undo",
		"redo" : "Redo",
		"clearformat" : "Clear formatting",
		"fontsizes" : {
			1 : "Small",
			3 : "Normal",
			5 : "Huge"
		},

		"fontfamilies" : {
			"Arial" : "arial,helvetica,sans-serif",
			"Arial Black" : "arial black,avant garde",
			"Courier New" : "courier new,courier",
			"Tahoma" : "tahoma,arial,helvetica,sans-serif",
			"Times New Roman" : "times new roman,times",
			"Verdana" : "verdana,geneva"
		}
	}
}(jQuery));
angular
		.module('bootstrap-wysiwyg', [])
		.directive(
				'bootstrapWysiwyg',
				[
						'$timeout',
						function($timeout) {

							var templates = {
								fontfamily : '<a class="btn btn-default dropdown-toggle" data-toggle="dropdown" title="{title}"><i class="fa fa-font"></i><b class="caret"></b></a><ul class="dropdown-menu">{li}</ul>',
								fontsize : '<a class="btn btn-default dropdown-toggle" data-toggle="dropdown" title="{title}"><i class="fa fa-text-height"></i>&nbsp;<b class="caret"></b></a><ul class="dropdown-menu">{li}</ul>',
								bold : '<a class="btn btn-default" data-edit="bold" title="{title}"><i class="fa fa-bold"></i></a>',
								italic : '<a class="btn btn-default" data-edit="italic" title="{title}"><i class="fa fa-italic"></i></a>',
								strikethrough : '<a	class="btn btn-default" data-edit="strikethrough" title="{title}"><i class="fa fa-strikethrough"></i></a>',
								underline : '<a class="btn btn-default"	data-edit="underline" title="{title}"><i	class="fa fa-underline"></i></a>',
								insertunorderlist : '<a class="btn btn-default" data-edit="insertunorderedlist" title="{title}"><i class="fa fa-list-ul"></i></a>',
								insertorderedlist : '<a class="btn btn-default"	data-edit="insertorderedlist" title="{title}"><i class="fa fa-list-ol"></i></a>',
								outdent : '<a class="btn btn-default" data-edit="outdent" title="{title}"><i class="fa fa-outdent"></i></a>',
								indent : '<a class="btn btn-default" data-edit="indent" title="{title}"><i class="fa fa-indent"></i></a>',
								justifyleft : '<a class="btn btn-default" data-edit="justifyleft" title="{title}"><i class="fa fa-align-left"></i></a>',
								justifycenter : '<a class="btn btn-default" data-edit="justifycenter" title="{title}"><i class="fa fa-align-center"></i></a>',
								justifyright : '<a class="btn btn-default" data-edit="justifyright"	title="{title}"><i class="fa fa-align-right"></i></a>',
								justifyfull : '<a class="btn btn-default" data-edit="justifyfull" title="{title}"><i class="fa fa-align-justify"></i></a>',
								undo : '<a class="btn btn-default" data-edit="undo" title="{title}"><i class="fa fa-undo"></i></a>',
								redo : '<a class="btn btn-default" data-edit="redo"	title="{title}"><i class="fa fa-repeat"></i></a>'

							};

							return {
								restrict : 'A',
								replace : true,
								scope : false,
								require : 'ngModel',

								link : function($scope, $elmt, attrs, ngModel) {
									if (!attrs.id) {
										throw new Error(
												"bootstrapWysiwyg must define id's");
									}

									appendWysiwygControl(attrs);
									$scope.$on("EVENT_RESIZE_WYSIWYG",
											function($event, id) {
												if (id == attrs.id) {
													resizeWysiwyg(attrs);
												}
											});
									$("#" + attrs.id).load(function() {
										resizeWysiwyg(attrs);
									});
									bindWysiwyg($scope, $elmt, attrs, ngModel);

									if (attrs.readonly != undefined) {
										attrs
												.$observe(
														"readonly",
														function(value) {
															var wysiwygBodyObj = $("#"
																	+ attrs.id
																	+ "wysiwygBody");
															var wysiwygTooplbarObj = $("#"
																	+ attrs.id
																	+ "wysiwygToolbar");
															if (value == 'false') {
																wysiwygBodyObj
																		.prop(
																				"contenteditable",
																				true);
																wysiwygTooplbarObj
																		.show();
															} else {
																wysiwygBodyObj
																		.prop(
																				"contenteditable",
																				false);
																wysiwygTooplbarObj
																		.hide();
															}
															resizeWysiwyg(attrs);
														});
									}

								}
							}

							function bindWysiwyg($scope, $elmt, attrs, ngModel) {

								function _render() {
									var wysiwygBodyObj = $("#" + attrs.id
											+ "wysiwygBody");
									if (wysiwygBodyObj) {
										wysiwygBodyObj.html(ngModel.$viewValue
												|| '');
									}
								}
								ngModel.$render = _render;

								_render();

								var wysiwygBodyObj = $("#" + attrs.id
										+ "wysiwygBody");
								var wysiwygToolbarObj = $("#" + attrs.id
										+ "wysiwygToolbar");
								wysiwygBodyObj.on("keyup", function(e) {
									ngModel
											.$setViewValue(wysiwygBodyObj
													.html());
								});

								wysiwygToolbarObj.on("click mouseup", function(
										e) {
									ngModel
											.$setViewValue(wysiwygBodyObj
													.html());
								});

							}

							function resizeWysiwyg(attrs) {
								var wysiwygObj = $("#" + attrs.id);
								var wysiwygBodyObj = $("#" + attrs.id
										+ "wysiwygBody");
								var parentObj = wysiwygObj.parent();
								var siblingHeight = 0;
								$.each(wysiwygObj.siblings(), function(i,
										control) {
									siblingHeight += $(control).actual(
											"outerHeight", {
												includeMargin : true
											});
								});
								var wysiwygTooplbarObj = $("#" + attrs.id
										+ "wysiwygToolbar");
								if (attrs.readonly == 'false') {
									siblingHeight += wysiwygTooplbarObj
											.outerHeight() + 1;
								}

								var height = parentObj.height() - siblingHeight
										- 20;

								if (attrs.heightAdjustment != undefined) {
									if (attrs.heightAdjustment.indexOf("%") < 0) {
										height -= parseInt(attrs.heightAdjustment);
									} else {
										height = attrs.heightAdjustment;
									}
								}
								wysiwygBodyObj.height(height);
							}

							function appendWysiwygControl(attrs) {
								var html = "";
								html += getToolbarHtml(attrs, attrs.language);
								html += getWysiwygEditorHtml(attrs,
										attrs.language);
								var obj = $("#" + attrs.id);
								obj
										.addClass("bootstrap-wysiwyg bootstrap-wysiwyg-default");
								obj.html(html);
								$('.bootstrap-wysiwyg a[title]').tooltip({
									container : 'body'
								});
								$('.bootstrap-wysiwyg .dropdown-menu input')
										.click(function() {
											return false;
										})
										.change(
												function() {
													$(this)
															.parent(
																	'.dropdown-menu')
															.siblings(
																	'.dropdown-toggle')
															.dropdown('toggle');
												}).keydown('esc', function() {
											this.value = '';
											$(this).change();
										});
								var wysiwygObj = $("#" + attrs.id
										+ "wysiwygBody");
								wysiwygObj.wysiwyg();
							}

							function getWysiwygEditorHtml(attrs) {
								return '<div id="'
										+ attrs.id
										+ 'wysiwygBody" class="bootstrap-wysiwyg-editor"></div>';
							}

							function getToolbarHtml(attrs) {
								if (attrs.toolbar != undefined) {
									var clazz = "btn-toolbar bootstrap-wysiwyg-toolbar "
											+ attrs.toolbar;
									var toolbar = '<div id="'
											+ attrs.id
											+ 'wysiwygToolbar" class="'
											+ clazz
											+ '" data-role="editor-toolbar" data-target="#'
											+ attrs.id + 'wysiwygBody">';
									toolbar += getFontfamilyHtml(attrs,
											attrs.language);
									toolbar += getFontsizeHtml(attrs,
											attrs.language);
									toolbar += getFontHtml(attrs,
											attrs.language);
									toolbar += getInsertListHtml(attrs,
											attrs.language);
									toolbar += getIndentHtml(attrs,
											attrs.language);
									toolbar += getJustifyHtml(attrs,
											attrs.language);
									toolbar += getUndoHtml(attrs,
											attrs.language);
									toolbar += "</div>";
									return toolbar;
								} else {
									return "";
								}

							}

							function getFontfamilyHtml(attrs) {
								if (attrs.fontsize == 'false') {
									return "";
								}
								var btngroup = '<div class="btn-group">';
								btngroup += templates.fontfamily.replace(
										"{title}", getLocale(attrs.language,
												'fontfamily'));
								btngroup += '</div>';
								var fontfamilies = getLocale(attrs.language,
										"fontfamilies");
								var li = "";

								for ( var name in fontfamilies) {
									var value = fontfamilies[name];
									li += '<li><a data-edit="fontName ' + name
											+ '" style="font-family:\'' + name
											+ '\'">' + value + '</a></li>';
								}
								btngroup = btngroup.replace("{li}", li);
								return btngroup;
							}

							function getFontsizeHtml(attrs) {
								if (attrs.fontfamily == 'false') {
									return "";
								}
								var btngroup = '<div class="btn-group">';
								btngroup += templates.fontsize.replace(
										"{title}", getLocale(attrs.language,
												'fontsize'));
								btngroup += '</div>';
								var fontsizes = getLocale(attrs.language,
										'fontsizes');
								var li = "";
								for ( var name in fontsizes) {
									var value = fontsizes[name];
									li += '<li><a data-edit="fontSize ' + name
											+ '"><font size="' + name + '">'
											+ value + '</font></a></li>';
								}
								btngroup = btngroup.replace("{li}", li);
								return btngroup;
							}

							function getFontHtml(attrs) {
								var btngroup = '';
								if (attrs.bold == undefined
										|| attrs.bold == 'true') {
									btngroup += templates.bold.replace(
											"{title}", getLocale(
													attrs.language, 'bold'));
								}
								if (attrs.italic == undefined
										|| attrs.italic == 'true') {
									btngroup += templates.italic.replace(
											"{title}", getLocale(
													attrs.language, 'italic'));
								}
								if (attrs.strikethrough == undefined
										|| attrs.strikethrough == 'true') {
									btngroup += templates.strikethrough
											.replace("{title}", getLocale(
													attrs.language,
													'strikethrough'));
								}
								if (attrs.underline == undefined
										|| attrs.underline == true) {
									btngroup += templates.underline.replace(
											"{title}",
											getLocale(attrs.language,
													'underline'));
								}
								if (btngroup == '') {
									return "";
								}
								btngroup = '<div class="btn-group">' + btngroup;
								btngroup += '</div>';
								return btngroup;
							}

							function getIndentHtml(attrs) {
								var btngroup = '';
								if (attrs.insertlist == undefined
										|| attrs.insertlist == 'true') {
									btngroup += templates.indent.replace(
											"{title}", getLocale(
													attrs.language, 'indent'));
									btngroup += templates.outdent.replace(
											"{title}", getLocale(
													attrs.language, 'outdent'));
								}
								if (btngroup == '') {
									return "";
								}
								btngroup = '<div class="btn-group">' + btngroup;
								btngroup += '</div>';
								return btngroup;
							}

							function getInsertListHtml(attrs) {
								var btngroup = '';
								if (attrs.indent == undefined
										|| attrs.indent == 'true') {
									btngroup += templates.insertunorderlist
											.replace("{title}", getLocale(
													attrs.language,
													'insertunorderlist'));
									btngroup += templates.insertorderedlist
											.replace("{title}", getLocale(
													attrs.language,
													'insertorderedlist'));
								}
								if (btngroup == '') {
									return "";
								}
								btngroup = '<div class="btn-group">' + btngroup;
								btngroup += '</div>';
								return btngroup;
							}

							function getJustifyHtml(attrs) {
								var btngroup = '';
								if (attrs.justifyfull == undefined
										|| attrs.justifyfull == 'true') {
									btngroup += templates.justifyleft.replace(
											"{title}", getLocale(
													attrs.language,
													'justifyleft'));
									btngroup += templates.justifycenter
											.replace("{title}", getLocale(
													attrs.language,
													'justifycenter'));
									btngroup += templates.justifyright.replace(
											"{title}", getLocale(
													attrs.language,
													'justifyright'));
									btngroup += templates.justifyfull.replace(
											"{title}", getLocale(
													attrs.language,
													'justifyfull'));
								}
								if (btngroup == '') {
									return "";
								}
								btngroup = '<div class="btn-group">' + btngroup;
								btngroup += '</div>';
								return btngroup;
							}

							function getUndoHtml(attrs) {
								var btngroup = '';
								if (attrs.undo == undefined
										|| attrs.undo == 'true') {
									btngroup += templates.undo.replace(
											"{title}", getLocale(
													attrs.language, 'undo'));
									btngroup += templates.redo.replace(
											"{title}", getLocale(
													attrs.language, 'redo'));
								}
								if (btngroup == '') {
									return "";
								}
								btngroup = '<div class="btn-group">' + btngroup;
								btngroup += '</div>';
								return btngroup;
							}

							function getLocale(language, key) {
								var locales = $.fn.wysiwyg.locales;
								if (locales[language] != undefined) {
									return locales[language][key];
								} else {
									return locales['en'][key];
								}
							}

						} ]);
