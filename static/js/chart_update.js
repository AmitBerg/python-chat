let requestHandler = new RequestHandler("/statistics/api");
let select = $('select');
let wordCountColors = {
    luminosity: 'bright',
    format: 'rgba', // e.g. 'rgb(225,200,20)'
    alpha: 0.6
};
let messageCountColors = {
    luminosity: 'bright',
    format: 'rgba',
    alpha: 0.4
};


function updateCharts() {
    // Destroy last charts

    // word count
    $('#wordCount').remove();
    $('#word-count').append('<canvas id="wordCount" width="500" height="500"></canvas>');

    // message count
    $('#messageCount').remove();
    $('#message-count').append('<canvas id="messageCount" width="500" height="500"></canvas>');

    // get values of select
    let pks = select.multipleSelect("getSelects");
    let response = requestHandler.SendSync({"action": "get_log_data", "room_pks": '[' + pks + ']'});

    let wordCount = [];
    let words = [];
    let colorsWords = [];

    for (let word of response.data.words) {
        words.push(word[0]);
        wordCount.push(word[1]);
        colorsWords.push(randomColor(wordCountColors))
    }

    new Chart(document.getElementById("wordCount"), {
        type: "doughnut",
        data: {
            "labels": words,
            "datasets": [{
                "label": "My First Dataset",
                "data": wordCount,
                "backgroundColor": colorsWords,
                "borderColor": borders(colorsWords),
                "borderWidth": 1.5
            }]
        },

    });

    let users = [];
    let msgCount = [];
    let colorsUsers = [];

    for (const [key, value] of Object.entries(response.data.count)) {
        users.push(key);
        msgCount.push(value);
        colorsUsers.push(randomColor(messageCountColors))
    }

    new Chart(document.getElementById("messageCount"), {
        type: "bar",
        data: {
            "labels": users,
            "datasets": [{
                "label": "Number of messages",
                "data": msgCount,
                "backgroundColor": colorsUsers,
                "borderColor": borders(colorsUsers),
                "borderWidth": 1.5

            }]
        },

    });

}

function borders(colors) {
    let borders = [];
    for (let color of colors) {
        borders.push(color.replace(/[\d\.]+\)$/g, '1)'))
    }

    return borders
}

$(function () {

    // select shit
    select.multipleSelect({
        placeholder: "select Rooms",
        filter: true,
    });

    $('.ms-parent').css("width", "50%");

    select.multipleSelect("checkAll");
    updateCharts();

    select.change(function () {
        updateCharts()
    })
});