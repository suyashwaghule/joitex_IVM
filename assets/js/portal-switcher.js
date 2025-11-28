/* Portal Switcher: injects a control to jump back to the portal selection page */
(function () {
  function goSelect() {
    const target = typeof getNavigationPath === 'function' ? getNavigationPath('select-portal.html') : `${window.location.origin}/select-portal.html`;
    // simple fade-out
    document.body.classList.add('opacity-80');
    setTimeout(() => window.location.href = target, 120);
  }

  // Ensure auth session
  if (!window.auth) return;
  if (!auth.isAuthenticated && !auth.currentUser) return;

  // Try to inject into an existing header; fallback to floating button
  function injectIntoHeader() {
    const header = document.querySelector('header, .header, #header, nav, .topbar');
    if (!header) return false;

    const container = document.createElement('div');
    container.className = 'portal-switcher';

    const btn = document.createElement('button');
    btn.textContent = 'Switch Portal';
    btn.className = 'ml-2 px-3 py-1.5 rounded-md text-sm border border-gray-200 hover:bg-gray-100 transition dark:border-gray-700 dark:hover:bg-gray-800';
    btn.addEventListener('click', goSelect);

    container.appendChild(btn);

    // Place at end of header
    header.appendChild(container);
    return true;
  }

  function injectFloating() {
    const btn = document.createElement('button');
    btn.textContent = 'Switch Portal';
    btn.style.position = 'fixed';
    btn.style.right = '16px';
    btn.style.bottom = '16px';
    btn.style.zIndex = '1000';
    btn.className = 'px-3 py-2 rounded-md text-sm shadow-md bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900';
    btn.addEventListener('click', goSelect);
    document.body.appendChild(btn);
  }

  if (!injectIntoHeader()) injectFloating();
})();
