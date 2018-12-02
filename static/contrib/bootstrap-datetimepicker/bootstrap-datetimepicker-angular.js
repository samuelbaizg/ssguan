angular
		.module('bootstrap-datetimepicker', [])
		.directive(
				'bootstrapDatetimepicker',
				[ function() {

					return {
						restrict : 'A',
						scope : {
							model : '=ngModel',
							endmodel : "=endModel",
							onchange : "&ngChange",
						},
						replace : false,
						require : 'ngModel',
						link : function($scope, elmt, attrs) {
							elmt = $(elmt);
							initDatetimepicker($scope, elmt, attrs);
							bindDatetimepicker($scope, elmt, attrs);

							function initDatetimepicker($scope, elmt, attrs) {
								var options = attrs.bootstrapDatetimepicker ? attrs.bootstrapDatetimepicker
										: '{}';

								options = $scope.$eval(options);

								if (attrs.format) {
									options.format = attrs.format;
								}

								if (attrs.weekstart) {
									options.weekStart = attrs.weekstart;
								}

								if (attrs.viewmode) {
									options.viewMode = attrs.viewmode;
								}

								if (attrs.minviewmode) {
									options.minViewMode = attrs.minviewmode;
								}

								if (attrs.maskinput) {
									options.maskInput = attrs.maskinput == 'true' ? true
											: false;
								}

								if (attrs.pickdate) {
									options.pickDate = attrs.pickdate == 'true' ? true
											: false;
								}

								if (attrs.picktime) {
									options.pickTime = attrs.picktime == 'true' ? true
											: false;
								}

								if (attrs.pick12hourformat) {
									options.pick12HourFormat = attrs.pick12hourformat == 'true' ? true
											: false;
								}

								if (attrs.pickseconds) {
									options.pickSeconds = attrs.pickseconds == 'true' ? true
											: false;
								}

								if (attrs.startdate) {
									options.startDate = attrs.startdate;
								}

								if (attrs.enddate) {
									options.endDate = attrs.enddate;
								}

								elmt.datetimepicker(options);
							}

							function bindDatetimepicker($scope, elmt, attrs) {
								if (attrs.hideonchange != 'false') {
									elmt
											.datetimepicker()
											.on(
													'changeDate',
													function(ev) {
														$scope.model = elmt
																.data(
																		'datetimepicker')
																.formatDate(
																		ev.date);
														$scope.$apply();
														if (attrs.endModel) {
															if ($scope.endmodel == null) {
																$scope.endmodel = $scope.model;
															} else if ($scope.model > $scope.endmodel) {
																$scope.endmodel = $scope.model;
															}
														}
														$scope
																.$apply($scope.onchange);
														elmt
																.datetimepicker('hide');
													});
								}

								$scope.$watch('model',
										function(newval, oldval) {
											var val = newval == null ? ""
													: newval;
											elmt.data('datetimepicker')
													.setDate(val);
										}, true);

								$scope.$on('$destroy', function() {
									elmt.datetimepicker('destroy');
								});

							}
						}
					}

				} ]);
