/* Floating Action Buttons: Switch Portal & Logout */
(function () {
  function goSelect() {
    let target = 'select-portal.html';
    const path = window.location.pathname;

    // Determine relative path based on depth
    if (path.includes('/portals/') && path.split('/portals/')[1].includes('/')) {
      // e.g. /portals/admin/dashboard.html -> level 2
      target = '../../select-portal.html';
    } else if (path.includes('/select-portal.html') || path.endsWith('/index.html') || path.endsWith('/')) {
      return; // Don't show on selection or login page
    }

    window.location.href = target;
  }

  function doLogout() {
    if (window.auth) {
      window.auth.logout();
    } else {
      // Fallback logout navigation
      let target = 'index.html';
      const path = window.location.pathname;
      if (path.includes('/portals/') && path.split('/portals/')[1].includes('/')) {
        target = '../../index.html';
      }
      window.location.href = target;
    }
  }

  function createFloatingButtons() {
    // Prevent duplicates
    if (document.getElementById('floating-actions')) return;

    // Don't show on login/select pages
    const path = window.location.pathname;
    if (path.endsWith('index.html') || path.endsWith('login.html') || path.endsWith('select-portal.html')) return;

    const container = document.createElement('div');
    container.id = 'floating-actions';
    container.style.position = 'fixed';
    container.style.bottom = '30px';
    container.style.right = '30px';
    container.style.zIndex = '10000';
    container.style.display = 'flex';
    container.style.gap = '10px';
    container.style.flexDirection = 'column'; // Vertical stack for FABs usually looks better, or row? User said "easy access". Vertical is common.

    // Style
    const btnStyle = "padding: 0.6rem 1.2rem; border-radius: 50px; border: none; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s;";

    // Switch Portal Button
    const switchBtn = document.createElement('button');
    switchBtn.className = 'btn btn-primary';
    switchBtn.style.cssText = btnStyle + " background-color: #4f46e5; color: white;";
    switchBtn.innerHTML = '<i class="bi bi-grid-fill"></i> Switch Portal';
    switchBtn.onclick = goSelect;
    switchBtn.onmouseover = () => switchBtn.style.transform = 'translateY(-2px)';
    switchBtn.onmouseout = () => switchBtn.style.transform = 'translateY(0)';

    // Logout Button
    const logoutBtn = document.createElement('button');
    logoutBtn.className = 'btn btn-danger';
    // Use a distinct color, e.g. red/danger
    logoutBtn.style.cssText = btnStyle + " background-color: #dc2626; color: white;";
    logoutBtn.innerHTML = '<i class="bi bi-box-arrow-right"></i> Logout';
    logoutBtn.onclick = doLogout;
    logoutBtn.onmouseover = () => logoutBtn.style.transform = 'translateY(-2px)';
    logoutBtn.onmouseout = () => logoutBtn.style.transform = 'translateY(0)';

    container.appendChild(switchBtn);
    container.appendChild(logoutBtn);

    document.body.appendChild(container);
  }

  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createFloatingButtons);
  } else {
    createFloatingButtons();
  }
})();
