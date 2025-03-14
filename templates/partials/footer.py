from flask import render_template_string

def render_footer():
    footer = """<footer id="footer" class="bg-light text-center py-3 mt-5">
    <p>&copy; {{ year }} Pro SEO Assistant | All rights reserved |
        <a href="https://chatgpt.com/g/g-67a9c0b376d881918b85c637d77761f0-pro-seo-assistant" target="_blank">
            Try Pro SEO Assistant GPT
        </a>
        | 
        <a href="https://www.facebook.com/people/Pro-SEO-Assistant-GPT/61574061533622/" target="_blank">
            Facebook
        </a>
    </p>
</footer>
    """
    return render_template_string(footer, year=2025)
