document.addEventListener('DOMContentLoaded', () => {
  const navTrigger = document.getElementById('navbarDropdown');

  // 1) Klikgedrag voor smooth scroll + tekstupdate
  document.querySelectorAll('.dropdown-item[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();

      // Alle links resetten
      document.querySelectorAll('.dropdown-item').forEach(item => {
        item.classList.remove('active');
      });

      // Voeg 'active' toe aan de aangeklikte link
      this.classList.add('active');

      navTrigger.textContent = this.textContent; // Update de navTrigger-tekst
      const targetId = this.getAttribute('href').substring(1);
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: 'smooth' });
      }

      // Optioneel: sluit de dropdown
      const dd = bootstrap.Dropdown.getOrCreateInstance(navTrigger);
      dd.hide();
    });
  });

  // 2) Intersection Observer: sectie in beeld => update navTrigger + actieve link
  const sectionMap = {
    'index': 'Index',
    'page_auditor-onpage_audit': 'SEO Audits',
    'page_auditor-link_metrics': 'Link Metrics',
    'tools-get_serp': 'SERP Analysis',
    'tools-is_index_google': 'Google Indexing Checker',
    'tools-keyword_analysis': 'Keyword Analysis'
  };

  // Opties voor IntersectionObserver
  const options = {
    root: null,         // viewport
    rootMargin: '0px',
    threshold: 0.5      // pas aan wanneer sectie "in view" is
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Bepaal welke sectie in beeld komt, update navTrigger
        const id = entry.target.id;
        if (sectionMap[id]) {
          navTrigger.textContent = sectionMap[id];

          // Reset de actieve status voor alle links
          document.querySelectorAll('.dropdown-item').forEach(link => {
            link.classList.remove('active');
          });

          // Voeg 'active' toe aan de juiste link
          const activeLink = document.querySelector(`.dropdown-item[href="#${id}"]`);
          if (activeLink) {
            activeLink.classList.add('active');
          }
        }
      }
    });
  }, options);

  // Observer aan elke sectie koppelen
  Object.keys(sectionMap).forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
});
