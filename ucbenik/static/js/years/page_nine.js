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


function tts(el) {
    if ('speechSynthesis' in window) {
        var msg = new SpeechSynthesisUtterance();
        msg.lang = "en-GB";
        msg.text = "year" + el.innerHTML;
        msg.volume = 0.5; // From 0 to 1
        msg.rate = 1; // From 0.1 to 10
        msg.pitch = 2; // From 0 to 2
        if (!msg.text)
            msg.text = "Please enter a value."
        window.speechSynthesis.speak(msg);
    } else{
        // Speech Synthesis Not Supported 😣
        alert("Sorry, your browser doesn't support text to speech!");
    }
}