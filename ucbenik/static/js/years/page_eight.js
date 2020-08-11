function show_congratz(e) {
    let div = document.getElementById("answer")
    if(e.target.innerHTML == "Yes") {
        document.getElementById('a1').play();
        div.children[0].style.backgroundColor = "#00A881";
        div.children[0].innerHTML = "J: Good job!";
        div.children[1].innerHTML = "Dobro ti gre!";
    } else {
        document.getElementById('a2').play();
        div.children[0].style.backgroundColor = "#D55225";
        div.children[0].innerHTML = "J: Practice makes perfect!";
        div.children[1].innerHTML = "Vaja dela mojstra!";
    }
    div.style.display = "block";
    document.getElementById("next").removeAttribute("disabled");
}