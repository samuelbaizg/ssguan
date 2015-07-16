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

var ReportController = function($scope, $rootScope, $filter, reportService) {

	var SERIES_COLORS = [ '#FF0000', '#0000FF', '#00FF00', '#470000',
			'#FFB600', '#FF00FF', '#00FFFF', '#800000', '#1C1C1C', '#E0FFE0',
			'#85802b', '#00749F', '#73C774', '#C7754C', '#17BDB8', '#EAA228',
			'#839557', '#4BB2C5', '#579575', '#C5B47F', '#D43F3A', '#337AB7',
			'#5BC0DE', '#5CB85C', '#F0AD4E', '#D9534F', '#FFFFE0', '#E0FFE0',
			'#30C0FF', '#F0C0FF' ]

	$scope.$on('EVENT_CLOSE_WSRIGHTCOL', function() {
		$rootScope.showWsRightCol(true);
	});

	$scope.reportBaseData = null;

	$scope.searchCriteria = {
		groupKey : null,
		assigneeKeys : null,
		worksheetKeys : null,
		startDate : null,
		endDate : null,

		reset : function() {
			this.worksheetKeys = null;
			this.startDate = $rootScope.envVar.RPT_SEARCH_START_DATE;
			this.endDate = $rootScope.envVar.RPT_SEARCH_END_DATE;
			this.groupKey = null;
			this.assigneeKeys = null;
		}
	}

	function initReportModule() {
		reportService.getReportBaseData().then(function(data) {
			$scope.reportBaseData = data;
			$scope.worksheets = data.worksheets;
			$scope.assignees = data.assignees;
			$rootScope.showWsRightCol(true);
			$scope.switchReportType('taskReport', 'rept_label_progressreport');
		});
	}

	initReportModule();

	$scope.moreReports = function() {
		$("#reportSearchTypeDialog").modal("show");
	}

	$scope.switchReportType = function(activeRptType, activeRptTypeLabel) {
		$("#reportSearchTypeDialog").modal("hide");
		$scope.activeRptType = activeRptType;
		$scope.searchCriteria.reset();
		$scope.activeRptTypeLabel = $filter("translate")(activeRptTypeLabel);
		$rootScope.showWsRightCol(true);

	}

	$scope.groupChange = function() {
		if ($scope.searchCriteria.groupKey == null
				|| $scope.searchCriteria.groupKey == '') {
			$scope.worksheets = $scope.reportBaseData.worksheets;
			$scope.assignees = $scope.reportBaseData.assignees;
			$scope.searchCriteria.worksheetKeys = null;
		} else {
			var worksheets = [];
			$scope.searchCriteria.worksheetKeys = [];
			$.each($scope.reportBaseData.worksheets, function(i, worksheet) {
				if (worksheet.groupKey == $scope.searchCriteria.groupKey) {
					worksheets.push(worksheet);
					$scope.searchCriteria.worksheetKeys.push(worksheet.key);
				}
			});
			$scope.worksheets = worksheets;
			var assignees = [];
			$scope.searchCriteria.assigneeKeys = [];
			$.each($scope.reportBaseData.assignees,
					function(i, assignee) {
						if (assignee.groupKeys
								.indexOf($scope.searchCriteria.groupKey) > -1) {
							assignees.push(assignee);
							$scope.searchCriteria.assigneeKeys
									.push(assignee.key);
						}
					});
			$scope.assignees = assignees;
		}
	}

	$scope.generateProgressChart = function() {
		$rootScope.showWsRightCol(false);
		$scope.activeReport = "progress";
		$scope.activeReportLabel = $filter("translate")(
				'rept_label_progresschart');
		$("#progressLineDiv, #progressBarDiv").html("");
		$scope.deviationTasks = null;
		function _generateProgressLineChart(data) {
			var plot1 = $.jqplot('progressLineDiv', [ data.plan, data.actual,
					data.forecast ], {
				seriesColors : SERIES_COLORS,
				axes : {
					xaxis : {
						renderer : $.jqplot.DateAxisRenderer,
						tickOptions : {
							formatString : '%b&nbsp;%#d'
						}
					},
					yaxis : {
						tickOptions : {
							formatString : '%d',
						}
					}
				},
				seriesDefaults : {
					lineWidth : 2,
					markerOptions : {
						size : 3,
						style : "diamond"
					}
				},
				legend : {
					renderer : jQuery.jqplot.EnhancedLegendRenderer,
					show : true,
					showSwatch : true,
					labels : [
							$filter("translate")(
									"rept_label_planfinishquantity"),
							$filter("translate")(
									"rept_label_actualfinishquantity"),
							$filter("translate")(
									"rept_label_forecastfinishquantity") ],
					// placement: 'outside',
					location : 'se'
				}
			});
		}

		function _generateProgressBarChart(barPriorities, barTaskCounts) {
			var plot3 = $.jqplot('progressBarDiv', barTaskCounts,
					{
						seriesColors : SERIES_COLORS,
						stackSeries : false,
						seriesDefaults : {
							renderer : $.jqplot.BarRenderer,
							rendererOptions : {
								barDirection : 'vertical',
								highlightMouseDown : true,
								barMargin : 20,
							},
							pointLabels : {
								show : true,
								location : 'n',
								formatString : '%d',
								hideZeros : true
							},
						},
						axes : {
							xaxis : {
								renderer : $.jqplot.CategoryAxisRenderer,
								ticks : barPriorities
							},
							yaxis : {
								padMin : 1,
								formatString : '%d'
							}
						},
						legend : {
							renderer : jQuery.jqplot.EnhancedLegendRenderer,
							show : true,
							showSwatch : true,
							labels : [
									$filter("translate")(
											"rept_label_planfinishquantity"),
									$filter("translate")(
											"rept_label_actualfinishquantity"),
									$filter("translate")(
											"rept_label_cancelquantity") ],
							location : 'se'
						}
					});
		}

		reportService.getRptProgressData($scope.searchCriteria.groupKey,
				$scope.searchCriteria.startDate, $scope.searchCriteria.endDate,
				$scope.searchCriteria.worksheetKeys,
				$scope.searchCriteria.assigneeKeys).then(function(data) {
			_generateProgressLineChart(data.progressLine);
			var barPriorities = [], barTaskCounts = [ [], [], [] ];
			$.each(data.progressBar, function(priority, statusData) {
				barPriorities.push($filter("translate")(priority));
				barTaskCounts[0].push(statusData[0]);// plan
				barTaskCounts[1].push(statusData[1]);// actual
				barTaskCounts[2].push(statusData[2]);// cancel
			});

			_generateProgressBarChart(barPriorities, barTaskCounts);
			$scope.deviationTasks = data.deviationTasks;
		});
	};

	$scope.generateAllocationChart = function() {
		$rootScope.showWsRightCol(false);
		$scope.allocationData = null;
		$scope.activeReport = "allocation";
		$scope.activeReportLabel = $filter("translate")(
				'rept_label_allocationchart');
		$("#allocationLineDiv,#allocationBarDiv").html("");
		function _generateAllocationLineChart(k, lineArray, legendArray) {
			var allocationLineDiv = $(
					"<div/>",
					{
						"id" : "lineDiv" + k,
						"class" : "col-sm-12 col-xs-12 col-md-12 col-lg-12 report-chart"
					});
			$("#allocationLineDiv").append(allocationLineDiv);
			var plot1 = $.jqplot("lineDiv" + k, lineArray, {
				seriesColors : SERIES_COLORS,
				axes : {
					xaxis : {
						renderer : $.jqplot.DateAxisRenderer,
						tickOptions : {
							formatString : '%b&nbsp;%#d'
						}
					},
					yaxis : {
						tickOptions : {
							formatString : '%d',
						}

					}

				},
				seriesDefaults : {
					lineWidth : 2,
					markerOptions : {
						size : 3,
						style : "diamond"
					}
				},
				legend : {
					renderer : jQuery.jqplot.EnhancedLegendRenderer,
					show : true,
					showSwatch : true,
					labels : legendArray,
					location : 'se'
				}
			});
		}

		function _generateAllocationBarChart(barAssignees, barTaskCounts,
				barLegendLabels) {
			var height = barAssignees.length > 2 ? 60 * barAssignees.length
					: 180;
			$("#allocationBarDiv").height(height);
			var plot3 = $.jqplot('allocationBarDiv', barTaskCounts, {
				seriesColors : SERIES_COLORS,
				stackSeries : true,
				seriesDefaults : {
					renderer : $.jqplot.BarRenderer,
					rendererOptions : {
						barDirection : 'horizontal',
						highlightMouseDown : true,
						barMargin : 20,
					},
					pointLabels : {
						show : true,
						location : 'e',
						formatString : '%d',
						hideZeros : true
					},
				},
				axes : {
					yaxis : {
						renderer : $.jqplot.CategoryAxisRenderer,
						ticks : barAssignees
					},
					xaxis : {
						padMin : 1,
						formatString : '%d'
					}
				},
				legend : {
					renderer : jQuery.jqplot.EnhancedLegendRenderer,
					show : true,
					showSwatch : true,
					labels : barLegendLabels,
					// placement: 'outside',
					location : 'se'
				}
			});
		}

		reportService
				.getRptAllocationData($scope.searchCriteria.groupKey,
						$scope.searchCriteria.startDate,
						$scope.searchCriteria.endDate,
						$scope.searchCriteria.worksheetKeys,
						$scope.searchCriteria.assigneeKeys)
				.then(
						function(data) {
							$scope.allocationData = data;
							var results = [];
							var barAssignees = [], barTaskCounts = [], barLegendLabels = [];
							function _constructAssigneeBarData(j, assigneeData) {
								barAssignees.push(assigneeData.assigneeName);
								var i = 0;
								$
										.each(
												assigneeData.statusTaskCounts,
												function(key, value) {
													if (j == 0) {
														barLegendLabels
																.push($filter(
																		'translate')
																		(key)
																		+ $filter(
																				'translate')
																				(
																						'rept_label_quantity'));
														if (barTaskCounts.length < i + 1) {
															barTaskCounts
																	.push([]);
														}
													}
													barTaskCounts[i]
															.push(value);
													i += 1;
												});
							}

							for (var i = 0, len = data.details.length; i < len; i += 10) {
								results.push(data.details.slice(i, i + 10));
							}
							var j = 0;
							$
									.each(
											results,
											function(i, result) {
												var lineArray = [];
												var legendArray = [];
												for (var j = 0; j < result.length; j++) {
													var assigneeData = result[j];
													lineArray
															.push(assigneeData.plan);
													legendArray
															.push(assigneeData.assigneeName);
													_constructAssigneeBarData(
															j, assigneeData);
												}
												_generateAllocationLineChart(
														i + 1, lineArray,
														legendArray);
												j += 1;
											});

							_generateAllocationBarChart(barAssignees,
									barTaskCounts, barLegendLabels);

						});
	};

};

ReportController.$inject = [ '$scope', '$rootScope', '$filter', 'reportService' ];