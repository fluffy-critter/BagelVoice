function pollForUpdates(infoPath, firstTime) {
    var lastUpdate = firstTime + 0;
    var count = 0;
    var oldTitle = document.title;

    function pollUpdate() {
	$.ajax({
	    url: infoPath,
	    dataType: "json",
	    success: function(json) {
		if (json.lastitem > lastUpdate) {
		    ++count;
		    lastUpdate = json.lastitem;
		    document.title = oldTitle + '(' + count + ')';
		}
	    }
	});
    }

    setInterval(pollUpdate, 5000);
}

	