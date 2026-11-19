const header = document.querySelector('.nav-wrap');
const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('.mobile-menu');

if (header && menuButton && menu) {
  const compact = window.matchMedia('(max-width: 47.99rem)');

  function setMenu(open) {
    menu.hidden = !open;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  }

  setMenu(false);
  header.dataset.enhanced = '';
  compact.addEventListener('change', () => {
    if (!compact.matches && (menu.contains(document.activeElement) || document.activeElement === menuButton)) {
      header.querySelector('.links a')?.focus();
    }
    setMenu(false);
  });
  menuButton.addEventListener('click', () => {
    setMenu(menu.hidden);
    if (!menu.hidden) menu.querySelector('a')?.focus();
  });

  menu.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (!link) return;
    setMenu(false);
    if (link.pathname === window.location.pathname && link.hash) {
      const target = document.getElementById(link.hash.slice(1));
      if (target) {
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      }
    }
  });

  document.addEventListener('click', (event) => {
    if (!header.contains(event.target)) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !menu.hidden) {
      setMenu(false);
      menuButton.focus();
    }
  });
}

const moreButton = document.querySelector('.who-more-toggle');
const moreCopy = document.querySelector('.who-more');

if (moreButton && moreCopy) {
  const narrow = window.matchMedia('(max-width: 42.5rem)');

  function updateMore(collapsed) {
    moreCopy.hidden = collapsed;
    moreButton.setAttribute('aria-expanded', String(!collapsed));
    moreButton.querySelector('span').textContent = collapsed ? 'Read more' : 'Show less';
  }

  function updateLayout() {
    if (narrow.matches) {
      moreButton.dataset.enhanced = '';
    } else {
      delete moreButton.dataset.enhanced;
    }
    updateMore(narrow.matches);
  }

  narrow.addEventListener('change', updateLayout);
  moreButton.addEventListener('click', () => updateMore(!moreCopy.hidden));
  updateLayout();
}
