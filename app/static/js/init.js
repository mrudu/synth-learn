var init = (function () {
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

	let init = function () {
		let assumptionsEditor = initEditor("assumptions_textarea");
		let guaranteesEditor = initEditor("guarantees_textarea");
		let inputsEditor = initLineEditor("inputs_textarea");
		let outputsEditor = initLineEditor("outputs_textarea");
		let tracesEditor = initEditor("traces_textarea", "traces");
	}

})();