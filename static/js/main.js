$(function () {
        // Correctly decide between ws:// and wss://
        let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
        let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
        console.log("Connecting to " + ws_path);
        let socket = new ReconnectingWebSocket(ws_path);

        let user = $("#username").html();

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
                let me = user === data.username;
                let messageClass;
                let dotClass;
                let alignClass;
                let floatClass;

                if (data.username === "Brobot") {
                    messageClass = "bot-message";
                    dotClass = "bot";
                    alignClass = "align-right";
                    floatClass = "float-right";
                }
                else {
                    messageClass = me ? "my-message" : "other-message";
                    dotClass = me ? "me" : "other";
                    alignClass = me ? "align-left" : "align-right";
                    floatClass = me ? "float-left" : "float-right";
                }
                // msg types are defined in chat/settings.py
                // Only for demo purposes is hardcoded, in production scenarios, consider call a service.

                // TODO add clickable links
                let words = data.message.split(" ");
                let newWords = [];
                for (let word of words) {
                    if (word.startsWith("http://") || word.startsWith("https://")) {
                        word = '<a target="_blank" style="position: relative; z-index: 10;" href="'
                            + htmlEntities(word) + '">' + htmlEntities(word) + '</a>';
                        newWords.push(word)

                    }
                    else if (word.includes(".")) {
                        word = '<a target="_blank" style="position: relative; z-index: 10;" href="http://'
                            + htmlEntities(word) + '">' + htmlEntities(word) + '</a>';
                        newWords.push(word)
                    }
                    else
                        newWords.push(htmlEntities(word))
                }

                let newMessage = newWords.join(" ");

                switch (data.msg_type) {
                    case 0:
                        ok_msg = '<li class="clearfix"><div class="message-data ' + alignClass + '">' +
                            '<span class="message-data-time">' + new Date().toLocaleTimeString() +
                            '</span> &nbsp; &nbsp; <span class="message-data-name">' + data.username +
                            '&nbsp;</span><i class="fa fa-circle ' + dotClass + '"></i>'
                            + '</div><div class="message ' + messageClass + ' ' + floatClass + "" +
                            '" style="word-wrap: break-word">' + newMessage + '</div></li>';
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
                if (data.username === "Brobot") {
                    if (!$(".loading").length) {
                        msgdiv.append('<div class="loading">' +
                            '<div class="loading__dots">' +
                            '<div class="loading__dots__dot"></div>' +
                            '<div class="loading__dots__dot"></div>' +
                            '<div class="loading__dots__dot"></div>' +
                            '</div><div class="loading__msg">Hold tight, Brobot is typing</div></div>');
                    }
                    setTimeout(function () {
                        msgdiv.append(ok_msg);
                        $(".loading").remove()
                    }, 3000);
                }
                else {
                    msgdiv.append(ok_msg);
                }
                // msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
                scrollDown();
            } else {
                console.log("Cannot handle message!");
            }

            $(window).unload(function () {
                console.log("mmeeeeeeeeeee");
                socket.send(JSON.stringify({
                    "command": "leave",
                    "room": getRoomID()
                }));
            })


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

        function leaveRoom() {
            socket.send(JSON.stringify({
                    "command": "leave",  // determines which handler will be used (see chat/routing.py)
                    "room": getRoomID()
                }));
        }

        window.onbeforeunload = function () {
            leaveRoom()
        };

        // not needed in the future
        // Room join/leave
        // left here for me to remember how to use leave/join

        // $("li.room-link").click(function () {
        //     roomId = $(this).attr("data-room-id");
        //     if (inRoom(roomId)) {
        //         // Leave room
        //         $(this).removeClass("joined");
        //         socket.send(JSON.stringify({
        //             "command": "leave",  // determines which handler will be used (see chat/routing.py)
        //             "room": roomId
        //         }));
        //     } else {
        //         // Join room
        //         $(this).addClass("joined");
        //         socket.send(JSON.stringify({
        //             "command": "join",
        //             "room": roomId
        //         }));
        //     }
        // });

        // Bind Enter key to send button
        $(document).keypress(function (e) {
            if (e.which === 13) {
                $("#send-btn").click();
            }
        });

    }
);