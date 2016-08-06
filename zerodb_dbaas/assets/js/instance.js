$(document).ready(function() {
	$("input[type='text']").keyup(function(){
		var inputValue = $.trim($(this).val());
		if (inputValue === "DELETE"){
			$('#deleteButton').removeAttr('disabled');
		} else {
			$('#deleteButton').attr('disabled', true);
		}
	});
});
