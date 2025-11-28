/* Portal Selection Page Logic */
(function () {
  console.log('Portal selection script loaded');
  console.log('Auth available:', !!window.auth);
  console.log('ROLE_CONFIG available:', !!window.ROLE_CONFIG);
  
  const app = document.getElementById('app');
  const grid = document.getElementById('portalsGrid');
  const greeting = document.getElementById('greeting');
  const emptyState = document.getElementById('emptyState');
  const logoutBtn = document.getElementById('logoutBtn');
  const themeToggle = document.getElementById('themeToggle');

  // Page enter transition
  requestAnimationFrame(() => app?.classList.add('page-enter-active'));

  // Theme handling
  function initTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) {
      document.documentElement.classList.toggle('dark', stored === 'dark');
      return;
    }
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.toggle('dark', prefersDark);
  }

  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  themeToggle?.addEventListener('click', toggleTheme);
  initTheme();

  // Require auth on this page
  if (!window.auth) {
    console.error('Auth not available!');
    return;
  }
  
  if (!auth.protectPage()) {
    console.log('User not authenticated, redirecting...');
    return;
  }

  console.log('Current user:', auth.currentUser);

  // Greeting
  const name = auth.currentUser?.name || 'User';
  if (greeting) {
    greeting.textContent = `Welcome, ${name} — Choose Your Portal`;
  }

  logoutBtn?.addEventListener('click', () => auth.logout());

  // Build list of portals from ROLE_CONFIG
  function listPortals() {
    return Object.entries(window.ROLE_CONFIG || {}).map(([role, cfg]) => ({
      role,
      name: cfg.name,
      color: cfg.color,
      dashboard: cfg.dashboard
    }));
  }

  function hasAccess(user, portalRole) {
    if (!user) return false;
    // Admin has access to all portals
    if (Array.isArray(user.permissions) && user.permissions.includes('all')) return true;
    // Check if user has this portal in their portals array
    if (Array.isArray(user.portals) && user.portals.includes(portalRole)) return true;
    // Fallback: user's primary role matches portal
    if (user.role === portalRole) return true;
    return false;
  }

  function createCard(portal, enabled) {
    const card = document.createElement('div');
    card.className = `group relative rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800/60 p-5 shadow-sm hover:shadow-md transition ${!enabled ? 'opacity-60' : ''}`;

    card.innerHTML = `
      <div class="flex items-start gap-4">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center text-white font-semibold" style="background:${portal.color}">
          ${portal.name.charAt(0)}
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-medium">${portal.name}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">${portal.role.charAt(0).toUpperCase() + portal.role.slice(1)} Portal</p>
        </div>
      </div>
      <div class="mt-5 flex items-center justify-between">
        <span class="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">${enabled ? 'Authorized' : 'Restricted'}</span>
        <button class="enterBtn px-3 py-1.5 rounded-md text-sm font-medium ${enabled ? 'bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100' : 'bg-gray-200 text-gray-500 cursor-not-allowed'} transition">Enter Portal</button>
      </div>
    `;

    const btn = card.querySelector('.enterBtn');
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      // Re-validate on click
      if (!auth.isAuthenticated()) {
        window.location.href = typeof getNavigationPath === 'function' ? getNavigationPath('index.html') : `${window.location.origin}/index.html`;
        return;
      }
      const allowed = hasAccess(auth.currentUser, portal.role);
      if (!allowed) {
        btn.blur();
        btn.classList.add('shake');
        alert('Access Denied');
        return;
      }

      // Smooth exit transition then redirect
      app.classList.add('page-exit-active');
      const target = typeof getNavigationPath === 'function' ? getNavigationPath(portal.dashboard) : `${window.location.origin}/${portal.dashboard}`;
      setTimeout(() => { window.location.href = target; }, 200);
    });

    return card;
  }

  function render() {
    console.log('Render function called');
    const portals = listPortals();
    console.log('Portals found:', portals.length, portals);
    
    if (!grid) {
      console.error('Grid element not found!');
      return;
    }
    
    grid.innerHTML = '';

    const items = portals.map(p => ({ p, enabled: hasAccess(auth.currentUser, p.role) }));
    const visible = items.filter(x => x.enabled);
    
    console.log('Items with access:', visible.length);

    // Show authorized first, then restricted (dimmed)
    items.sort((a, b) => Number(b.enabled) - Number(a.enabled));

    if (visible.length === 0) {
      emptyState?.classList.remove('hidden');
    } else {
      emptyState?.classList.add('hidden');
    }

    for (const { p, enabled } of items) {
      grid.appendChild(createCard(p, enabled));
    }
    
    console.log('Render complete, cards added:', items.length);
  }

  render();
})();
