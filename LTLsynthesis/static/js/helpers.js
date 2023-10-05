$(document).ready(function() {
	$('.alert').alert()
	let count = 0;
	let exampleReference = {};
	let variable_set = {};
	fetch('/static/js/examples.json')
    .then((response) => response.json())
    .then((json) => exampleReference = json);

	let formatFormData = function(data) {
		let assumptions = assumptionsEditor.getValue().trim();
		let guarantees = guaranteesEditor.getValue().trim();
		if (!guarantees) {
			$("#image-container").text("Guarantees not specified");
			return null;
		}

		let k = parseInt(data.get('kvalue'));
		k = k > 0? k : 1;

		formula = "";
		if (assumptions) {
			formula += make_formula(assumptions);
			formula += " -> ";
		}
		formula += make_formula(guarantees);

		data.append('formula', formula.trim());

		let inputs = inputsEditor.getValue().trim();
		let outputs = outputsEditor.getValue().trim();
		if (!inputs && !outputs) {
			addAlert("No input or output symbols specified");
			return null;
		}
		inputs = make_propositions(inputs);
		outputs = make_propositions(outputs);

		data.set('inputs', inputs);
		data.set('outputs', outputs);
		data.set('k', k);

		let traces = tracesEditor.getValue().trim();
		if(traces.length > 0)
			data.set('traces', make_traces(traces));

		return data;
	};
	
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
	
	let process_variable = str => {
		str = str.split('=').map(s => s.trim());
		variable_set[str[0]] = str[1];
		return '';
	}
	let make_formula = str => "((" + str.split(/\r|\n/).map(s => 
		s.trim()).filter(s => s.length > 0).join(") & (") + "))";
	let make_propositions = str => str.split(/\r|\n|,| /).filter(s => 
		s.length > 0).map(s => s.trim()).join(',');
	let make_traces = str => str.split(/\r|\n/).map(s => 
		s.includes('=')? process_variable(s):s.trim().split(
			/\.|,|:|;|\#/).map(t => t in variable_set? variable_set[t]:
			t).join(".")).filter(s => s.length > 0).join('\n');

	let setData =  function (exampleName) {
		assumptionsEditor.setValue(exampleReference[exampleName][
			'assumptions'].join('\n'));
		guaranteesEditor.setValue(exampleReference[exampleName][
			'guarantees'].join('\n'));
		inputsEditor.setValue(exampleReference[exampleName]['inputs']);
		outputsEditor.setValue(exampleReference[exampleName]['outputs']);
		tracesEditor.setValue(exampleReference[exampleName][
			'traces'].join('\n'));
	};

	let addAlert = function(message, isError) {
		$('<div>', {class: 'alert alert-dismissible d-flex \
			align-items-center ' + (isError? 'alert-danger':
				'alert-warning'), role: 'alert'}).appendTo('form').html(
			"<i class=\"bi bi-exclamation-triangle-fill\"></i> &nbsp;"
			+ message + "<button type=\"button\" class=\"btn-close\" \
			data-bs-dismiss=\"alert\" aria-label=\"Close\"></button>");
		$('.alert').alert();
	}

	let beforeQuery = function(data) {
		document.getElementById('img').html = "";
		let showTarget = data.get('target') != null? data.get(
			'target').size > 0 : false;
		$('.downloader').addClass('visually-hidden');
		$('.submit-text').addClass('visually-hidden');
		$('.loading').removeClass('visually-hidden');
		$('ul.list-group').addClass('visually-hidden').html("");
		return showTarget;
	};

	let afterQuery = function(showTarget) {
		$('.submit-text').html("Submit");
		$('.downloader').removeClass('visually-hidden');
		$('.submit-text').removeClass('visually-hidden');
		$('.loading').addClass('visually-hidden');
		if (!showTarget) {
			$('.downloader.target').addClass('visually-hidden');
		}
	}
	
	$('#submit').click(function(){
		
		let data = new FormData($('#acacia-form')[0]);
		data = formatFormData(data);
		if (data == null) return;
		let showTarget = beforeQuery(data);
		
		$.ajax({
			type: 'POST',
			url: '/',
			enctype: 'multipart/form-data',
			processData: false,
			contentType: false,
			cache: false,
			data: data, 
			success: function(success) {
				afterQuery(showTarget);
				document.getElementById('img').src = 
					"/static/temp_model_files/LearnedModel_"+ success.query_number + 
					".svg?count=" + count;
				if (success.realizable) {
					$('#realizability').html("REALIZABLE:" + success.message);
				}
			},
			error: function(error) {
				data = error.responseJSON;
				afterQuery(showTarget);
				document.getElementById('img').src = "";
				addAlert(data.message, !data.retry);
				if (!data.realizable) {
					$('#realizability').html("UNREALIZABLE");
				} else {
					$('#realizability').html("REALIZABLE");
				}
				$('#message').html(data.message);
			}
		});
	});

	$('#submitstrix').click(function(){
		
		let data = new FormData($('#strix-form')[0]);
		data = formatFormData(data);
		if (data == null) return;
		showTarget = beforeQuery(data);
		
		$.ajax({
			type: 'POST',
			url: '/strix',
			enctype: 'multipart/form-data',
			processData: false,
			contentType: false,
			cache: false,
			data: data, 
			success: function(data) {
				count += 1;
				afterQuery(showTarget);
				document.getElementById('img').src = "/static/temp_\
				model_files/" + data.svg + "?count=" + count;
				$('.figure-caption').html(data.msg);
			}
		});
	});

	$('#SimpleArbiter2').click(() => {setData('SimpleArbiter2')});
	$('#SimpleArbiter3').click(() => {setData('SimpleArbiter3')});
	$('#LiftFloor2').click(() => {setData('LiftFloor2')});
	$('#TowerCranes2').click(() => {setData('TowerCranes2')});
	$('#TowerCranes3').click(() => {setData('TowerCranes3')});
	$('#CraneController2').click(() => {setData('CraneController2')});
});
