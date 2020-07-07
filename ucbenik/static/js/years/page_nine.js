function setYears() {
    let selected = [];
    while (selected.length != 5) {
        let year = Math.floor(Math.random() * (2020 - 1000 + 1) ) + 1000;;
        if(selected.indexOf(year) == -1) {
            selected.push(year);
        }
    }
    document.getElementById("one").innerHTML = selected[0];
    document.getElementById("two").innerHTML = selected[1];
    document.getElementById("three").innerHTML = selected[2];
    document.getElementById("four").innerHTML = selected[3];
    document.getElementById("five").innerHTML = selected[4];
}


function redo(){
    setYears();
}

$(function () {
    setYears();
    document.getElementById("next").removeAttribute("disabled");
});