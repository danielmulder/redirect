document.addEventListener('DOMContentLoaded', () => {
  const navTrigger = document.getElementById('navbarDropdown');

  // 1) Klikgedrag voor smooth scroll + tekstupdate
  document.querySelectorAll('.dropdown-item[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
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

  // 2) Intersection Observer: sectie in beeld => update navTrigger
  // Mapping van ID -> label (zoals in je dropdown)
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