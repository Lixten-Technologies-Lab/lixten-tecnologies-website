// ============================================
// LIXTEN TECHNOLOGIES - Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  // Navbar scroll effect
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // Intersection Observer for fade-in animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

  // Stagger animations for grid items
  document.querySelectorAll('.grid-2 .fade-in, .grid-3 .fade-in, .grid-4 .fade-in').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.1}s`;
  });

  // Cursor glow effect on cards
  document.querySelectorAll('.card, .service-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty('--mouse-x', `${x}%`);
      card.style.setProperty('--mouse-y', `${y}%`);
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Mobile menu toggle (simple alert for now - can be expanded)
  const menuToggle = document.querySelector('.menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      const navLinks = document.querySelector('.nav-links');
      if (navLinks) {
        const isVisible = navLinks.style.display === 'flex';
        navLinks.style.display = isVisible ? 'none' : 'flex';
        navLinks.style.position = isVisible ? '' : 'absolute';
        navLinks.style.top = isVisible ? '' : '100%';
        navLinks.style.left = isVisible ? '' : '0';
        navLinks.style.right = isVisible ? '' : '0';
        navLinks.style.flexDirection = isVisible ? '' : 'column';
        navLinks.style.background = isVisible ? '' : 'var(--menu-bg)';
        navLinks.style.padding = isVisible ? '' : '2rem';
        navLinks.style.borderBottom = isVisible ? '' : '1px solid var(--menu-border)';
      }
    });
  }

  // Dynamic stats loading from Supabase REST API
  async function loadDynamicStats() {
    if (!window.ENV || !window.ENV.SUPABASE_URL) return;
    try {
      const response = await fetch(`${window.ENV.SUPABASE_URL}/rest/v1/website_settings?select=*`, {
        headers: {
          'apikey': window.ENV.SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${window.ENV.SUPABASE_ANON_KEY}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch settings');
      const data = await response.json();
      
      const mapping = {
        'stats_projects': document.querySelector('[data-stat="projects"]'),
        'stats_clients': document.querySelector('[data-stat="clients"]'),
        'stats_members': document.querySelector('[data-stat="members"]'),
        'stats_satisfaction': document.querySelector('[data-stat="satisfaction"]')
      };
      
      data.forEach(item => {
        const el = mapping[item.key];
        if (el) {
          el.setAttribute('data-target', item.value);
          // If already animated, update the text directly
          if (el.parentElement.classList.contains('counted')) {
            const suffix = el.getAttribute('data-stat') === 'satisfaction' ? '%' : '+';
            el.textContent = (+item.value).toLocaleString() + suffix;
          }
        }
      });

      // Brochure visibility toggle check
      const brochureSetting = data.find(item => item.key === 'show_brochure');
      const showVal = brochureSetting ? brochureSetting.value : 'true';
      localStorage.setItem('lixten-show-brochure', showVal);
      if (showVal === 'false') {
        document.documentElement.setAttribute('data-hide-brochure', 'true');
      } else {
        document.documentElement.removeAttribute('data-hide-brochure');
      }
    } catch (err) {
      console.warn('Could not load dynamic metrics, using defaults:', err);
    }
  }

  loadDynamicStats();

  // Stats counter animation
  const statsSection = document.querySelector('.stats-section');
  if (statsSection) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
          entry.target.classList.add('counted');
          const counters = entry.target.querySelectorAll('.stat-number');
          counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;
            const suffix = counter.getAttribute('data-stat') === 'satisfaction' ? '%' : '+';
            
            const updateCounter = () => {
              current += increment;
              if (current < target) {
                counter.textContent = Math.floor(current).toLocaleString() + suffix;
                requestAnimationFrame(updateCounter);
              } else {
                counter.textContent = target.toLocaleString() + suffix;
              }
            };
            updateCounter();
          });
        }
      });
    }, { threshold: 0.5 });

    counterObserver.observe(statsSection);
  }

  // Create floating particles in hero (if present)
  const hero = document.querySelector('.hero');
  if (hero && !hero.querySelector('.particle')) {
    for (let i = 0; i < 5; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = `${20 + Math.random() * 60}%`;
      particle.style.top = `${20 + Math.random() * 60}%`;
      particle.style.animationDelay = `${Math.random() * 2}s`;
      hero.appendChild(particle);
    }
  }

  // Active nav link based on scroll position
  const sections = document.querySelectorAll('section[id]');
  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      if (window.scrollY >= sectionTop - 200) {
        current = section.getAttribute('id');
      }
    });
    
    document.querySelectorAll('.nav-links a').forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });

  // Theme toggle: light default, dark with data-theme="dark" and localStorage
  const themeToggle = document.getElementById('themeToggle');
  const root = document.documentElement;

  function applySavedTheme() {
    const saved = localStorage.getItem('lixten-theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = saved === 'dark' || (!saved && systemPrefersDark);
    
    if (isDark) {
      root.setAttribute('data-theme', 'dark');
      updateThemeButton(true);
    } else {
      root.removeAttribute('data-theme');
      updateThemeButton(false);
    }
  }

  function updateThemeButton(isDark) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('i');
    if (icon) {
      icon.className = isDark ? 'bi bi-sun' : 'bi bi-moon';
    }
  }

  applySavedTheme();

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = root.getAttribute('data-theme') === 'dark';
      if (isDark) {
        root.removeAttribute('data-theme');
        localStorage.setItem('lixten-theme', 'light');
        updateThemeButton(false);
      } else {
        root.setAttribute('data-theme', 'dark');
        localStorage.setItem('lixten-theme', 'dark');
        updateThemeButton(true);
      }
    });
  }
});

// Add page transition animation on load
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    document.body.classList.add('page-transition');
    setTimeout(() => document.body.classList.remove('page-transition'), 500);
  }
});
