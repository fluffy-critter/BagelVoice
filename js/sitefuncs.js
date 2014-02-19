function pollForUpdates(firstTime) {
    var lastUpdate = firstTime + 0;
    var count = 0;
    var oldTitle = document.title;

    function pollUpdate() {
	$.ajax({
	    url: 'async.py?since=' + lastUpdate,
	    dataType: "json",
	    success: function(json) {
		count += json.threads.length;
		lastUpdate = json.lastitem;
		if (count) {
		    document.title = oldTitle + ' (' + count + ')';
		}
	    }
	});
    }

    // TODO incremental backoff (up to, say, 5 minutes if no message received)
    setInterval(pollUpdate, 5000);
}

