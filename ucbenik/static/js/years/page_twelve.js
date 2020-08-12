function tts(id) {
    if ('speechSynthesis' in window) {
      var msg = new SpeechSynthesisUtterance();
      msg.text = document.getElementById(id).value;
      if (!msg.text)
        msg.text = "Please enter a value."
      window.speechSynthesis.speak(msg);
     }else{
       // Speech Synthesis Not Supported 😣
       alert("Sorry, your browser doesn't support text to speech!");
     }
  }