function add(el) {
    var fam = document.getElementById("fam");
    if (fam.children.length < 6) {
        fam.innerHTML = '<div class="msg jenny translation full-width">'+
                        'I have a <input class="textarea" type="text" style="width:20%">.'+
                        '<input class="textarea" type="text"  style="width:20%"> name is '+
                        '<input class="textarea" type="text"  style="width:20%">.</div>' + 
                        fam.innerHTML
    } else {
        el.style.display = "none"
    }
}