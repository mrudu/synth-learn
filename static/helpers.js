$(document).ready(function() {
	var input_propositions = [];
	var output_propositions = [];
	
	$("#refresh").click(function() {
		var url = $("#image").attr("src");
		$("#image").attr("src", url + `?v=${new Date().getTime()}`);
	});
	$('#input_atomic_propositions').keyup(function() {
		input_propositions = $(this).val().split(' ');
		const index = input_propositions.indexOf('');
		if (index > -1) {
	  		input_propositions.splice(index, 1); // 2nd parameter means remove one item only
		}
		if (input_propositions.length > 0)
			$('#input-propositions-trace').html(
				'<button type="button" class="btn btn-disabled" style="margin: 0 1rem;">Input Propositions:</button>');
		else
			$('#input-propositions-trace').html('');
		for (let i = 0; i < input_propositions.length; i++) {
			$('#input-propositions-trace').append(
				'<button type="button" class="btn btn-success" style="margin: 0 0.5rem;">' + input_propositions[i] + '</button>');
		};
	});
	$('#output_atomic_propositions').keyup(function() {
		output_propositions = $(this).val().split(' ');
		const index = output_propositions.indexOf('');
		if (index > -1) {
	  		output_propositions.splice(index, 1); // 2nd parameter means remove one item only
		}
		if (output_propositions.length > 0)
			$('#output-propositions-trace').html(
				'<button type="button" class="btn btn-disabled" style="margin: 0 1rem;">Output Propositions</button>');
		else
			$('#output-propositions-trace').html('');
		for (let i = 0; i < output_propositions.length; i++) {
			$('#output-propositions-trace').append(
				'<button type="button" class="btn btn-warning" style="margin: 0 0.5rem;">' + output_propositions[i] + '</button>');
		};
	});
});