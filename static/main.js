// Note that the path doesn't matter right now; any WebSocket
// connection gets bumped over to WebSocket consumers
$(window).ready( function () {
    let socket = new WebSocket("ws://" + window.location.host + "/chat/?username=dan");
    let socket2 = new WebSocket("ws://" + window.location.host + "/chat/?username=amit");

    socket.onmessage = function(e) {
        $("#messages").append("<p>"+e.data+"</p>");
    };

    socket2.onmessage = function(e) {
        $("#messages").append("<p>"+e.data+"</p>");
    };

    socket.onopen = function() {
        socket.send("hello world 1");
    };

    socket2.onopen = function() {
        socket2.send("hello world 2");
    };

    // Call onopen directly if socket is already open
    if (socket.readyState === WebSocket.OPEN) socket.onopen();
    if (socket2.readyState === WebSocket.OPEN) socket2.onopen();
});
