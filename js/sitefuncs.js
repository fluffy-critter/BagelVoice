function pollForUpdates() {
    var lastUpdate;
    var count = 0;
    var oldTitle = document.title;
    var retry = 5000;

    statusBox = $("#status");

    function updateEvent(tbox, obj) {
	ebox = tbox.children('#event-' + obj.eid);
	if (ebox.length) {
	    console.log("Replacing event " + obj.eid);
	    ebox.replaceWith(obj.html);
	    return true;
	}
    }

    function updateThread(obj) {
	tbox = $("#thread-" + obj.tid);
	if (tbox.length) {
	    tbox.addClass('unread');
	    var prepend = '';
	    for (var i = 0; i < obj.events.length; i++) {
		eobj = obj.events[i];
		if (!updateEvent(tbox, eobj)) {
		    console.log("Prepending event " + eobj.eid);
		    prepend += eobj.html;
		}
	    }
	    if (prepend) {
		tbox.children('.events').prepend(prepend);
	    }
	} else {
	    inbox = $("#inbox");
	    if (inbox.length) {
		$.ajax({
		    url: 'render.py/t/' + obj.tid,
		    dataType: 'html',
		    success: function(html) {
			inbox.prepend(html);
		    }
		});
	    }
	}
    }

    // of course moving to WebSockets makes this entire thing pointless
    function pollUpdate() {
	$.ajax({
	    url: 'async.py' + (lastUpdate ? '?since=' + lastUpdate : ''),
	    dataType: "json",
	    success: function(json) {
		if (statusBox) {
		    statusBox.removeClass('error');
		    statusBox.html('');
		}

		if (json.threads) {
		    console.log("notified of " + json.threads.length + " threads");
		    count += json.threads.length;

		    for (var i = 0; i < json.threads.length; i++) {
			var thread = json.threads[i];
			updateThread(thread);
		    }
		}
		// exponential backoff
		if (json.threads && json.threads.length) {
		    console.log("resetting timer");
		    retry = 1000;
		} else {
		    console.log("backing off");
		    retry = Math.min(60000, retry*1.5);
		}
		console.log("next update check = " + retry);
		
		if (lastUpdate && count) {
		    document.title = oldTitle + ' (' + count + ')';
		}
		lastUpdate = json.lastitem;
		setTimeout(pollUpdate, retry);
	    },
	    error: function(jq, st, th) {
		setTimeout(pollUpdate, 20000);
		errstr = st + ": " + th;
		console.warn("Got error " + errstr);
		if (statusBox) {
		    statusBox.addClass('error');
		    statusBox.html('<div>' + errstr + '</div>');
		}
	    }
	});
    }

    setTimeout(pollUpdate, retry);
}

function markUnread(target) {
    
}

$(document).ready(pollForUpdates)