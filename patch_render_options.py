import re

with open("templates/index.html", "r") as f:
    content = f.read()

fix_render = """
      function renderTestQuestion() {
        const container = document.getElementById("levelTestArea");
        container.innerHTML = "";
        if (currentTestIndex >= levelTestQuestions.length) {
          submitLevelTest();
          return;
        }

        const q = levelTestQuestions[currentTestIndex];
        document.getElementById("testProgress").innerText =
          `Question ${currentTestIndex + 1} / ${levelTestQuestions.length}`;

        const block = document.createElement("div");
        block.className = "level-q-container";
        block.innerHTML = `<h4 class="mb-4">${q.question}</h4>`;

        let options = q.options;
        if (typeof options === "string") {
            try {
                options = JSON.parse(options);
            } catch (e) {
                options = [];
            }
        }

        const shuffledOptions = [...options].sort(() => Math.random() - 0.5);

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
        container.appendChild(block);
      }
"""

content = re.sub(r"function renderTestQuestion\(\) \{.*?\n      \}", fix_render.strip(), content, flags=re.DOTALL)

with open("templates/index.html", "w") as f:
    f.write(content)
