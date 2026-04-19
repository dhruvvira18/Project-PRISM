import re

with open("templates/index.html", "r") as f:
    content = f.read()

# Fix loadLevelTest to remove subject parameter
content = re.sub(r"async function loadLevelTest\(subject\) \{", r"async function loadLevelTest() {", content)
content = re.sub(r"\$\{API_URL\}/level-test\?subject=\$\{encodeURIComponent\(subject\)\}", r"${API_URL}/level-test", content)

# Fix loadChapters
content = re.sub(r"currentChapter = chap;\n\s+loadLevelTest\(subject\);", r"currentChapter = chap;\n              currentLevel = localStorage.getItem('prism_user_level') || 'Intermediate';\n              document.getElementById('levelBadge').innerText = `${currentChapter} | Level: ${currentLevel}`;\n              switchPhase('phase3');", content)

# Fix uploadByomDocument
content = re.sub(r"currentChapter = \"Uploaded Document\";\n\s+loadLevelTest\(\"BYOM\"\);", r"currentChapter = \"Uploaded Document\";\n          currentLevel = localStorage.getItem('prism_user_level') || 'Intermediate';\n          document.getElementById('levelBadge').innerText = `${currentChapter} | Level: ${currentLevel}`;\n          switchPhase('phase3');", content)

# Fix window.onload flow=calibration check
content = re.sub(r"loadLevelTest\(\"BYOM\"\);", r"loadLevelTest();", content)

# Fix renderTestQuestion to use option.difficulty and option.text
# Since we removed string options from BYOM completely, it should just be opt.text and opt.difficulty
render_fix = """
        shuffledOptions.forEach((opt) => {
          const btn = document.createElement("button");
          btn.className = "level-option";
          btn.innerText = opt.text;
          btn.onclick = () => {
            levelTestSelections[currentTestIndex] = opt.difficulty;
            setTimeout(() => {
              currentTestIndex++;
              renderTestQuestion();
            }, 300);
          };
          block.appendChild(btn);
        });
"""

content = re.sub(r"        shuffledOptions\.forEach\(\(opt\) => \{.*?block\.appendChild\(btn\);\n        \}\);", render_fix.strip(), content, flags=re.DOTALL)


# Fix submitLevelTest logic
submit_fix = """
      async function submitLevelTest() {
        const answersArr = Object.values(levelTestSelections);
        if (answersArr.length === 0) answersArr.push(2);
        try {
          const res = await fetch(`${API_URL}/calculate-level`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answers: answersArr }),
          });
          const data = await res.json();
          currentLevel = data.level || "Intermediate";
        } catch (e) {
          currentLevel = "Intermediate";
        }

        document.getElementById("levelBadge").innerText =
          `${currentChapter || 'Calibration'} | Level: ${currentLevel}`;

        const userId = localStorage.getItem('prism_user_id');
        if (userId) {
          try {
            await fetch(`${API_URL}/update-user-level`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: userId, level: currentLevel }),
            });
            localStorage.setItem('prism_user_level', currentLevel);
          } catch (e) {
            console.error("Failed to update user level");
          }
        }

        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('flow') === 'calibration') {
            window.history.replaceState({}, document.title, "/");
            switchPhase("phase1a");
        } else {
            switchPhase("phase1a");
        }
      }
"""

content = re.sub(r"      async function submitLevelTest\(\) \{.*?\n      \}", submit_fix.strip(), content, flags=re.DOTALL)

with open("templates/index.html", "w") as f:
    f.write(content)
