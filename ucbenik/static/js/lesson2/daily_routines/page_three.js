correct = [];

function check(el, value) {
    if(!correct.includes(el)){
        if(value){
            el.classList.add("correct");
            correct.push(el);
        }
        else {
            el.classList.add("incorrect");
        }
    }
    if(correct.length == 18) {
        document.getElementById("next").removeAttribute("disabled");
    }
}