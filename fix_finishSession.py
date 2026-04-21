with open("templates/index.html", "r") as f:
    content = f.read()

s1 = """      function finishSession() {
        // Clear session
        localStorage.removeItem('prism_current_session_id');
        // Refresh dashboard
        loadDashboard();
        // Go back to main
        switchPhase('phase1a');
      }"""
r1 = """      function finishSession() {
        // Clear session
        localStorage.removeItem('prism_current_session_id');
        // Refresh dashboard
        loadDashboard();

        // Reset current chapter state
        currentChapter = "";

        // Go back to main
        switchPhase('phase1a');
      }"""
content = content.replace(s1, r1)

with open("templates/index.html", "w") as f:
    f.write(content)
print("Done")
