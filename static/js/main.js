$(function () {
    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    let socket = new ReconnectingWebSocket(ws_path);

    // Helpful debugging
    socket.onopen = function () {
        console.log("Connected to chat socket");
        // as rooms loads
        let roomID = getRoomID();
        if (!isNaN(roomID)) {
            socket.send(JSON.stringify({
                "command": "join",
                "room": getRoomID()
            }));
        }

    };

    socket.onclose = function () {
        console.log("Disconnected from chat socket");
    };

    socket.onmessage = function (message) {
        // Decode the JSON
        console.log("Got websocket message " + message.data);
        let data = JSON.parse(message.data);
        // Handle errors
        if (data.error) {
            alert(data.error);
            return;
        }
        // Handle joining
        if (data.join) {
            console.log("Joining room " + data.join);
            console.log(message.data);
            let input = $("#message-input");
            $("#send-btn").click(function () {
                    // only send if there is something in the input
                    if (input.val()) {
                        socket.send(JSON.stringify({
                            "command": "send",
                            "room": data.join,
                            "message": input.val()
                        }));
                        input.val("");
                    }
                }
            );
            // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
            $("#room-" + data.leave).remove();
        } else if (data.message || data.msg_type != 0) {
            let msgdiv = $(".chat-history ul");
            let ok_msg = "";
            // msg types are defined in chat/settings.py
            // Only for demo purposes is hardcoded, in production scenarios, consider call a service.
            switch (data.msg_type) {
                case 0:
                    ok_msg = '<li class="clearfix"><div class="message-data align-right">' +
                        '<span class="message-data-time">' + new Date().toLocaleTimeString() +
                        '</span> &nbsp; &nbsp; <span class="message-data-name">' + data.username +
                        '&nbsp;</span><i class="fa fa-circle me"></i>'
                        + '</div><div class="message other-message float-right">'
                        + htmlEntities(data.message) + '</div></li>';
                    break;
                case 1:
                    // Warning/Advice messages
                    ok_msg = "<div class='contextual-message text-warning'>" + data.message + "</div>";
                    break;
                case 2:
                    // Alert/Danger messages
                    ok_msg = "<div class='contextual-message text-danger'>" + data.message + "</div>";
                    break;
                case 3:
                    // "Muted" messages
                    ok_msg = "<div class='contextual-message text-muted'>" + data.message + "</div>";
                    break;
                case 4:
                    // User joined room
                    ok_msg = "<div class='contextual-message text-muted'>" + data.username + " joined the room!" + "</div>";
                    break;
                case 5:
                    // User left room
                    ok_msg = "<div class='contextual-message text-muted'>" + data.username + " left the room!" + "</div>";
                    break;
                default:
                    console.log("Unsupported message type!");
                    return;
            }
            msgdiv.append(ok_msg);
            // msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
            scrollDown();
        } else {
            console.log("Cannot handle message!");
        }
    };

    // Says if we joined a room or not by if there's a div for it
    function inRoom(roomId) {
        return $("#room-" + roomId).length > 0;
    }

    // get room id from url, might need to be changed
    function getRoomID() {
        return window.location.pathname.slice(-1);
    }

    // Im here to prevent XSS
    function htmlEntities(str) {
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // Scroll down to the bottom of the page.
    // why is it called scrollTop though?
    function scrollDown() {
        $(document).scrollTop($(document).height());
    }

    // not needed in the future
    // Room join/leave
    // left here for me to remember how to use leave/join
    $("li.room-link").click(function () {
        roomId = $(this).attr("data-room-id");
        if (inRoom(roomId)) {
            // Leave room
            $(this).removeClass("joined");
            socket.send(JSON.stringify({
                "command": "leave",  // determines which handler will be used (see chat/routing.py)
                "room": roomId
            }));
        } else {
            // Join room
            $(this).addClass("joined");
            socket.send(JSON.stringify({
                "command": "join",
                "room": roomId
            }));
        }
    });

    // Bind Enter key to send button
    $(document).keypress(function (e) {
        if (e.which === 13) {
            $("#send-btn").click();
        }
    });

});