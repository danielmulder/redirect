import re
import json
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PageParser:
    """
    De `PageParser` klasse verwerkt HTML-inhoud van een pagina en haalt diverse elementen op,
    zoals de paginatitel, meta tags, canonical tag, headings, Open Graph tags, en links met metadata.

    Attributes:
        soup (BeautifulSoup): Het BeautifulSoup object voor de HTML-inhoud van de pagina.
        base_url (str): De basis-URL van de pagina voor het bepalen van externe links.
        base_domain (str): Het domein van de basis-URL.
        parsed_data (dict): Opgeslagen gegevens van de geëxtraheerde elementen.
        page_metrics (dict): Opgeslagen metriekgegevens van de pagina.
    """

    def __init__(self, page_content, base_url):
        """
        Initialisatie van de parser met de HTML-inhoud van een pagina.

        Args:
            page_content (str): HTML-inhoud van de pagina om te verwerken.
            base_url (str): De basis-URL van de pagina voor het bepalen van externe links.
        """
        #robots_logger.info(f"Page parser called")
        self.parsed_data = {}
        self.page_metrics = {}
        self.soup = BeautifulSoup(page_content, 'html.parser')
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc

    def extract_elements_only(self):
        """
        Haalt meerdere elementen uit de HTML-inhoud op, zoals de paginatitel, meta tags,
        canonical tag, headings, en Open Graph tags.

        Returns:
            tuple: Een dictionary van geëxtraheerde gegevens en een lijst van externe links.
        """
        self.parsed_data = {
            'title': self.extract_page_title(),
            'meta_description': self.extract_meta_description(),
            'canonical_tag': self.extract_canonical_tag(),
            'robots_meta': self.extract_robots_meta_tag(),
            'headings': self.extract_headings(),
            'open_graph_tags': self.extract_open_graph_tags(),
            'structured_data': self.extract_structured_data(),
            'og_locale': self.extract_open_graph_tags().get('og:locale')
        }
        return {k: v for k, v in self.parsed_data.items() if v} # Filter empty values

    def extract_elements(self):
        """
        Haalt meerdere elementen uit de HTML-inhoud op, zoals de paginatitel, meta tags,
        canonical tag, headings, en Open Graph tags.

        Returns:
            tuple: Een dictionary van geëxtraheerde gegevens en een lijst van externe links.
        """
        logger.info(f"Extraxt elements called")

        self.parsed_data = {
            'title': self.extract_page_title(),
            'meta_description': self.extract_meta_description(),
            'canonical_tag': self.extract_canonical_tag(),
            'robots_meta': self.extract_robots_meta_tag(),
            'headings': self.extract_headings(),
            'open_graph_tags': self.extract_open_graph_tags(),
            'structured_data': self.extract_structured_data()
        }
        # Haal externe links apart op
        external_links = self.extract_links_with_metadata(self.soup, self.base_url)

        logger.info(f"Extraxt elements done")
        return self.parsed_data, external_links

    def extract_hreflang_tags(self):
        """
        Haalt alle hreflang-tags op uit de HTML-inhoud en valideert ze.

        Returns:
            list: Een lijst van geldige hreflang-tags als dictionaries.
            Bijv: [{"hreflang": "nl", "href": "https://www.pouchdirect.nl/"}]
        """
        hreflang_tags = []

        # Zoek alle <link> tags met rel="alternate" en hreflang attribuut
        for link in self.soup.find_all("link", rel="alternate"):
            hreflang = link.get("hreflang")
            href = link.get("href")

            try:
                # Valideer de gevonden tag
                if hreflang and href:
                    hreflang_tag = self.validate_hreflang_tag({
                        "hreflang": hreflang.strip(),
                        "href": href.strip()
                    })
                    hreflang_tags.append(hreflang_tag)
            except ValueError as e:
                logger.error(f"Invalid hreflang tag: {e}")

        return hreflang_tags

    @staticmethod
    def validate_hreflang_tag(hreflang_tag):
        return
        """
        Valideert een enkele hreflang-tag.

        Args:
            hreflang_tag (dict): De hreflang-tag om te valideren.
                Bijv: {"hreflang": "nl", "href": "https://www.example.com/nl/"}

        Returns:
            dict: De gevalideerde hreflang-tag.

        Raises:
            ValueError: Als de tag ongeldig is.
        """
        if not isinstance(hreflang_tag, dict):
            raise ValueError("hreflang tag is not a dictionary.")

        hreflang = hreflang_tag.get("hreflang")
        href = hreflang_tag.get("href")

        if not hreflang or not isinstance(hreflang, str) or not hreflang.strip():
            raise ValueError(f"Invalid hreflang value: {hreflang}")
        if not href or not isinstance(href, str) or not href.strip():
            raise ValueError(f"Invalid href value: {href}")

        # Optioneel: Controleer of de href een geldige URL is
        parsed_href = urlparse(href)
        if not parsed_href.scheme or not parsed_href.netloc:
            raise ValueError(f"Invalid URL in href: {href}")

        return hreflang_tag

    def extract_element_text(self, tag):
        """
        Haalt de tekstinhoud van een HTML-tag op.

        Args:
            tag (str): De naam van de HTML-tag.

        Returns:
            str: De tekstinhoud van de HTML-tag, of een lege string als de tag niet gevonden is.
        """
        element = self.soup.find(tag)
        return element.get_text().strip() if element else ''

    def extract_page_title(self):
        """
        Haalt de paginatitel op.

        Returns:
            str: De titel van de pagina.
        """
        return self.extract_element_text('title')

    def extract_meta_tag_content(self, meta_name):
        """
        Haalt de content van een meta tag op op basis van de naam.

        Args:
            meta_name (str): De naam van de meta tag (bijv. 'description').

        Returns:
            str: De content van de meta tag, of een lege string als de tag niet gevonden is.
        """
        meta_tag = self.soup.select_one(f'meta[name="{meta_name}"]')  # CSS selector
        return meta_tag['content'].strip() if meta_tag and 'content' in meta_tag.attrs else ''

    def extract_meta_description(self):
        """
        Haalt de meta description van de pagina op.

        Returns:
            str: De meta description.
        """
        return self.extract_meta_tag_content('description')

    def extract_robots_meta_tag(self):
        """
        Haalt de robots meta tag op.

        Returns:
            str: De robots meta tag content.
        """
        return self.extract_meta_tag_content('robots')

    def extract_canonical_tag(self):
        """
        Haalt de canonical tag op.

        Returns:
            str: De URL van de canonical tag, of een lege string als deze niet gevonden is.
        """
        #robots_logger.info(f"Extracting canonicals")
        link_tag = self.soup.select_one('link[rel="canonical"]')
        return link_tag['href'].strip() if link_tag and 'href' in link_tag.attrs else ''

    def extract_headings(self):
        """
        Haalt alle headings (H1 tot H6) op uit de HTML-inhoud.

        Returns:
            dict: Een dictionary met de headings gegroepeerd op niveau (bijv. 'h1', 'h2').
        """
        headings = {}
        for level in range(1, 7):
            tags = [tag.text.strip() for tag in self.soup.find_all(f'h{level}')]
            if tags:
                headings[f'h{level}'] = tags
        return headings

    def extract_open_graph_tags(self):
        #robots_logger.info(f"Extracting open graph")
        og_tags = {}
        for meta in self.soup.select('meta[property^="og:"]'):
            property_name = meta['property']
            if property_name.startswith('og:'):
                og_tags[property_name] = meta['content'].strip()
        return og_tags

    @staticmethod
    def extract_anchor_text(link):
        """
        Haalt de ankertekst van een link op.

        Args:
            link (Tag): De link tag.

        Returns:
            str: De ankertekst van de link.
        """
        return link.get_text().strip() if link else ''

    @staticmethod
    def extract_rel_attribute(link):
        """
        Haalt de rel-attribuut van een link op.

        Args:
            link (Tag): De link tag.

        Returns:
            list: De waarde van het rel-attribuut, of None als deze niet aanwezig is.
        """
        return link.get('rel') if link.has_attr('rel') else None

    @staticmethod
    def extract_links_with_metadata(soup, base_url):
        """
        Haalt links met metadata (zoals ankertekst en rel-attribuut) op uit de HTML-inhoud.

        Args:
            soup (BeautifulSoup): Het BeautifulSoup object van de HTML-inhoud.
            base_url (str): De basis-URL voor het omzetten van relatieve URL's.

        Returns:
            list: Een lijst van dictionaries met linkinformatie.
        """
        links_data = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            absolute_url = urljoin(base_url, url)
            parsed_base_url = urlparse(base_url)
            parsed_url = urlparse(absolute_url)
            is_internal = parsed_url.netloc == '' or parsed_url.netloc == parsed_base_url.netloc
            anchor_text = PageParser.extract_anchor_text(link)
            rel_attr = PageParser.extract_rel_attribute(link)
            links_data.append({
                'url': absolute_url,
                'anchor_text': anchor_text,
                'rel': rel_attr
            })
        return links_data

    @staticmethod
    def strip_css_js(html_content):
        """
        Verwijdert CSS en JavaScript uit de HTML-inhoud.

        Args:
            html_content (str): De HTML-inhoud.

        Returns:
            str: De HTML-inhoud zonder CSS en JavaScript.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        for link in soup.find_all("link", rel="stylesheet"):
            link.decompose()
        for tag in soup.find_all(style=True):
            del tag["style"]
        stripped_content = soup.get_text(separator=' ', strip=True)
        return re.sub(r'\s+', ' ', stripped_content)

    def extract_structured_data(self):
        """
        Haalt alle gestructureerde data (zoals JSON-LD en Microdata) uit de HTML-inhoud.

        Returns:
            dict: Een dictionary met gestructureerde data. Sleutels zijn de typen data
                  (bijv. 'json-ld', 'microdata') en waarden zijn lijsten met de gevonden data.
        """
        structured_data = {
            'json-ld': [],
            'microdata': []
        }

        # JSON-LD Extraction
        json_ld_scripts = self.soup.select('script[type="application/ld+json"]')
        if not json_ld_scripts:
            logger.info("No JSON-LD scripts found on the page.")
        else:
            for idx, script in enumerate(json_ld_scripts):
                try:
                    if script.string:
                        json_data = json.loads(script.string.strip())
                        structured_data['json-ld'].append(json_data)
                        logger.debug(f"Found JSON-LD structured data at index {idx}: {json_data}")
                    else:
                        logger.debug(f"Empty JSON-LD script tag at index {idx}. Skipping.")
                except json.JSONDecodeError as e:
                    pass
                    #robots_logger.warning(
                    #    f"Failed to parse JSON-LD structured data at index {idx}: {e.msg} "
                    #    f"(line {e.lineno}, column {e.colno})"
                    #)
                except Exception as e:
                    logger.debug(f"Unexpected error while parsing JSON-LD at index {idx}: {e}")

        # Microdata Extraction
        microdata_elements = self.soup.find_all(attrs={'itemscope': True})
        if not microdata_elements:
            logger.debug("No Microdata elements found on the page.")
        else:
            for idx, item in enumerate(microdata_elements):
                try:
                    microdata = self._parse_microdata(item)
                    if microdata:
                        structured_data['microdata'].append(microdata)
                        logger.debug(f"Found Microdata at index {idx}: {microdata}")
                    else:
                        logger.debug(f"Microdata at index {idx} returned no data. Skipping.")
                except Exception as e:
                    logger.debug(f"Unexpected error while parsing Microdata at index {idx}: {e}")

        if not structured_data['json-ld'] and not structured_data['microdata']:
            logger.info("No structured data (JSON-LD or Microdata) found on the page.")
        else:
            logger.info(f"Extraction completed. Found {len(structured_data['json-ld'])} JSON-LD entries and "
                        f"{len(structured_data['microdata'])} Microdata entries.")

        return structured_data

    def _parse_microdata(self, item):
        """
        Parse een HTML-element met Microdata (itemscope, itemtype, itemprop).

        Args:
            item (Tag): Een BeautifulSoup-tag die Microdata bevat.

        Returns:
            dict: Een dictionary die de Microdata representeert.
        """
        microdata = {}
        if item.has_attr('itemtype'):
            microdata['@type'] = item['itemtype']

        for child in item.find_all(attrs={'itemprop': True}, recursive=False):
            prop_name = child['itemprop']
            if child.has_attr('content'):
                microdata[prop_name] = child['content']
            elif child.name == 'meta' and child.has_attr('content'):
                microdata[prop_name] = child['content']
            else:
                microdata[prop_name] = child.get_text(strip=True)
        return microdata

    def extract_images(self):
        images = []
        for img in self.soup.find_all("img", src=True):
            src = img["src"].strip()

            # Skip inline data-URLs
            if src.lower().startswith("data:"):
                continue  # Go to next <img>

            # Convert everything that is not "data:" into absolute URL
            absolute_src = urljoin(self.base_url, src)
            alt_text = img.get("alt", "").strip()

            images.append({
                "src": absolute_src,
                "alt": alt_text
            })
        return images

    def extract_aria_attributes(self):
        """
        Haalt alle ARIA-attributen op uit de HTML-inhoud.

        Returns:
            list: Een lijst met dictionaries waarin elk item een element en zijn ARIA-attributen bevat.
        """
        aria_elements = []

        for element in self.soup.find_all(True):  # Zoek alle HTML-elementen
            aria_attrs = {k: v for k, v in element.attrs.items() if k.startswith("aria-")}
            if aria_attrs:  # Alleen toevoegen als er aria-attributen zijn
                aria_elements.append({"tag": element.name, "attributes": aria_attrs})

        return aria_elements


