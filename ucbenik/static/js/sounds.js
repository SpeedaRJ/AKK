function play(id) {
    var audio = document.getElementById(id);
    audio.play();
  }

function tts(id) {
  if ('speechSynthesis' in window) {
    var msg = new SpeechSynthesisUtterance();
    msg.lang = "en-GB";
    msg.text = document.getElementById(id).value;
    if (!msg.text)
    msg.text = "Please enter a value."
    msg.volume = 0.5; // From 0 to 1
    msg.rate = 1; // From 0.1 to 10
    msg.pitch = 2; // From 0 to 2
    window.speechSynthesis.speak(msg);
   }else{
     // Speech Synthesis Not Supported 😣
     alert("Sorry, your browser doesn't support text to speech!");
   }
}