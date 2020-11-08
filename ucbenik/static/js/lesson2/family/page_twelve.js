function solution(el, solution){
    if(solution == el.value.toLowerCase().trim()){
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else{
        el.classList.remove("correct");
        el.classList.add("incorrect");
    }
    checkCorrectness();
}

function checkCorrectness() {
    let items = document.getElementsByClassName("textarea")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 8) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}