function check(el, solution) {
    let solved = false;
    if(el.value.split(",").length === solution.length || el.value.split(" ").length === solution.length || el.value.split(".").length === solution.length ||
        el.value.split("-").length === solution.length || el.value.split(";").length === solution.length || el.value.split(":").length === solution.length)
        solved = true;
    for(let x in solution) {
        if(!el.value.toLowerCase().includes(solution[x])){
            solved = false;
            break;
        }
    }
    if(solved) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    checkCorrectness();
}

function checkCorrectness() {
    let items = document.getElementsByClassName("answer")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === items.length) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}