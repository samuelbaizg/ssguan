angular
		.module('bootstrap-tagsinput', [])
		.directive(
				'bootstrapTagsinput',
				[ function() {

					return {
						restrict : 'A',
						scope : {
							submit : '&submit',
							model : '=ngModel',
							tasource : '&tasource'
						},
						replace : false,
						require : 'ngModel',
						link : function($scope, elmt, attrs) {
							elmt = $(elmt);

							initTagsinput($scope, elmt, attrs);
							bindTagsinput($scope, elmt, attrs);

							if (attrs.submit) {
								var elt = elmt.tagsinput('input');
								elt.keydown(function(e) {
									if (elt.val() == '' && e.keyCode == 13) {
										$scope.submit();
									}
								});
							}

							function initTagsinput($scope, elmt, attrs) {
								var options = attrs.bootstrapTagsinput ? attrs.bootstrapTagsinput
										: '{}';
								options = $scope.$eval(options);
								if (attrs.placeholder) {
									elmt.prop("placeholder", attrs.placeholder);
								}
								if (attrs.typeahead) {
									if (attrs.tasource == null) {
										throw new Error(
												"tasource must be defined with prop typehead.")
									}
									var typeahead = $scope
											.$eval(attrs.typeahead);
									typeahead.source = function(query) {
										return $scope.tasource();

									};
									options.typeahead = typeahead;
								}
								if (attrs.tasource) {
									attrs.$observe("tasource", function(value) {
										elmt.tagsinput(options);
									});
								}
								elmt.tagsinput(options);

							}

							function bindTagsinput($scope, elmt, attrs) {
								if ($scope.model != undefined
										&& !angular.isArray($scope.model)) {
									throw new Error($scope.model
											+ ' must be an Array.');
								}

								function _render() {
									if ($scope.model != undefined
											&& !angular.isArray($scope.model)) {
										$scope.model = [$scope.model];
									}
									if ($scope.model != null) {
										elmt.tagsinput('removeAll');
										for (var i = 0; i < $scope.model.length; i++) {
											elmt.tagsinput('add',
													$scope.model[i]);
										}
									}
								}

								_render();

								$scope.$watch("model", _render);

								elmt
										.on(
												'itemAdded',
												function(event) {
													if ($scope.model
															.indexOf(event.item) === -1)
														$scope.model
																.push(event.item);
												});

								elmt.on('itemRemoved', function(event) {
									var idx = $scope.model.indexOf(event.item);
									if (idx !== -1)
										$scope.model.splice(idx, 1);
								});
							}
						}

					}

				} ]);
