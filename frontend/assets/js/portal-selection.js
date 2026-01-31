/* Portal Selection Page Logic */
(function () {
  console.log('Portal selection script loaded');
  
  // DOM Elements
  const app = document.getElementById('app');
  const grid = document.getElementById('portalsGrid');
  const greeting = document.getElementById('greeting');
  const emptyState = document.getElementById('emptyState');
  const logoutBtn = document.getElementById('logoutBtn');
  const themeToggle = document.getElementById('themeToggle');
  const userNameDisplay = document.getElementById('userNameDisplay');
  const userRoleDisplay = document.getElementById('userRoleDisplay');

  // Role Icons Mapping
  const ROLE_ICONS = {
    admin: 'bi-shield-lock-fill',
    callcenter: 'bi-headset',
    sales: 'bi-graph-up-arrow',
    salesexec: 'bi-person-badge',
    engineer: 'bi-tools',
    inventory: 'bi-box-seam-fill',
    network: 'bi-hdd-network-fill',
    finance: 'bi-cash-coin'
  };

  // Role Descriptions (Optional flavor text)
  const ROLE_DESC = {
    admin: 'System configuration & user management',
    callcenter: 'Customer support & ticket handling',
    sales: 'Sales strategy & team performance',
    salesexec: 'Lead management & new acquisitions',
    engineer: 'Field operations & maintenance',
    inventory: 'Stock tracking & equipment logic',
    network: 'Infrastructure monitoring & uptime',
    finance: 'Billing, invoicing & revenue analysis'
  };

  // Theme Handling
  function initTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) {
      document.documentElement.classList.toggle('dark', stored === 'dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', prefersDark);
    }
  }

  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  themeToggle?.addEventListener('click', toggleTheme);
  initTheme();

  // Authentication Check
  if (!window.auth) {
    console.error('Auth module not found');
    return;
  }
  
  if (!auth.protectPage()) {
    return;
  }

  // Update User Profile in Navbar
  const user = auth.currentUser;
  if (user) {
    if (userNameDisplay) userNameDisplay.textContent = user.name || 'User';
    if (userRoleDisplay) userRoleDisplay.textContent = user.role || 'Guest';
    
    // Update Greeting
    if (greeting) {
      greeting.innerHTML = `Welcome back, <span class="text-brand-600 dark:text-brand-400">${user.name.split(' ')[0]}</span>`;
    }
  }

  logoutBtn?.addEventListener('click', () => auth.logout());

  // Helper: Check Access
  function hasAccess(user, portalRole) {
    if (!user) return false;
    if (Array.isArray(user.permissions) && user.permissions.includes('all')) return true;
    if (Array.isArray(user.portals) && user.portals.includes(portalRole)) return true;
    if (user.role === portalRole) return true;
    return false;
  }

  // Helper: Create Card
  function createCard(portal, enabled) {
    const card = document.createElement('div');
    const iconClass = ROLE_ICONS[portal.role] || 'bi-grid-fill';
    const description = ROLE_DESC[portal.role] || 'Access portal dashboard';
    
    // Dynamic styles based on state
    const opacityClass = enabled ? 'opacity-100' : 'opacity-60 grayscale';
    const cursorClass = enabled ? 'cursor-pointer' : 'cursor-not-allowed';
    
    card.className = `glass-card group relative p-6 rounded-2xl flex flex-col gap-4 ${opacityClass} ${cursorClass}`;
    
    card.innerHTML = `
      <div class="flex items-start justify-between">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-xl text-white shadow-lg transition-transform group-hover:scale-110 duration-300" 
             style="background: ${portal.color}">
          <i class="bi ${iconClass}"></i>
        </div>
        ${enabled 
          ? `<span class="px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide bg-emerald-100 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20">Active</span>`
          : `<span class="px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700">Locked</span>`
        }
      </div>
      
      <div>
        <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-1 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">${portal.name}</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">${description}</p>
      </div>

      <div class="mt-auto pt-4 flex items-center justify-between border-t border-slate-200/50 dark:border-slate-700/50">
        <span class="text-xs font-medium text-slate-400">v1.0.0</span>
        <button class="enterBtn w-8 h-8 rounded-full flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 group-hover:bg-brand-500 group-hover:text-white transition-all duration-300 shadow-sm">
          <i class="bi bi-arrow-right"></i>
        </button>
      </div>
    `;

    // Click Handler
    const handleEnter = (e) => {
      // Prevent bubble up if clicking specific inner elements if needed, 
      // but here we want the whole card to be clickable or just the button?
      // Let's make the whole card clickable for better UX if enabled.
      if (!enabled) {
        card.classList.add('shake');
        setTimeout(() => card.classList.remove('shake'), 500);
        return;
      }

      // Re-verify auth
      if (!auth.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
      }

      // Animation before redirect
      card.style.transform = 'scale(0.95)';
      card.style.opacity = '0';
      
      const target = typeof getNavigationPath === 'function' 
        ? getNavigationPath(portal.dashboard) 
        : portal.dashboard;

      setTimeout(() => {
        window.location.href = target;
      }, 200);
    };

    if (enabled) {
        card.addEventListener('click', handleEnter);
    } else {
        // Prevent click but show shake
        card.addEventListener('click', () => {
             card.classList.add('shake');
             setTimeout(() => card.classList.remove('shake'), 500);
        });
    }

    return card;
  }

  // Render Function
  function render() {
    if (!window.ROLE_CONFIG || !grid) return;
    
    const portals = Object.entries(window.ROLE_CONFIG).map(([role, cfg]) => ({
      role,
      ...cfg
    }));

    grid.innerHTML = '';
    
    const items = portals.map(p => ({ p, enabled: hasAccess(auth.currentUser, p.role) }));
    
    // Sort: Enabled first
    items.sort((a, b) => Number(b.enabled) - Number(a.enabled));
    
    if (items.filter(i => i.enabled).length === 0) {
      emptyState?.classList.remove('hidden');
    } else {
      emptyState?.classList.add('hidden');
    }

    items.forEach(({ p, enabled }, index) => {
      const card = createCard(p, enabled);
      // Stagger animation
      card.style.animation = `slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards ${index * 100}ms`;
      grid.appendChild(card);
    });
  }

  render();

})();
