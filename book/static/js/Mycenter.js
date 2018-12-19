$(document).ready(function () {
    var csrftoken =$("meta[name=csrf-token]").attr("content");
    $.ajaxSetup({
        headers: {"X-CSRFToken": csrftoken},
    });

    $('#editor').click(function () {
        $('#dis').css('display', 'block')
    });
    $('#save').click(function () {
        var text = $('textarea').val();
        {
            $.post('/book/introduce/',{texts:text},function (msg) {
                location.reload(true)
            })
        }

    });
    $('#cancel').click(function () {
        $('#dis').css('display', 'none')
    });

});
var  page = 1;
function test() {
    $.post('/book/center/', {page:page}, function (read) {
        if (read=='error') {
            alert('没有更多数据');
            $("#dispalys").css('display','none')
        }else { href="{% url 'book:show_article' foo2.id %}"
            var data = JSON.parse(read);
            for (i = 0; i < 1; i++) {
                $('<li class="list-group-item" style="padding: 0px">' +
                    '   <ul class="list-group">' +
                    '       <li class="list-group-item"><a style="font-size: 18px"  href="/book/show/'+data[i]["id"]+'">' + data[i]["title"] + '</a></li>' +
                    '       <li class="list-group-item"><p id="contents">' + data[i]["content"] + '</p></li>' +
                    '       <li class="list-group-item">' +
                    '           <span class="glyphicon glyphicon glyphicon-eye-open"' +
                    '              aria-hidden="true"></span> ' + data[i]["number"] + '&nbsp;' +
                    '           <span class="glyphicon glyphicon glyphicon-comment"\n' +
                    '              aria-hidden="true"></span> ' + data[i]["comment_number"] + '&nbsp;' +
                    '           <span class="glyphicon glyphicon glyphicon-heart"' +
                    '              aria-hidden="true"></span> ' + data[i]["collect_number"] + '' +
                    '           <span class="pull-right"> ' + data[i]["date"] + '</span>' +
                    '       </li>' +
                    '   </ul>' +
                    '</li>').appendTo($("#list_data"))
            }
           page = page+1;
        }
    });
}



