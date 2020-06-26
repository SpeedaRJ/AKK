function check(e, solution) {
    let array = [].slice.call(e.target.parentNode.children)
    for(let x in array){
            if(array[x].tagName.toLowerCase() == "label") {
                array[x].style.color = "#333";
            }
        }
    if(e.target.id.includes(solution)){
        for(let x in array){
            if(array[x].tagName.toLowerCase() == "label") {
                if(array[x].htmlFor == e.target.id) {
                    array[x].style.color = "#00A881";
                    array[x].parentNode.classList.add('correct');
                    array[x].parentNode.classList.remove('incorrect');
                }
            }
        }
    } else {
        for(let x in array){
            if(array[x].tagName.toLowerCase() == "label") {
                if(array[x].htmlFor == e.target.id) {
                    array[x].style.color = "#F15D2A";
                    array[x].parentNode.classList.add('incorrect');
                    array[x].parentNode.classList.remove('correct');
                }
            }
        }
    }
    checkCorrectness()
}

function checkCorrectness() {
    let items = document.getElementsByClassName("question")
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