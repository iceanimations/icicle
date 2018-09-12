function toggleDisplay(btn, jd, ed, code) {
	btn = document.getElementById(btn);
	jd = document.getElementById(jd);
	ed = document.getElementById(ed);
	code = document.getElementById(code);
	if (btn.checked == true) {
		jd.style = jd.style + ";display: block;";
		ed.style = ed.style + ";display: none;";
		code.style = code.style + ";display: block";
	}
	else {
		jd.style = jd.style + ";display: none;";
		ed.style = ed.style + ";display: block;";
		code.style = code.style + ";display: none";
	}
}
