function selectAll(source) {
  checkboxes = document.getElementsByName('leaves');
  for(var i=0, n=checkboxes.length;i<n;i++) {
	  if (checkboxes[i].dataset.employeeid == source.dataset.employeeid) {
	  	checkboxes[i].checked = source.checked;
  	}
  }
}
