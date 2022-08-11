$(document).ready(function() {
	let initEditor = function(id, mode="ltl") {
		return CodeMirror.fromTextArea(document.getElementById(id), {
			lineNumbers: true,
			lineWrapping: true,
			mode: mode,
			theme: "3024-day",
			matchBrackets: true,
			autoCloseBrackets: true,
			extraKeys: { "Tab": false, "Shift-Tab": false }
		});
	};
	let initLineEditor = function(id) {
		return CodeMirror.fromTextArea(document.getElementById(id), {
			mode: "ltl",
			theme: "3024-day",
			lineWrapping: true,
			extraKeys: { "Tab": false, "Shift-Tab": false }
		});
	};
	
	let assumptionsEditor = initEditor("assumptions_textarea");
	let guaranteesEditor = initEditor("guarantees_textarea");
	let inputsEditor = initLineEditor("inputs_textarea");
	let outputsEditor = initLineEditor("outputs_textarea");
	let tracesEditor = initEditor("traces_textarea", "traces");
	
	$("#refresh").click(function() {
		let url = $("#image").attr("src");
		$("#image").attr("src", url + `?v=${new Date().getTime()}`);
	});

	let make_formula = str => "((" + str.split(/\r|\n/).map(s => s.trim()).filter(s => s.length > 0).join(") & (") + "))";
	let make_propositions = str => str.split(/\r|\n/).map(s => s.trim()).join(',');
	let make_traces = str => str.split(/\r|\n/).map(s => s.trim().split(/\.|,|:|;/).join(".")).filter(s => s.length > 0).join('\n');
	
	$('#submit').click(function(){
		let data = {};
		let assumptions = assumptionsEditor.getValue().trim();
		let guarantees = guaranteesEditor.getValue().trim();
		if (!guarantees) {
			$("#image-container").text("Guarantees not specified");
			return;
		}

		formula = "";
		if (assumptions) {
			formula += make_formula(assumptions);
			formula += " -> ";
		}
		formula += make_formula(guarantees);

		data['formula'] = formula.trim();

		let inputs = inputsEditor.getValue().trim();
		let outputs = outputsEditor.getValue().trim();
		if (!inputs && !outputs) {
			$("#image-container").text("No input or output symbols specified")
			return;
		}
		inputs = make_propositions(inputs);
		outputs = make_propositions(outputs);

		data['inputs'] = inputs;
		data['outputs'] = outputs;

		let traces = tracesEditor.getValue().trim();
		data['traces'] = make_traces(traces);		
		
		$.ajax({
			type: 'POST',
			url: '/',
			data: data,
			dataType: 'json'
		}).done(function(data) {
			console.log("Response Data" + data); // Log the server response to console
			$("#refresh").click();
		});
	});
});