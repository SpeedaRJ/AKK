function toggle_c(el) {
    if (el.classList.contains("correct")) {
        el.classList.remove("correct");
    } else {
        el.classList.add("correct");
    }
    check()
}

function toggle_i(el) {
    if (el.classList.contains("incorrect")) {
        el.classList.remove("incorrect");
    } else {
        el.classList.add("incorrect");
    }
    check()
}

function check() {
    let paras = document.getElementsByClassName("in")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined) {
            if(paras[x].className.includes("correct"))
                counter++;
        }
    }
    if(counter === 16)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}