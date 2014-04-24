$("#filename").keypress(function (e) {
    if (e.which == 13) {
        e.preventDefault();
        downlodSubtitle()
        return false;
    }
});

$("#button").click(function () {
    downlodSubtitle()
});

function downlodSubtitle() {
    var fileName = $("#filename").val();
    var language = $("#language").val();
    if (!checkError()) {
        $("#result").html("<h1>Aguarde</h1><img src=\"http://newsbtc.com/wp-content/themes/allegro-theme/images/loading.gif\">");
        $.getJSON("/search?file_name=" + fileName + "&languages=" + language, function (data) {
            strName = data[0].file_name;
            strURL = data[0].url_file;
            $("#result").html("</br><a href=\"" + strURL + "\">Download " + strName);
        });
    }

    function checkError() {
        error = ""
        if (isEmpty(fileName)) {
            error = error + "- Insira o nome do arquivo \n";
        }

        if (isEmpty(error)) {
            return false;
        } else {
            alert(error);
            return true;
        }
    }

    function isEmpty(str) {
        return (!str || 0 === str.length);
    }
}

