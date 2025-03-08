document.addEventListener('DOMContentLoaded', () => {
  /**
   * navTrigger references the dropdown toggle link ("Go to") in the navbar.
   * We'll update its text when the user clicks on a dropdown item or when
   * the Intersection Observer detects a new section in view.
   */
  const navTrigger = document.getElementById('navbarDropdown');

  /**
   * 1) Click behavior for smooth scrolling and text updates.
   * We look for all dropdown items whose href starts with "#".
   */
  document.querySelectorAll('.dropdown-item[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault(); // Prevent default anchor click behavior

      // Update the dropdown toggle text to match the clicked item
      navTrigger.textContent = this.textContent;

      // Extract the section ID by removing the leading "#" from the href
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);

      // If the section exists, smoothly scroll to it
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
      }

      // Optionally, close the dropdown after the click (Bootstrap 5)
      const dd = bootstrap.Dropdown.getOrCreateInstance(navTrigger);
      dd.hide();
    });
  });

  /**
   * 2) Intersection Observer: Automatically update navTrigger text
   *    based on which section is currently in view.
   *
   * sectionMap maps each section's ID to the label text we want to show
   * in the dropdown toggle (navTrigger).
   */
    const sectionMap = {
      'index': 'Index',
      'page_auditor-onpage_audit': 'SEO Audits',
      'page_auditor-link_metrics': 'Link Metrics',
      'tools-get_serp': 'SERP Analysis',
      'tools-is_index_google': 'Google Indexing Checker',
      'tools-keyword_analysis': 'Keyword Analysis',
      'optimize-meta-alt-tags': 'Meta Tags & Alt Tags',
      'tools-robots_util': 'Check Robots.txt', // <- Deze komma miste!
      'tools-whois_lookup': 'Whois Lookup',
      'tools-insecure_headers': 'Check Headers',
      'tools-create_optimized_content': 'SEO Optimize Content',
      'tools-improve_titles_meta': 'Optimize Meta Tags',
      'tools-actionable_reports': 'Actionable Reports'
    };

  /**
   * Intersection Observer options:
   * - root: null => the viewport
   * - threshold: 0.5 => the section is considered "in view" when 50% of it is visible
   */
  const options = {
    root: null,
    rootMargin: '0px',
    threshold: 0.5
  };

  /**
   * Create the observer. When a section is at least 50% in view,
   * we check if it's one of our mapped IDs. If so, we update navTrigger.
   */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        if (sectionMap[id]) {
          navTrigger.textContent = sectionMap[id];
        }
      }
    });
  }, options);

  /**
   * Attach the observer to each relevant section by its ID.
   */
  Object.keys(sectionMap).forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      observer.observe(el);
    }
  });
});
