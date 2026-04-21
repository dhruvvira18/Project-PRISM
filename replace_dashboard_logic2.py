with open("templates/index.html", "r") as f:
    content = f.read()

s1 = """                    try {
                        let parsed = JSON.parse(chat.ai_response);
                        if (parsed && parsed.steps) {
                            aiDataStr = parsed.steps.map(s => {
                                if (s.type === 'concept') return `<p><strong>${s.title}</strong>: ${s.content}</p>`;
                                if (s.type === 'visual') return `<p><strong>Visual:</strong> <i class="fas ${s.icon}"></i> ${s.title}</p>`;
                                if (s.type === 'analogy') return `<p><strong>Analogy:</strong> ${s.content}</p>`;
                                if (s.type === 'quiz') return `<p><strong>Quiz:</strong> ${s.question}</p>`;
                                return "";
                            }).join("");
                        } else {
                            aiDataStr = "No formatted response available.";
                        }
                    } catch(e) {
                        aiDataStr = "No details available.";
                    }"""

r1 = """                    try {
                        let parsed = JSON.parse(chat.ai_response);
                        if (parsed) {
                            if (Array.isArray(parsed.flashcards) && parsed.flashcards.length > 0) {
                                aiDataStr += '<div style="margin-top: 10px;">';
                                parsed.flashcards.slice(0, 3).forEach((card, idx) => {
                                    const bullets = Array.isArray(card.bullet_points) ? card.bullet_points.slice(0, 3) : [];
                                    let listHtml = '<ul class="key-points-list" style="padding-left: 20px; font-size: 0.95rem; line-height: 1.6;">';
                                    bullets.forEach(point => {
                                        listHtml += `<li style="margin-bottom: 8px;">${clean(point)}</li>`;
                                    });
                                    listHtml += '</ul>';

                                    aiDataStr += `
                                        <div style="background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                                            <h4 style="color: var(--primary-blue); font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
                                                <i class="fas fa-brain" style="color: var(--primary-green);"></i> ${card.title || `Flashcard ${idx + 1}`}
                                            </h4>
                                            ${listHtml}
                                        </div>
                                    `;
                                });
                                aiDataStr += '</div>';
                            } else if (parsed.steps) {
                                aiDataStr = parsed.steps.map(s => {
                                    if (s.type === 'concept') return `<p><strong>${s.title}</strong>: ${s.content}</p>`;
                                    if (s.type === 'visual') return `<p><strong>Visual:</strong> <i class="fas ${s.icon}"></i> ${s.title}</p>`;
                                    if (s.type === 'analogy') return `<p><strong>Analogy:</strong> ${s.content}</p>`;
                                    if (s.type === 'quiz') return `<p><strong>Quiz:</strong> ${s.question}</p>`;
                                    return "";
                                }).join("");
                            } else {
                                aiDataStr = "No formatted response available.";
                            }
                        }
                    } catch(e) {
                        aiDataStr = "No details available.";
                    }"""

content = content.replace(s1, r1)

with open("templates/index.html", "w") as f:
    f.write(content)
print("Done")
