(() => {
  'use strict';

  const header = document.querySelector('.site-header');
  const mobileToggle = document.querySelector('.menu-toggle');
  const mobileNav = document.querySelector('#mobile-nav');
  const productToggle = document.querySelector('.products-toggle');
  const productsMenu = document.querySelector('#products-menu');

  const setMobileMenu = (open) => {
    mobileToggle.setAttribute('aria-expanded', String(open));
    mobileToggle.textContent = open ? 'Close' : 'Menu';
    mobileToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
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
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (!mobileNav.hidden) { setMobileMenu(false); mobileToggle.focus(); }
    if (!productsMenu.hidden) { setProductsMenu(false); productToggle.focus(); }
  });
  const desktopQuery = window.matchMedia('(min-width: 961px)');
  desktopQuery.addEventListener('change', (event) => {
    if (event.matches) setMobileMenu(false);
    else setProductsMenu(false);
  });
  const updateHeader = () => header.classList.toggle('is-scrolled', window.scrollY > 20);
  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();

  // Category navigation always reveals its destination, even after filtering.
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const categories = [...document.querySelectorAll('[data-category]')];
  const filterLabels = { all: 'all 7 products', hands: '4 dexterous hands', arms: 'the P7 robotic arm', software: 'the RealStudio embodied AI platform', humanoids: 'the RealBot humanoid platform' };
  const setFilter = (filter) => {
    filterButtons.forEach((button) => {
      const active = button.dataset.filter === filter;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    categories.forEach((item) => {
      item.hidden = filter !== 'all' && item.dataset.category !== filter;
    });
    const featureGrid = document.querySelector('.platform-products');
    featureGrid.hidden = ![...featureGrid.querySelectorAll('[data-category]')].some((item) => !item.hidden);
    document.querySelector('#products').dataset.activeFilter = filter;
    document.querySelector('#filter-status').textContent = `Showing ${filterLabels[filter]}.`;
  };
  filterButtons.forEach((button) => button.addEventListener('click', () => setFilter(button.dataset.filter)));
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (target?.closest('[hidden]')) setFilter('all');
    setMobileMenu(false);
    setProductsMenu(false);
  });
  window.addEventListener('hashchange', () => {
    const target = document.getElementById(window.location.hash.slice(1));
    if (target?.closest('[hidden]')) {
      setFilter('all');
      target.scrollIntoView();
    }
  });

  // Product information comes from the existing RealHand product content.
  const products = {
    l6: {
      name: 'L6', category: 'RealHand / Dexterous hands', subtitle: 'Compact by design.', image: 'l6.webp',
      description: 'A compact, power-efficient dexterous hand designed for embedded robotics and scalable integration. A starting point for bringing dexterous manipulation into your next system.',
      highlights: ['Compact format', 'Robotic manipulation', 'Hardware integration']
    },
    o6: {
      name: 'O6', category: 'RealHand / Dexterous hands', subtitle: 'Adapt to the task.', image: 'o6.webp',
      description: 'A linkage-driven dexterous hand for handling tools, irregular objects, and everyday manipulation tasks. Designed to connect robotic control with physical interaction.',
      highlights: ['6 active + 5 passive DoF', 'Linkage transmission', 'Dexterous manipulation']
    },
    l20: {
      name: 'L20', category: 'RealHand / Dexterous hands', subtitle: 'More freedom to manipulate.', image: 'l20.webp',
      description: 'A high-DoF dexterous hand for advanced manipulation research, combining precise, repeatable control with optional tactile sensing.',
      highlights: ['16 active + 5 passive DoF', '21 joints', 'Optional tactile sensing']
    },
    l30: {
      name: 'L30', category: 'RealHand / Dexterous hands', subtitle: 'Precision at your fingertips.', image: 'l30-silver-palm.webp',
      description: 'A tendon-driven dexterous hand for responsive manipulation and precise control. Explore fine contact, tool use, and the next generation of embodied intelligence.',
      highlights: ['17 active + 4 passive DoF', 'Tendon-driven actuation', 'CAN FD control']
    },
    p7: {
      name: 'P7', category: 'RealARM / Robotic arms', subtitle: 'Precision in every motion.', image: 'p7.png',
      description: 'A 7-axis robotic arm for arm-hand systems, SDK-controlled motion, and repeatable manipulation demonstrations. Bring reach and coordinated motion to your robotics workflow.',
      highlights: ['7-axis robotic arm', 'Arm-hand integration', 'SDK-controlled motion']
    },
    realbot: {
      name: 'RealBot', category: 'Humanoid robotics', subtitle: 'Embodied intelligence, realized.',
      description: 'A humanoid robot platform for embodied AI research and real-world applications, connecting perception, motion, and physical interaction. Talk to our team about your application and platform requirements.',
      highlights: ['Humanoid robot platform', 'Embodied AI', 'Whole-body interaction']
    }
  };
  const productDialog = document.querySelector('#product-dialog');
  const imageContainer = document.querySelector('#dialog-product-image');
  const highlights = document.querySelector('#dialog-highlights');
  document.querySelectorAll('[data-product]').forEach((button) => {
    button.addEventListener('click', () => {
      const product = products[button.dataset.product];
      if (!product) return;
      document.querySelector('#dialog-category').textContent = product.category;
      document.querySelector('#dialog-title').textContent = product.name;
      document.querySelector('#dialog-subtitle').textContent = product.subtitle;
      document.querySelector('#dialog-description').textContent = product.description;
      document.querySelector('#dialog-contact').href = `mailto:sales@realworldlabs.com?subject=${encodeURIComponent(`${product.name} product enquiry`)}`;
      imageContainer.classList.toggle('is-concept', !product.image);
      if (product.image) {
        const image = new Image();
        image.src = `./assets/products/${product.image}`;
        image.alt = `${product.name} ${product.category.split('/').at(-1).trim()}`;
        imageContainer.replaceChildren(image);
      } else {
        const wordmark = document.createElement('div');
        wordmark.className = 'dialog-wordmark';
        const name = document.createElement('strong');
        name.textContent = product.name;
        const category = document.createElement('span');
        category.textContent = 'Humanoid robotics';
        wordmark.append(name, category);
        imageContainer.replaceChildren(wordmark);
      }
      highlights.replaceChildren(...product.highlights.map((text) => {
        const item = document.createElement('span');
        item.textContent = text;
        return item;
      }));
      document.body.classList.add('modal-open');
      productDialog.showModal();
    });
  });

  // Edition availability follows the supplied RealStudio editions poster and feature matrix.
  const capabilities = {
    control: { number: '01 / CONTROL', heading: 'Connect and teleoperate.', description: 'Connect robots, view live status and sensor data, and teleoperate with data gloves or vision-based hand tracking.', availability: 'Available in every edition.' },
    collect: { number: '02 / COLLECT', heading: 'Capture data. Manage datasets.', description: 'Record synchronized vision, language, action, depth, IMU, and tactile data. Review episodes and manage dataset versions, imports, and exports.', availability: 'Included in Data and Enterprise.' },
    train: { number: '03 / TRAIN', heading: 'Post-train VLA and RL policies.', description: 'Annotate and clean data, post-train π0.5 and Isaac GR00T N1.7, and train humanoid or quadruped locomotion policies.', availability: 'Included in Training and Enterprise.' },
    deploy: { number: '04 / DEPLOY', heading: 'Operate multiple robots on site.', description: 'Monitor and teleoperate robots many-to-many over LAN. Use the Runtime SDK for policy-driven control, or record actions and select them at runtime.', availability: 'Included in Deployment and Enterprise.' }
  };
  const studioTabs = [...document.querySelectorAll('.studio-tab')];
  const studioPanel = document.querySelector('#studio-panel');
  const selectCapability = (button) => {
    const capability = capabilities[button.dataset.capability];
    studioTabs.forEach((tab) => {
      const active = tab === button;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    studioPanel.setAttribute('aria-labelledby', button.id);
    studioPanel.querySelector('.panel-number').textContent = capability.number;
    studioPanel.querySelector('h3').textContent = capability.heading;
    studioPanel.querySelector('.panel-description').textContent = capability.description;
    studioPanel.querySelector('.panel-availability').textContent = capability.availability;
  };
  studioTabs.forEach((button, index) => {
    button.addEventListener('click', () => selectCapability(button));
    button.addEventListener('keydown', (event) => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % studioTabs.length;
      if (event.key === 'ArrowLeft') next = (index + studioTabs.length - 1) % studioTabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = studioTabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      selectCapability(studioTabs[next]);
      studioTabs[next].focus();
    });
  });

  const videoDialog = document.querySelector('#video-dialog');
  const video = document.querySelector('#demo-video');
  const videos = {
    manipulation: { title: 'Object interaction — real-world manipulation', file: 'manipulation' },
    coordination: { title: 'Coordinated manipulation — folding demonstration', file: 'coordination' }
  };
  document.querySelectorAll('[data-video]').forEach((button) => {
    button.addEventListener('click', () => {
      const demo = videos[button.dataset.video];
      document.querySelector('#video-title').textContent = demo.title;
      video.poster = `./assets/demos/${demo.file}.jpg`;
      video.src = `./assets/demos/${demo.file}.mp4`;
      document.body.classList.add('modal-open');
      videoDialog.showModal();
      video.play().catch(() => { /* Native controls remain available. */ });
    });
  });
  [productDialog, videoDialog].forEach((dialog) => {
    dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => {
      if (event.target !== dialog) return;
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => {
      if (!document.querySelector('dialog[open]')) document.body.classList.remove('modal-open');
      if (dialog === videoDialog && !dialog.open) {
        video.pause();
        video.removeAttribute('src');
        video.load();
      }
    });
  });

  document.querySelector('#copyright-year').textContent = String(new Date().getFullYear());
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.documentElement.classList.add('js-motion');
    document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));
    reducedMotion.addEventListener('change', (event) => {
      if (event.matches) document.documentElement.classList.remove('js-motion');
    });
  }
})();
