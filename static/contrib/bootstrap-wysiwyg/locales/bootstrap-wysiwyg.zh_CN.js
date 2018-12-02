(function($) {
	if ($.fn.wysiwyg.locales == undefined) {
		$.fn.wysiwyg.locales = {};
	}
	$.fn.wysiwyg.locales['zh_CN'] = {
		"fontfamily" : "字体",
		"fontsize" : "字号",
		"bold" : "粗体",
		"italic" : "斜体",
		"strikethrough" : "删除线",
		"underline" : "下划线",
		"insertunorderlist" : "项目符号",
		"insertorderedlist" : "编号列表",
		"outdent" : "减少缩进",
		"indent" : "增加缩进",
		"justifyleft" : "左对齐",
		"justifycenter" : "居中",
		"justifyright" : "右对齐",
		"justifyfull" : "两端对齐",
		"undo" : "撤消",
		"redo" : "重做",
		"clearformat" : "清除格式",
		"fontsizes" : {
			1 : "小",
			3 : "中",
			5 : "大"
		},

		"fontfamilies" : {
			"Simsun" : "宋体",
			"NSimSun" : "新宋体",
			"KaiTi_GB2312" : "楷体",
			"SimHei" : "黑体",
			"Microsoft YaHei" : "微软雅黑",
			"Arial" : "arial,helvetica,sans-serif",
			"Arial Black" : "arial black,avant garde",
			"Courier New" : "courier new,courier",
			"Tahoma" : "tahoma,arial,helvetica,sans-serif",
			"Times New Roman" : "times new roman,times",
			"Verdana" : "verdana,geneva"
		}
	};
}(jQuery));
