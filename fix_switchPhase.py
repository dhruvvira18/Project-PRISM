with open("templates/index.html", "r") as f:
    content = f.read()

s1 = """      function switchPhase(phaseId) {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (typeof stopAudio === "function") stopAudio();
        document
          .querySelectorAll(".phase")
          .forEach((p) => p.classList.remove("active-phase"));
        document.getElementById(phaseId).classList.add("active-phase");
        if (phaseId === "phase3" && !sessionStartTime) startSessionTimer();
      }"""
r1 = """      function switchPhase(phaseId) {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (typeof stopAudio === "function") stopAudio();
        document
          .querySelectorAll(".phase")
          .forEach((p) => p.classList.remove("active-phase"));
        document.getElementById(phaseId).classList.add("active-phase");

        if (phaseId === "phase3") {
            if (!sessionStartTime) startSessionTimer();
        } else {
            // When leaving phase3, reset topic count, timer and current UI state
            document.getElementById("questionInput").value = "";
            document.getElementById("answerSection").style.display = "none";
            document.getElementById("progressDots").innerHTML = "";
            document.getElementById("dynamicCardContainer").innerHTML = "";
            sessionStartTime = null;
            sessionTopicsLearned = 0;
            document.getElementById("topicsCount").innerText = "0";
        }
      }"""
content = content.replace(s1, r1)

with open("templates/index.html", "w") as f:
    f.write(content)
print("Done")
