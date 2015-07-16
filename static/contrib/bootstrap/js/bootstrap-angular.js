angular
		.module('bootstrap-angular', [])
		.directive(
				'buttonsRadio',
				[ function() {
					return {
						restrict : 'E',
						scope : {
							model : '=',
							options : '=',
							suffix : '='
						},
						controller : [
								'$scope',
								'$element',
								function($scope, $element) {
									$scope.activate = function(option, $event) {
										$scope.model = option[$element
												.attr("idProperty")];
										if ($event.stopPropagation) {
											$event.stopPropagation();
										}
										if ($event.preventDefault) {
											$event.preventDefault();
										}
										$event.cancelBubble = true;
										$event.returnValue = false;
									};
									$scope.isActive = function(option) {
										return option[$element
												.attr("idProperty")] == $scope.model;
									};
									$scope.getName = function(option) {
										return option[$element
												.attr("nameProperty")];
									};
								} ],
						template : "<button type='button' class='btn btn-{{suffix ? suffix : \"default\"}}' ng-class='{active: isActive(option)}'"
								+ "ng-repeat='option in options' ng-click='activate(option, $event)'>{{getName(option)}} "
								+ "</button>"
					}
				} ]).directive('tooltip', [ function() {

			return {
				restrict : 'A',
				scope : true,
				link : function($scope, elmt, attrs) {
					$(elmt).prop('title', attrs.title);
					$(elmt).tooltip({
						container : 'body'
					});
				}
			};
		} ]);