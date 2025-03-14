from flask import render_template_string, url_for, request


def render_nav():
    # ✅ Vergelijk zonder extra trailing slash
    is_homepage = request.path.rstrip('/') == url_for('pages.home').rstrip('/')
    is_shared_chat = request.path.rstrip('/') == url_for('pages.shared_chat_sessions').rstrip('/')

    nav = f"""
    <nav id="sticky-nav" class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{url_for('pages.home')}">
                <img id="logo_nav" src="https://proseo.tech/static/images/logo.svg" alt="Pro SEO Tech Logo">
                <span class="logo-text">Pro SEO Assistant</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                    data-bs-target="#navbarNav" aria-controls="navbarNav"
                    aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <!-- ✅ Dropdown-menu alleen tonen op de homepage -->
                    {(
        '''
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown"
               role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Index
            </a>
            <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
                <li><a class="dropdown-item" href="#index">Index</a></li>
                <li><a class="dropdown-item" href="#page_auditor-onpage_audit">SEO Audits</a></li>
                <li><a class="dropdown-item" href="#page_auditor-link_metrics">Link Metrics</a></li>
                <li><a class="dropdown-item" href="#tools-keyword_analysis">Keyword Analysis</a></li>
                <li><a class="dropdown-item" href="#tools-create_optimized_content">SEO Optimize Content</a></li>
                <li><a class="dropdown-item" href="#tools-improve_titles_meta">Optimize Meta Tags</a></li>
                <li><a class="dropdown-item" href="#optimize-meta-alt-tags">Meta & Alt Tags</a></li>
                <li><a class="dropdown-item" href="#tools-robots_util">Robots.txt Checker</a></li>
                <li><a class="dropdown-item" href="#tools-get_serp">SERP Analysis</a></li>
                <li><a class="dropdown-item" href="#tools-is_index_google">Google Indexing Checker</a></li>
                <li><a class="dropdown-item" href="#tools-whois_lookup">Whois Lookup</a></li>
                <li><a class="dropdown-item" href="#tools-insecure_headers">Check Insecure Headers</a></li>
                <li><a class="dropdown-item" href="#tools-actionable_reports">Actionable Reports</a></li>
            </ul>
        </li>
        ''' if is_homepage else f'''
                    <li class="nav-item">
                        <a class="nav-link" href="{url_for('pages.home')}">
                            Home
                        </a>
                    </li>
                    '''
    )}

                    <!-- ✅ Shared Chats altijd tonen -->
                    <li class="nav-item">
                        <a class="nav-link {'active' if is_shared_chat else ''}" 
                           href="{url_for('pages.shared_chat_sessions')}">
                            Shared Chats
                        </a>
                    </li>
                </ul>

                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item dropdown me-3">
                        <a class="nav-link dropdown-toggle" href="#" id="langDropdown"
                           role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            Language
                        </a>
                        <ul class="dropdown-menu lang-dropdown" aria-labelledby="langDropdown">
                            <li><a class="dropdown-item" href="/">EN</a></li>
                            <li><a class="dropdown-item" href="/nl/">NL</a></li>
                        </ul>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-light text-primary px-3 py-2 fw-bold"
                           href="https://chatgpt.com/g/g-67a9c0b376d881918b85c637d77761f0-pro-seo-assistant"
                           target="_blank">
                            Use Pro SEO Assistant
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    """

    return render_template_string(nav)
