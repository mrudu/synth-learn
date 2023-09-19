$(document).ready(function() {
	$('.alert').alert()
	let count=0
	let exampleReference = {
		'SimpleArbiter2': {
			'assumptions': [],
			'guarantees': ['G (p -> F (gp))', 'G (q -> F (gq))', 'G (!gp | !gq)'],
			'inputs': 'p, q',
			'outputs': 'gp, gq',
			'traces': ['p & q.gp & !gq']
		},
		'SimpleArbiter3': {
			'assumptions': [],
			'guarantees': 
				['G (p -> F (gp))',
				'G (r -> F (gr))',
				'G (q -> F (gq))',
				'G (!(gp & gq) & !(gp & gr) & !(gr & gq))'],
			'inputs': 'p, q, r',
			'outputs': 'gp, gq, gr',
			'traces': ['p & q & r.gp & !gq & !gr']
		},
		'LiftFloor3': {
			'assumptions': [
				'G(b0 -> (b0 W (f0 & serve)))',
				'G(b1 -> (b1 W (f1 & serve)))'],
			'guarantees' :
				['G (b0 -> F (f0 & serve))',
				'G (b1 -> F (f1 & serve))',
				'G ((f0 & !f1) | (!f0 & f1))',
				'G ((f0 & serve) -> X (!f1))',
				'G ((f1 & serve) -> X (!f0))',
				'f0'],
			'inputs': 'b0, b1',
			'outputs': 'f0, f1, serve',
			'traces': [
				'!b0 & b1.f0 & !f1 & !serve.!b0 & b1.!f0 & f1 & serve.!b0 & !b1.!f0 & f1 & !serve.!b0 & !b1.!f0 & f1 & !serve',
				'!b0 & !b1.f0 & !f1 & !serve.!b0 & !b1.f0 & !f1 & !serve']
		},
		'PrioritizedArbiter': {
			'assumptions': ['G F !m'],
			'guarantees' : ['G (p1 -> F (g1))',
				'G (p2 -> F (g2))',
				'G (m -> gm)',
				'G (g1 -> (!g2 & !gm))',
				'G (g2 -> (!g1 & !gm))',
				'G (gm -> (!g1 & !g2))'],
			'inputs': 'p1, p2, m',
			'outputs': 'g1, g2, gm',
			'traces': ["!m & !p1 & !p2.!g1 & !g2 & !gm",
				"m & p1 & p2.!g1 & !g2 & gm.!m & !p1 & !p2.g1 & !g2 & !gm",
				"!m & p1 & p2.g1 & !g2 & !gm.!m & !p1 & !p2.!g1 & g2 & !gm",
				"!m & p1 & !p2.g1 & !g2 & !gm.!m & !p1 & !p2.!g1 & !g2 & !gm",
				"m & !p1 & p2.!g1 & !g2 & gm.!m & !p1.!g1 & g2 & !gm.!m & !p1 & !p2.!g1 & !g2 & !gm",
				"m & p1 & !p2.!g1 & !g2 & gm.!m & p2.g1 & !g2 & !gm.!m & !p1 & !p2.!g1 & g2 & !gm",
				"m & !p1 & p2.!g1 & !g2 & gm.!m & !p1 & p2.!g1 & g2 & !gm.!m & !p1 & !p2.!g1 & !g2 & !gm",
				"m & p1 & !p2.!g1 & !g2 & gm.!m & p1 & !p2.g1 & !g2 & !gm.!m & !p1 & !p2.!g1 & !g2 & !gm"]
		},
		'TowerCranes2': {
			'assumptions': [
				'G(r1 -> (r1 W g1))',
				'G(r2 -> (r2 W g2))',
				'G(g1 -> F (l1))',
				'G(g2 -> F (l2))',
				'G (!(r1 & l1))',
				'G (!(r2 & l2))'],
			'guarantees' : [
				'G (r1 -> F (g1))',
				'G (r2 -> F (g2))',
				'G (g1 -> (g1 U X(l1)))',
				'G (g2 -> (g2 U X(l2)))',
				'G (!(g1 & g2))'],
			'inputs': 'r1, r2, l1, l2',
			'outputs': 'g1, g2',
			'traces': ['!r1 & r2.!g1 & g2',
				'!r1 & !r2.!g1 & !g2',
				'r1 & !r2.g1 & !g2']
		},
		'TowerCranes3': {
			'assumptions': [
				'G(r11 -> (r11 W g11))',
				'G(r12 -> (r12 W g12))',
				'G(r22 -> (r22 W g22))',
				'G(r23 -> (r23 W g23))',
				'G(g11 -> F (l11))',
				'G(g12 -> F (l12))',
				'G(g22 -> F (l22))',
				'G(g23 -> F (l23))'],
			'guarantees' : [
				'G (r11 -> F (g11))',
				'G (r12 -> F (g12))',
				'G (r22 -> F (g22))',
				'G (r23 -> F (g23))',
				'G (g11 -> (g11 U X(l11)))',
				'G (g12 -> (g12 U X(l12)))',
				'G (g22 -> (g22 U X(l22)))',
				'G (g23 -> (g23 U X(l23)))',
				'G (!(g11 & g12))',
				'G (!(g22 & g23))'],
			'inputs': 'r11, r12, r22, r23, l11, l12, l22, l23',
			'outputs': 'g11, g12, g22, g23',
			'traces': [""]
		},
		'CraneController2': {
			'assumptions': [
				'G (!(g1 & g2))',
				'G (g1 -> (g1 W X(l1)))',
				'G (g2 -> (g2 W X(l2)))',
				'G ((x11 & !x12) -> F(!r1))',
				'G ((!x21 & !x22) -> F(!r2))',
				'G(r1 -> (r1 W g1))',
				'G(r2 -> (r2 W g2))',
				'G (r1 -> F (g1))',
				'G (r2 -> F (g2))',
				'G (rhoistUP1 -> F(hoistUP1))',
				'G (rhoistUP2 -> F(hoistUP2))'],
			'guarantees' : [
				// No release when request
				'G (r1 -> !l1)',
				'G (r2 -> !l2)',
				// Transition Requirements for Crane 1
				'G (!(x11 xor x12) -> !(x11 xor X(x11)))',
				'G ((x11 xor x12) -> !((x11 xor X(x11)) & !(x12 xor X(x12))))',
				// Transition Requirements for Crane 2
				'G (!(x21 xor x22) -> !(x21 xor X(x21)))',
				'G ((x21 xor x22) -> !((x21 xor X(x21)) & !(x22 xor X(x22))))',
				// Critical implies grant
				'G ((x11 & !x12) -> g1)',
				'G ((!x21 & !x22) -> g2)',
				// Grant implies release
				'G (g1 -> F X(l1))',
				'G (g2 -> F X(l2))',
				// Move out of critical implies release
				'G (((x11 & !x12) & X !(x11 & !x12)) <-> X(l1))',
				'G (((!x21 & !x22) & X !(!x21 & !x22)) <-> X(l2))',
				// Move position requires hoistUp
				'G (!hoistUP1 -> !(x11 xor X(x11)))',
				'G (!hoistUP1 -> !(x12 xor X(x12)))',
				'G (!hoistUP2 -> !(x22 xor X(x22)))',
				'G (!hoistUP2 -> !(x23 xor X(x23)))',
				],
			'inputs': 'g1, g2, r1, r2, hoistUP1, hoistUP2',
			'outputs': 'l1, l2, x11, x12, x21, x22, rhoistUP1, rhoistUP2',
			'traces': [""]
		}
	}

	let variable_set = {}
	
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
	let make_formula = str => "((" + str.split(/\r|\n/).map(s => s.trim()).filter(s => s.length > 0).join(") & (") + "))";
	let make_propositions = str => str.split(/\r|\n|,| /).filter(s => s.length > 0).map(s => s.trim()).join(',');
	let make_traces = str => str.split(/\r|\n/).map(
		s => s.includes('=')? 
		process_variable(s):
		s.trim().split(/\.|,|:|;|\#/).map(t => t in variable_set? variable_set[t]: t).join(".")).filter(
		s => s.length > 0).join('\n');

	let setData =  function (exampleName) {
		assumptionsEditor.setValue(exampleReference[exampleName]['assumptions'].join('\n'));
		guaranteesEditor.setValue(exampleReference[exampleName]['guarantees'].join('\n'));
		inputsEditor.setValue(exampleReference[exampleName]['inputs']);
		outputsEditor.setValue(exampleReference[exampleName]['outputs']);
		tracesEditor.setValue(exampleReference[exampleName]['traces'].join('\n'));
	};

	let addAlert = function(message, isError) {
		$('<div>', {
			class: 'alert alert-dismissible d-flex align-items-center ' + (isError?'alert-danger':'alert-warning'),
			role: 'alert'
		}).appendTo('form').html(
		"<i class=\"bi bi-exclamation-triangle-fill\"></i> &nbsp;"
		+ message
		+ "<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Close\"></button>");
		$('.alert').alert();
	}
	
	$('#submit').click(function(){
		$('.downloader').addClass('visually-hidden');
		$('.submit-text').addClass('visually-hidden');
		$('ul.list-group').addClass('visually-hidden').html("");
		$('.loading').removeClass('visually-hidden');
		
		let data = new FormData($('#acacia-form')[0]);

		let showTarget = data.get('target').size > 0;
		
		let assumptions = assumptionsEditor.getValue().trim();
		let guarantees = guaranteesEditor.getValue().trim();
		if (!guarantees) {
			$("#image-container").text("Guarantees not specified");
			return;
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
			return;
		}
		inputs = make_propositions(inputs);
		outputs = make_propositions(outputs);

		data.set('inputs', inputs);
		data.set('outputs', outputs);
		data.set('k', k);

		let traces = tracesEditor.getValue().trim();
		data.set('traces', make_traces(traces));	
		
		$.ajax({
			type: 'POST',
			url: '/',
			enctype: 'multipart/form-data',
			processData: false,
			contentType: false,
			cache: false,
			data: data, 
			success: function(data) {
				$('.submit-text').html("Submit");
				$('.downloader').removeClass('visually-hidden');
				$('.submit-text').removeClass('visually-hidden');
				$('.loading').addClass('visually-hidden');
				if (!showTarget) {
					$('.downloader.target').addClass('visually-hidden');
				}
				document.querySelector('svg').innerHTML = data.img;
				document.getElementById('img').src = "/static/temp_model_files/LearnedModel_"+ data.query_number + ".svg?count=" + count;
				$('.figure-caption').html("");
				let ul = $('ul.list-group');
				ul.removeClass('visually-hidden');
				data.traces.forEach((item) => {
					ul.append(`<li class="list-group-item">${item.join('.')}</li>`);
				});
			},
			error: function(error) {
				data = error.responseJSON
				$('.downloader').removeClass('visually-hidden');
				$('.submit-text').removeClass('visually-hidden');
				$('.loading').addClass('visually-hidden');
				if (!showTarget) {
					$('.downloader.target').addClass('visually-hidden');
				}
				addAlert(data.msg, !data.retry);
				if (data.retry) {
					$('.submit-text').html("Retry?");
					$('input[name="kvalue"').val(data.k + 1);
				}
			}
		});
	});

	$('#submitstrix').click(function(){
		document.getElementById('img').src = "";
		$('.downloader').addClass('visually-hidden');
		$('.submit-text').addClass('visually-hidden');
		$('ul.list-group').addClass('visually-hidden').html("");
		$('.loading').removeClass('visually-hidden');
		
		let data = new FormData($('#strix-form')[0]);
		
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

		data.append('formula', formula.trim());

		let inputs = inputsEditor.getValue().trim();
		let outputs = outputsEditor.getValue().trim();
		if (!inputs && !outputs) {
			$("#image-container").text("No input or output symbols specified")
			return;
		}
		inputs = make_propositions(inputs);
		outputs = make_propositions(outputs);

		data.set('inputs', inputs);
		data.set('outputs', outputs);	
		
		$.ajax({
			type: 'POST',
			url: '/strix',
			enctype: 'multipart/form-data',
			processData: false,
			contentType: false,
			cache: false,
			data: data, 
			success: function(data) {
				count += 1
				$('.downloader').removeClass('visually-hidden');
				$('.submit-text').removeClass('visually-hidden');
				$('.loading').addClass('visually-hidden');
				document.getElementById('img').src = "/static/temp_model_files/" + data.svg + "?count=" + count;
				$('.figure-caption').html(data.msg);
			}
		});
	});

	$('#SimpleArbiter2').click(() => {setData('SimpleArbiter2')});
	$('#SimpleArbiter3').click(() => {setData('SimpleArbiter3')});
	$('#LiftFloor3').click(() => {setData('LiftFloor3')});
	$('#TowerCranes2').click(() => {setData('TowerCranes2')});
	$('#TowerCranes3').click(() => {setData('TowerCranes3')});
	$('#CraneController2').click(() => {setData('CraneController2')});
});