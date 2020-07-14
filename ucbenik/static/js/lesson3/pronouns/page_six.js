function check(el, real) {
    if(real) {
        el.classList.add("correct")
    } else {
        el.classList.add("incorrect")
    }
    let solved = 0;
    let inputs = document.getElementsByClassName ("selection")
    for(let x in inputs) {
        if(inputs[x].tagName == "BUTTON"){
            if(inputs[x].classList.contains("correct") && !inputs[x].classList.contains("incorrect"))
                solved++;
        }
    }
    if(solved == 10){
        document.getElementById("next").removeAttribute("disabled")
    } else {
        document.getElementById("next").setAttribute("disabled", "disabled")
    }
}