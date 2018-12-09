$(document).ready(function () {
    var quotes = [];
    var authors = [];

    function readJson() {
        return $.getJSON('quotes.json');
    }

    readJson().done(function (json) {
        $.each(json, function(key, value) {
            quotes[key] = {quotes: value.quotes};
        });
    });
       
    console.log("Ready! :D")

    $(function () {
        $("#quoteButton").click(function () {
            quoteNum = Math.random();
            $('#quote').html(quotes[0]);
            $('#author').html(authors[0]);
            console.log(quoteNum);
        });
    });
});