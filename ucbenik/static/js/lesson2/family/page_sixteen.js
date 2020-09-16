function add(el) {
    var fam = document.getElementById("fam");
    if (fam.children.length < 5) {
        fam.innerHTML = '<div class="msg jenny translation full-width">'+
                        '<input class="textarea" type="text" style="width:100%">.'+
                        '</div>' + 
                        fam.innerHTML
    } else {
        el.style.display = "none"
    }
}