$(function () {
    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    let socket = new ReconnectingWebSocket(ws_path);
});