angular
		.module('bootstrap-typeahead', [])
		.directive(
				'bootstrapTypeahead',
				[ function() {

					return {
						restrict : 'A',
						scope : {
							model : '=ngModel',
							tasource : '&tasource',
							readonly : '=ngReadonly',
							itemvalue : '=itemvalue'
						},
						replace : false,
						link : function($scope, elmt, attrs) {
							elmt = $(elmt);
							if (attrs.placeholder) {
								elmt.prop("placeholder", attrs.placeholder);
							}

							$scope.$on('$destroy', function() {
								elmt.typeahead('destroy');
							});
							
							initBootstrapTypeahead($scope, elmt, attrs);

							$scope.$watch('readonly',
									function() {
										if ($scope.readonly) {
											elmt.typeahead('destroy');
										} else {
											initBootstrapTypeahead($scope,
													elmt, attrs);
										}
									});
							

							function initBootstrapTypeahead($scope, elmt, attrs) {
								var options = attrs.bootstrapTypeahead ? attrs.bootstrapTypeahead
										: '{}';
								if (attrs.tasource == null) {
									throw new Error("tasource must be defined.")
								}
								options = $scope.$eval(options);
								options.source = $scope.tasource();
								if (options.source && options.source.length > 0
										&& (typeof options.source[0] == 'object')
										&& attrs.itemvaluekey == undefined) {
									throw new Error(
											"itemvaluekey must be defined if tasource is json array.")
								}
								if (attrs.itemvaluekey != undefined) {
									options.displayText = function(item) {
										return item.name;
									}
								}

								_watch();

								$scope.$watch('itemvalue', _watch);

								function _watch() {
									if (attrs.itemvaluekey != undefined && options.source) {
										var found = false;
										$
												.each(
														options.source,
														function(i, obj) {
															if (obj[attrs.itemvaluekey] == $scope.itemvalue) {
																elmt
																		.val(obj.name);
																found = true
																return false;
															}
														});
										if (!found) {
											elmt.val('');
										}
									}
								}

								options.afterSelect = function(item) {
									if (typeof item == 'object') {
										$scope.model = item.name;
										$scope.itemvalue = item[attrs.itemvaluekey];
										$scope.$apply();
									} else {
										$scope.model = item;
										$scope.$apply();
									}

								}
								elmt.typeahead(options);
								elmt.focus(function() {
									if (!elmt.is("[readonly]")) {
										elmt.typeahead('lookup');
									}
								});
							}
						}
					}

				} ]);
