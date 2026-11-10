(() => {
  'use strict';
  const header = document.querySelector('.site-header');
  const mobileToggle = document.querySelector('.menu-toggle');
  const mobileNav = document.querySelector('#mobile-nav');
  const productToggle = document.querySelector('.products-toggle');
  const productsMenu = document.querySelector('#products-menu');
  const setMobileMenu = (open) => {
    mobileToggle.setAttribute('aria-expanded', String(open));
    mobileToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    mobileToggle.textContent = open ? 'Close' : 'Menu';
    mobileNav.hidden = !open;
  };
  const setProductsMenu = (open) => {
    productToggle.setAttribute('aria-expanded', String(open));
    productsMenu.hidden = !open;
  };
  mobileToggle.addEventListener('click', () => setMobileMenu(mobileNav.hidden));
  productToggle.addEventListener('click', () => setProductsMenu(productsMenu.hidden));
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-dropdown')) setProductsMenu(false);
    if (!event.target.closest('.site-header')) setMobileMenu(false);
    if (event.target.closest('a')) { setMobileMenu(false); setProductsMenu(false); }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (!mobileNav.hidden) { setMobileMenu(false); mobileToggle.focus(); }
    if (!productsMenu.hidden) { setProductsMenu(false); productToggle.focus(); }
  });
  window.matchMedia('(min-width: 961px)').addEventListener('change', () => {
    setMobileMenu(false); setProductsMenu(false);
  });
  const updateHeader = () => header.classList.toggle('is-scrolled', scrollY > 20);
  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();

  const filters = [...document.querySelectorAll('[data-product-filter]')];
  const categories = [...document.querySelectorAll('[data-category]')];
  const setFilter = (key) => {
    filters.forEach((button) => {
      const active = button.dataset.productFilter === key;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    categories.forEach((section) => { section.hidden = key !== 'all' && section.dataset.category !== key; });
    const status = document.querySelector('#filter-status');
    if (status) status.textContent = key === 'all' ? 'Showing all products.' : 'Showing ' + filters.find(b => b.dataset.productFilter === key).textContent.toLowerCase() + '.';
  };
  filters.forEach(button => button.addEventListener('click', () => setFilter(button.dataset.productFilter)));
  const revealHashTarget = () => {
    const target = document.getElementById(location.hash.slice(1));
    if (target && target.closest('[hidden]') && filters.length) {
      setFilter('all'); target.scrollIntoView();
    }
  };
  window.addEventListener('hashchange', revealHashTarget);
  document.addEventListener('click', (event) => {
    const anchor = event.target.closest('a[href]');
    if (!anchor || !filters.length) return;
    const destination = new URL(anchor.href, location.href);
    if (destination.origin !== location.origin || destination.pathname !== location.pathname || !destination.hash) return;
    const target = document.getElementById(destination.hash.slice(1));
    if (target?.closest('[hidden]')) setFilter('all');
  });

  const contentElement = document.querySelector('#studio-content');
  if (contentElement) {
    const capabilities = JSON.parse(contentElement.textContent);
    const tabs = [...document.querySelectorAll('[data-capability]')];
    const panel = document.querySelector('#studio-panel');
    const select = (button) => {
      const capability = capabilities.find(item => item.key === button.dataset.capability);
      tabs.forEach(tab => {
        const active = tab === button;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', String(active));
        tab.tabIndex = active ? 0 : -1;
      });
      panel.setAttribute('aria-labelledby', button.id);
      panel.querySelector('.panel-number').textContent = capability.number + ' / ' + capability.label.toUpperCase();
      panel.querySelector('h3').textContent = capability.heading;
      panel.querySelector('.panel-description').textContent = capability.description;
      panel.querySelector('.panel-availability').textContent = capability.availability;
      panel.querySelector('ul').replaceChildren(...capability.features.map(feature => {
        const li = document.createElement('li'); li.textContent = feature; return li;
      }));
    };
    tabs.forEach((button, index) => {
      button.addEventListener('click', () => select(button));
      button.addEventListener('keydown', (event) => {
        let next;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next === undefined) return;
        event.preventDefault(); select(tabs[next]); tabs[next].focus();
      });
    });
  }

  const comparison = document.querySelector('#feature-matrix');
  const editionSelect = comparison?.querySelector('#matrix-edition');
  if (editionSelect) {
    const groups = [...comparison.querySelectorAll('[data-edition-group]')];
    const selectEdition = () => {
      const option = editionSelect.selectedOptions[0];
      let includedCount = 0;
      let totalCount = 0;
      groups.forEach(group => {
        const included = group.dataset.editionGroup === 'free' ||
          group.dataset.editionGroup === editionSelect.value ||
          editionSelect.value === 'enterprise';
        const count = group.querySelectorAll('li').length;
        totalCount += count;
        if (included) includedCount += count;
        group.classList.toggle('is-included', included);
        group.querySelector('.matrix-group-state').textContent = included ? 'Included' : 'Not included';
        group.open = included;
      });
      comparison.querySelector('.matrix-edition-name').textContent = option.textContent;
      comparison.querySelector('.matrix-edition-description').textContent = option.dataset.description;
      comparison.querySelector('.matrix-edition-count').textContent =
        includedCount + ' of ' + totalCount + ' features included.';
    };
    editionSelect.addEventListener('change', selectEdition);
    selectEdition();
    comparison.classList.add('has-edition-view');
  }

  const viewer = document.querySelector('#image-viewer');
  document.querySelectorAll('[data-lightbox]').forEach(button => {
    button.addEventListener('click', () => {
      viewer.querySelector('img').src = button.dataset.lightbox;
      viewer.querySelector('img').alt = button.querySelector('img').alt;
      viewer.querySelector('p').textContent = button.dataset.caption;
      viewer.showModal(); document.body.classList.add('modal-open');
    });
  });
  viewer?.querySelector('.dialog-close').addEventListener('click', () => viewer.close());
  viewer?.addEventListener('close', () => document.body.classList.remove('modal-open'));
  viewer?.addEventListener('click', event => {
    if (event.target !== viewer) return;
    const rect = viewer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) viewer.close();
  });
  document.querySelectorAll('.article-demo').forEach(details => {
    details.addEventListener('toggle', () => {
      if (!details.open) details.querySelectorAll('video').forEach(video => video.pause());
    });
  });
  document.querySelector('#copyright-year').textContent = String(new Date().getFullYear());
  const legacyRoutes = { realstudio: '/products/realstudio/', software: '/products/realstudio/', hands: '/products/#hands', 'robotic-arms': '/products/p7/', humanoids: '/products/realbot/', realbot: '/products/realbot/', realbrain: '/products/realbrain/', 'in-action': '/blogs/' };
  if (document.body.dataset.page === 'home' && legacyRoutes[location.hash.slice(1)]) location.replace(legacyRoutes[location.hash.slice(1)]);
})();
