with open("templates/index.html", "r") as f:
    content = f.read()

s1 = """      <!-- Navbar/Header with Sidebar Toggle -->
      <div style="position: absolute; top: 20px; left: 20px; z-index: 1000;">"""
r1 = """      <!-- Navbar/Header with Sidebar Toggle -->
      <div style="position: absolute; top: 20px; left: 130px; z-index: 1000;">"""
content = content.replace(s1, r1)

with open("templates/index.html", "w") as f:
    f.write(content)
print("Done")
