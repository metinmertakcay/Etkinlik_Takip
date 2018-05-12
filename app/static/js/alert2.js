function clickButton() {
    var eden_k_id = document.getElementById('eden_k_id').value
    var metin = document.getElementById('metin').value

    if ((eden_k_id == "") || (metin == "") ) {
    }
    else{
        alert("Şikayetiniz başarıyla iletilmiştir.");
    }
}

function clickButton2() {
    var name = document.getElementById('name').value
    var message = document.getElementById('message').value

    if ((name == "") || (message == "") ) {
    }
    else{
        alert("Yorumunuz başarıyla eklenmiştir.");
    }
}