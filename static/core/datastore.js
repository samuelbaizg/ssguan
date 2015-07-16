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

angular
		.module('datastore', [])
		.service(
				'dsHttp',
				[
						'$http',
						'$rootScope',
						'$q',
						'$filter',
						function($http, $rootScope, $q, $filter) {
							var baseUrl = window.location.origin;

							var requests = {};

							function Request(ctx) {
								this.ctx = ctx;
								this._cSTARTED = 'started';
								this._cSUCCESS = 'success';
								this._cERROR = 'error';
								this._step = null;
								this.status = null;
								this.message = null;
								this.data = null;

								this.isInProgress = function() {
									return this._step == this._cSTARTED;
								};
								this.isSuccess = function() {
									return this._step == this._cSUCCESS;
								};
								this.isFailed = function() {
									return this._step == this._cERROR;
								};
								this.start = function() {
									this._step = this._cSTARTED;
									$rootScope.$emit("EVENT_DSSTATUS_UPDATE",
											this);
								};
								this.succeed = function(status, message, data) {
									this._step = this._cSUCCESS;
									this.status = status,
											this.message = message,
											this.data = data
									$rootScope.$emit("EVENT_DSSTATUS_UPDATE",
											this);
								};

								this.failed = function(status, message, data) {
									this._step = this._cERROR;
									this.status = status,
											this.message = message,
											this.data = data
									$rootScope.$emit("EVENT_DSSTATUS_UPDATE",
											this);
								};
							}

							function newRequest(ctx) {
								function _newRequest(ctx) {
									delete requests[ctx];
									requests[ctx] = new Request(ctx);
									return requests[ctx];
								}
								if (ctx == null) {
									throw new Error("ctx can't be null.");
								}
								var request = requests[ctx];
								if (request != null && request.isInProgress()) {
									throw new Error('the previous request to "'
											+ ctx + '" is still in progress. ');
								} else {
									return _newRequest(ctx);
								}
							}

							function getURL(ctx) {
								return "/" + ctx;
							}

							var factory = {};

							factory.post = function(ctx, postData, postConfig) {
								var deferred = $q.defer();
								try {
									var request = newRequest(ctx);
									request.start();
									if (postData == null) {
										postData = {};
									}
									var url = getURL(ctx);
									var i = url.indexOf("?");
									if (i > 0) {
										var paramList = url.substring(i + 1)
												.split(",");
										for ( var j in paramList) {
											var pl = paramList[j].split("=");
											postData[pl[0]] = pl[1];
										}
										url = url.substring(0, i);
									}

									var promise = $http.post(url, postData,
											postConfig);

									promise = promise
											.success(function(data, status,
													headers, config) {
												if (status == 200
														&& data.status == "core_status_success") {
													request.succeed(
															data.status,
															data.message,
															data.data);
													deferred.resolve(data.data);
												} else {
													data = {
														status : data.status,
														message : data.message,
														data : data.data
													}
													request.failed(data.status,
															data.message,
															data.data);
													deferred.reject(data);
												}
											});

									promise = promise
											.error(function(data, status,
													headers, config) {
												data = {
													status : status,
													message : null
												};
												if (status == 0) {
													data.status = "core_status_http0_networkrefused";
													data.message = $filter(
															'translate')(
															data.status);
												}
												if (status == 500) {
													data.status = "core_status_http500_internalservererror";
													data.message = $filter(
															'translate')(
															data.status);
												}
												request.failed(data.status,
														data.message);
												deferred.reject(data);
											});
								} catch (e) {
									if (console) {
										console.log(e.message);
									}
									var message = $filter('translate')(
											'core_error_duplicatesubmit')
									// infobox.alert(message);
								}
								return deferred.promise;
							};
							return factory;
						} ])
		.directive(
				'dsStatus',
				[
						'$rootScope',
						'$filter',
						'$timeout',
						function($rootScope, $filter, $timeout) {

							return {
								restrict : 'A',
								link : function($scope, $elmt, $attrs) {
									var ctx = $attrs.dsStatus;
									if (ctx == null) {
										throw new Error(
												"dataStatus must set ctx property.");
									}

									function _getInProgressMessage(request) {
										var msg = null;
										if (request.ctx.indexOf("save") > -1) {
											msg = "core_label_saving";
										} else if (request.ctx
												.indexOf("delete") > -1) {
											msg = "core_label_deleting";
										} else if (request.ctx.indexOf("list") > -1
												|| request.ctx.indexOf("data") > -1) {
											msg = "core_label_loading";
										} else {
											msg = "core_label_submiting";
										}
										msg = $filter("translate")(msg);
										var html = '<span><i class="fa fa-spinner fa-pulse fa-lg"><font>';
										html += msg + '</font></i></span>';
										return html;
									}

									function _getSuccessMessage(request) {
										var msg = null;
										if (request.message == null
												|| request.message == '') {

											if (request.ctx.indexOf("save") > -1) {
												msg = "core_label_savedin";
											} else if (request.ctx
													.indexOf("delete") > -1) {
												msg = "core_label_deletedin";
											} else if (request.ctx
													.indexOf("list") > -1
													|| request.ctx
															.indexOf("data") > -1) {
												msg = "core_label_loadedin";
											} else {
												msg = "core_label_submitedin";
											}
											var date = new Date();
											var timeStr = $filter('date')(date,
													'HH: mm: ss');
											msg = $filter("translate")(msg, {
												datetime : timeStr
											});
										} else {
											msg = request.message;
										}
										if ($attrs.zerokey != undefined) {
											var length = 0;
											var i = $attrs.zerokey
													.indexOf(".length");
											if (i == -1) {
												length = request.data[$attrs.zerokey];
											} else if (i == 0) {
												length = request.data.length;
											} else {
												length = request.data[$attrs.zerokey[
														0, i - 1]].length;
											}
											if (length == 0) {
												msg = $filter("translate")(
														"core_label_norecords");
											} else {
												msg = '';
											}
										}
										var html = "";
										if (msg != '') {
											var html = '<span><i class="fa fa-check-circle-o fa-lg"><font>';
											html += msg + '</font></i></span>';
										}
										return html;
									}

									function _getErrorMessage(request) {
										return request.message;
									}

									function _dsStatusUpdate($event, request) {
										var showinprogress = $attrs.showinprogress == 'false' ? false
												: true;
										var showsuccess = $attrs.showsuccess == 'false' ? false
												: true;
										var showerror = $attrs.showerror == 'false' ? false
												: true;
										var selector = "[ds-status='"
												+ $attrs.dsStatus + "']";
										var message = request.message != null ? request.message
												: '';
										if (request.isInProgress()
												&& !request.inprogressShowed
												&& showinprogress) {
											var html = _getInProgressMessage(request);
											$timeout(function() {
												$(selector).html(html);
											}, 0);
											request.inprogressShowed = true;
										} else if (request.isSuccess()) {
											if (showsuccess
													&& !request.successShowed) {
												var html = _getSuccessMessage(request);
												$timeout(function() {
													$(selector).html(html);
												}, 0);
												request.successShowed = true;
											}
											if (!showsuccess) {
												$timeout(function() {
													$(selector).html("");
												}, 0);
											}
										} else if (request.isFailed()) {
											if (!request.errorShowed
													&& showerror) {
												infobox
														.alert(
																_getErrorMessage(request),
																function() {
																	if (request.status == "core_error_session_expired") {
																		$rootScope
																				.$broadcast(
																						"EVENT_LOGIN_REDIRECT",
																						request.data);
																	}
																});
											}
											$timeout(function() {
												$(selector).html("");
											}, 0);
											request.errorShowed = true;
										}
									}

									$rootScope
											.$on(
													"EVENT_DSSTATUS_UPDATE",
													function($event, request) {
														if (ctx == "*") {
															_dsStatusUpdate(
																	$event,
																	request);
														} else {
															$
																	.each(
																			ctx
																					.split(","),
																			function(
																					i,
																					c) {
																				if (request.ctx == c) {
																					_dsStatusUpdate(
																							$event,
																							request);
																				}
																			});
														}

													});

								}
							};

						} ]);