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

var conf = {

	CONSTANTs : {

		I18N : {
			translations : I18N.translations,
			defaultLanguage : I18N.defaultLanguage
		}

	},

	SERVICEs : {
		"string" : StringService,
		"random" : RandomService,
		"number" : NumberService,
		"hashmap" : HashmapService,
		"storage" : StorageService
	},

	DIRECTIVEs : {
		"main" : MainDirective,
		"navbar" : NavbarDirective,
		"autosave" : AutoSaveDirective,
		'infinitescroll' : InfiniteScrollDirective
	},

	FILTERs : {
		"usubstr" : USubstrFilter,
		"uinsert" : UInsertFilter,
		"html2text" : HtmlToTextFilter
	},

	TEMPLATEs : {

		"main" : 'app/partials/Main.html',

		"/login" : {
			wsLeftCol : {
				bodyPath : 'user/partials/LoginForm.html',
				widthClass : "col-xs-12 col-sm-12 col-md-12 col-lg-12"
			}
		},
		"/settings" : {
			sidebar : {
				sidebarHeadPath : 'user/partials/SettingsSidebarHead.html',
				sidebarBodyPath : 'user/partials/SettingsSidebarBody.html',
				defaultOpen : true
			},
			wsLeftCol : {
				headPath : 'user/partials/SettingsListHead.html',
				bodyPath : 'user/partials/SettingsListBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-7 col-lg-7",
				maxWidthClass : "col-xs-12 col-sm-12 col-md-12 col-lg-12"
			},
			wsRightCol : {
				headPath : 'user/partials/SettingsEditHead.html',
				bodyPath : 'user/partials/SettingsEditBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-5 col-lg-5",
				maxWidthClass : "col-xs-12 col-sm-12 col-md-12 col-lg-12"
			}
		},
		"/note" : {
			shortcuts : [ {
				link : "EVENT_SHORTCUT_NOTEBOOK",
				title : "note_label_notebook",
				iconClass : "fa fa-book fa-2x"
			} ],
			sidebar : {
				sidebarHeadPath : 'note/partials/NoteSidebarHead.html',
				sidebarBodyPath : 'note/partials/NoteSidebarBody.html'
			},
			wsLeftCol : {
				headPath : 'note/partials/NoteListHead.html',
				bodyPath : 'note/partials/NoteListBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-3 col-lg-3",
				maxWidthClass : "col-xs-12 col-sm-12 col-md-12 col-lg-12"
			},
			wsRightCol : {
				headPath : 'note/partials/NoteEditHead.html',
				bodyPath : 'note/partials/NoteEditBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-9 col-lg-9",
				defaultOpen : false
			}
		},
		"/contact" : {
			shortcuts : [ {
				link : "EVENT_SHORTCUT_GROUP",
				title : "cont_label_group",
				iconClass : "fa fa-users fa-2x"
			} ],
			sidebar : {
				sidebarHeadPath : 'contact/partials/ContactSidebarHead.html',
				sidebarBodyPath : 'contact/partials/ContactSidebarBody.html'
			},
			wsLeftCol : {
				headPath : 'contact/partials/ContactListHead.html',
				bodyPath : 'contact/partials/ContactListBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-5 col-lg-5",
				maxWidthClass : "col-xs-12 col-sm-12 col-md-12 col-lg-12"
			},
			wsRightCol : {
				headPath : 'contact/partials/ContactEditHead.html',
				bodyPath : 'contact/partials/ContactEditBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-7 col-lg-7",
				defaultOpen : false
			}
		},
		"/task" : {
			shortcuts : [ {
				link : "EVENT_SHORTCUT_WORKSHEET",
				title : "task_label_worksheet",
				iconClass : "fa fa-tasks fa-2x"
			} ],
			sidebar : {
				sidebarHeadPath : 'task/partials/TaskSidebarHead.html',
				sidebarBodyPath : 'task/partials/TaskSidebarBody.html'
			},
			wsLeftCol : {
				headPath : 'task/partials/TaskListHead.html',
				bodyPath : 'task/partials/TaskListBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-5 col-lg-5",
				maxWidthClass : "col-xs-12 col-sm-12 col-md-12 col-lg-12"
			},
			wsRightCol : {
				headPath : 'task/partials/TaskEditHead.html',
				bodyPath : 'task/partials/TaskEditBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-7 col-lg-7",
				defaultOpen : false
			}
		},
		"/report" : {
			shortcuts : [],
			sidebar : {
				sidebarHeadPath : 'report/partials/ReportSidebarHead.html',
				sidebarBodyPath : 'report/partials/ReportSidebarBody.html',
				defaultOpen : false
			},
			wsLeftCol : {
				headPath : 'report/partials/ReportSearchHead.html',
				bodyPath : 'report/partials/ReportSearchBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-2 col-lg-2",
				maxWidthClass : "col-xs-12 col-sm-12 col-md-2 col-lg-2"
			},
			wsRightCol : {
				headPath : 'report/partials/ReportViewHead.html',
				bodyPath : 'report/partials/ReportViewBody.html',
				widthClass : "col-xs-12 col-sm-12 col-md-10 col-lg-10",
				defaultOpen : false
			}
		}
	},

	MODULEs : {

		"ngRoute" : {
			sysMod : true
		},
		"ngSanitize" : {
			sysMod : true
		},
		"pascalprecht.translate" : {
			sysMod : true
		},
		"bootstrap-wysiwyg" : {
			sysMod : true
		},
		"bootstrap-typeahead" : {
			sysMod : true
		},
		"bootstrap-tagsinput" : {
			sysMod : true
		},
		"bootstrap-datetimepicker" : {
			sysMod : true
		},
		"datastore" : {
			sysMod : true
		},
		"bootstrap-angular" : {
			sysMod : true
		},
		"userMod" : {

			controllers : {
				"loginController" : [ LoginController, "/login" ],
				"settingsController" : [ SettingsController, "/settings" ]
			},

			services : {
				"userService" : UserService,
				"settingsService" : SettingsService
			},

			directives : {

			},

			filters : {

			},

			dependencies : []

		},

		"noteMod" : {

			controllers : {
				"noteController" : [ NoteController, "/note" ]
			},

			services : {
				"noteService" : NoteService
			},

			directives : {

			},

			filters : {

			},

			dependencies : []
		},

		"contactMod" : {

			controllers : {
				"contactController" : [ ContactController, "/contact" ]
			},

			services : {
				"contactService" : ContactService
			},

			directives : {

			},

			filters : {

			},

			dependencies : []
		},

		"taskMod" : {

			controllers : {
				"taskController" : [ TaskController, "/task" ]
			},

			services : {
				"taskService" : TaskService
			},

			directives : {

			},

			filters : {

			},

			dependencies : []
		},
		"reportMod" : {

			controllers : {
				"reportController" : [ ReportController, "/report" ]
			},

			services : {
				"reportService" : ReportService
			},

			directives : {

			},

			filters : {

			},

			dependencies : []
		}

	}

};