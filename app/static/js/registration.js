var expanded = false;
function showCheckboxes(){
  var checkboxes = document.getElementById("checkboxes")
  if(!expanded) {
    checkboxes.style.display = "block";
    expanded = true;
  }else {
    checkboxes.style.display = "none";
    expanded = false;
  }
}

/*onsubmit="return submission()"
function submission(){
    var sehir = document.forms["Form"]["inputGroupSelect01"].value;
    document.write(sehir);
    if(sehir == "Tüm Yerler")
    {
        alert("Lütfen bir şehir seçiniz.");
        return false;
    }
    return false;
}*/