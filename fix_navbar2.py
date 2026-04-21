with open("templates/index.html", "r") as f:
    content = f.read()

s1 = """      <!-- Navbar/Header with Sidebar Toggle -->
      <div style="position: absolute; top: 20px; left: 130px; z-index: 1000;">
        <button class="btn btn-outline-secondary" type="button" data-bs-toggle="offcanvas" data-bs-target="#dashboardSidebar" aria-controls="dashboardSidebar" style="border-color: var(--primary-blue); color: var(--primary-blue); border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; background: white; box-shadow: var(--card-shadow);">
          <i class="fas fa-bars"></i>
        </button>
      </div>"""
r1 = """      <!-- Navbar/Header with Sidebar Toggle -->
      <div style="position: absolute; top: 20px; left: 140px; z-index: 1000;">
        <button class="btn btn-outline-secondary" type="button" data-bs-toggle="offcanvas" data-bs-target="#dashboardSidebar" aria-controls="dashboardSidebar" style="border-color: var(--primary-blue); color: var(--primary-blue); border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; background: white; box-shadow: var(--card-shadow);">
          <i class="fas fa-bars"></i>
        </button>
      </div>"""
content = content.replace(s1, r1)

with open("templates/index.html", "w") as f:
    f.write(content)
print("Done")
