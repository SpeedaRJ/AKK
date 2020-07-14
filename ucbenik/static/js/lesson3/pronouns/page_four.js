function solution(el, solution) {
    if(el.value.toLowerCase() == solution) {
       el.classList.add('correct');
       el.classList.remove('incorrect');
    } else {
        el.classList.remove('correct');
       el.classList.add('incorrect');
    }
    let solved = 0;
    let inputs = document.getElementsByClassName ("answer")
    for(let x in inputs) {
        if(inputs[x].tagName == "INPUT"){
            if(inputs[x].classList.contains("correct") && !inputs[x].classList.contains("incorrect"))
                solved++;
        }
    }
    if(solved == 8){
        document.getElementById("next").removeAttribute("disabled")
        document.getElementById("conversation_two").removeAttribute("hidden")
        document.getElementById("conversation_one").setAttribute("hidden", "hidden")
    } else {
        document.getElementById("next").setAttribute("disabled", "disabled")
        document.getElementById("conversation_one").removeAttribute("hidden")
        document.getElementById("conversation_two").setAttribute("hidden", "hidden")
    }
}