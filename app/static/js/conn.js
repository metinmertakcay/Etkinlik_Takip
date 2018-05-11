function clickButton() {
    var name = document.getElementById('name').value
    var email = document.getElementById('email').value
    var phone = document.getElementById('phone').value
    var message = document.getElementById('message').value

    if ((name == "") || (email == "") || (phone == "") || (message == "")) {
        alert("İşlem gerçekleştirilemedi.");
    }
    else{
        alert("İşleminiz başarıyla gerçekleştirilmiştir.");
    }
}