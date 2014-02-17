function pollForUpdates(infoPath, firstTime) {
    var lastUpdate = firstTime + 0;
    var count = 0;
    var oldTitle = document.title;

    function pollUpdate() {
	$.ajax({
	    url: infoPath + '?since=' + lastUpdate,
	    dataType: "json",
	    success: function(json) {
		count += json.updatedThreads.length;
		lastUpdate = json.lastitem;
		if (count) {
		    document.title = oldTitle + ' (' + count + ')';
		}
	    }
	});
    }

    setInterval(pollUpdate, 5000);
}

	