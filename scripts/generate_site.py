import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.json"
CONTENT_PATH = ROOT / "config" / "content.json"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_service_links(services: list) -> str:
    return "\n".join(
        f'<li><a href="{service["url"]}">{service["name"]}</a></li>'
        for service in services
    )


def build_area_tags(location_pages: list) -> str:
    return "\n".join(
        f'<a class="area-tag" href="{page["url"]}" role="listitem">📍 {page["city"]}</a>'
        for page in location_pages
    )


def build_faq_html(faqs: list, heading: str = "Frequently Asked Questions") -> str:
    if not faqs:
        return ""

    html = [f'<h3 style="margin:40px 0 14px;">{heading}</h3>']
    for item in faqs:
        html.append(f"<h4>{item.get('question', '')}</h4>")
        html.append(f"<p>{item.get('answer', '')}</p>")
    return "\n".join(html)


def build_bullets_html(items: list) -> str:
    return "\n".join(f"<li>{item}</li>" for item in items)


def render(template: str, variables: dict) -> str:
    output = template

    for _ in range(3):
        previous = output
        for key, value in variables.items():
            output = output.replace(key, str(value))

        if output == previous:
            break

    return output


def base_variables(config: dict, content: dict) -> dict:
    business = config["business"]
    location = config["location"]
    services = config["services"]
    location_pages = config["locationPages"]

    home = content.get("home", {})
    about = content.get("about", {})
    contact = content.get("contact", {})
    footer = content.get("footer", {})

    variables = {
        "{{BUSINESS_NAME}}": business["name"],
        "{{NICHE}}": business["niche"],
        "{{PRIMARY_SERVICE}}": business["primaryService"],
        "{{SCHEMA_TYPE}}": business["schemaType"],
        "{{DOMAIN}}": business["domain"],
        "{{PHONE_DISPLAY}}": business["phoneDisplay"],
        "{{PHONE_TEL}}": business["phoneTel"],
        "{{EMAIL}}": business["email"],
        "{{FORM_URL}}": business["formUrl"],

        "{{CITY}}": location["city"],
        "{{STATE_FULL}}": location["state"],
        "{{STATE_ABBR}}": location["stateAbbr"],
        "{{REGION}}": location["region"],

        "{{SERVICE_LINKS_HTML}}": build_service_links(services),
        "{{AREA_TAGS_HTML}}": build_area_tags(location_pages),
        "{{AREA_SERVED_JSON}}": json.dumps(
            [location["city"]] + [page["city"] for page in location_pages]
        ),

        "{{HERO_BADGE}}": home.get("heroBadge", ""),
        "{{HERO_DESCRIPTION}}": home.get("heroDescription", ""),
        "{{SERVICES_INTRO}}": home.get("servicesIntro", ""),
        "{{TRUST_INTRO}}": home.get("trustIntro", ""),
        "{{ABOUT_HEADLINE}}": home.get("aboutHeadline", about.get("headline", "")),
        "{{ABOUT_SNIPPET}}": home.get("aboutSnippet", ""),

     "{{ABOUT_META_DESCRIPTION}}": about.get("metaDescription", ""),
"{{ABOUT_HERO_DESCRIPTION}}": about.get("heroDescription", ""),
"{{ABOUT_PARAGRAPH_1}}": about.get("paragraph1", ""),
"{{ABOUT_PARAGRAPH_2}}": about.get("paragraph2", ""),
"{{VALUES_INTRO}}": about.get("valuesIntro", ""),

"{{CONTACT_HEADLINE}}": contact.get("headline", "Get Your Free Estimate"),
"{{CONTACT_INTRO}}": contact.get("intro", "Call today or complete the estimate form and we’ll get back to you quickly."),
"{{PHONE_CONTACT_NOTE}}": contact.get("phoneNote", "Call for estimates, scheduling, or urgent service questions."),
"{{EMAIL_CONTACT_NOTE}}": contact.get("emailNote", "Use email for general questions or follow-up details."),
"{{CONTACT_SERVICE_AREA}}": contact.get("serviceAreaText", f"{location['city']} and nearby communities."),
        "{{SERVICE_AREA_INTRO}}": (
    f"We proudly provide {business['niche'].lower()} throughout "
    f"{location['city']}, {location['state']}."
),

        "{{FOOTER_DESCRIPTION}}": footer.get("description", f"{business['name']} provides {business['niche'].lower()} in {location['city']}, {location['stateAbbr']}."),
        "{{FOOTER_SERVICE_AREA}}": footer.get("serviceArea", f"Serving {location['city']} and nearby communities."),
        "{{FOOTER_TAGLINE}}": footer.get("tagline", "Local service · Free estimates · Fast response"),

        "{{HOURS_SHORT}}": "Mon–Fri 7am–7pm · Sat 8am–5pm",
        "{{HOURS_FULL}}": "Mon–Fri: 7:00am – 7:00pm<br>Saturday: 8:00am – 5:00pm<br>Sunday: Closed",

        "{{EMERGENCY_BANNER_TEXT}}": "Fast local service available",
        "{{PRIMARY_CTA}}": "Get a Free Estimate",
        "{{PHONE_CTA}}": "Call Now"
    }

    for index, service in enumerate(services, start=1):
        variables[f"{{{{SERVICE_{index}_NAME}}}}"] = service["name"]
        variables[f"{{{{SERVICE_{index}_URL}}}}"] = service["url"]
        variables[f"{{{{SERVICE_{index}_DESCRIPTION}}}}"] = service["description"]

    return variables


def copy_assets() -> None:
    for folder in ["css", "js", "images"]:
        source = ROOT / folder
        target = OUTPUT_DIR / folder
        if source.exists():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)


def generate_static_pages(config: dict, content: dict, variables: dict) -> None:
    pages = {
        "home.html": "index.html",
        "about.html": "about.html",
        "contact.html": "contact.html",
        "faq.html": "faq.html"
    }

    for template_name, output_name in pages.items():
        path = TEMPLATES_DIR / template_name
        if not path.exists():
            continue

        template = path.read_text(encoding="utf-8")
        page_vars = variables.copy()

        if template_name == "faq.html":
            faq_content = content.get("faq", {})
            page_vars["{{FAQ_HEADLINE}}"] = faq_content.get(
                "headline",
                "Frequently Asked Questions"
            )
            page_vars["{{FAQ_INTRO}}"] = faq_content.get("intro", "")
            page_vars["{{FAQ_ITEMS_HTML}}"] = build_faq_html(
                faq_content.get("questions", []),
                faq_content.get("headline", "Frequently Asked Questions")
            )

        rendered = render(template, page_vars)
        (OUTPUT_DIR / output_name).write_text(rendered, encoding="utf-8")


def service_content(content: dict, service_name: str) -> dict:
    for item in content.get("services", []):
        if item.get("name") == service_name:
            return item
    return {}


def generate_service_pages(config: dict, content: dict, variables: dict) -> None:
    template_path = TEMPLATES_DIR / "service.html"
    if not template_path.exists():
        return

    template = template_path.read_text(encoding="utf-8")

    for service in config["services"]:
        copy = variables.copy()
        page_content = service_content(content, service["name"])

        copy.update({
            "{{CURRENT_SERVICE_NAME}}": service["name"],
            "{{CURRENT_SERVICE_URL}}": service["url"],
            "{{CURRENT_SERVICE_DESCRIPTION}}": service["description"],
            "{{CURRENT_SERVICE_TITLE}}": page_content.get("title", f"{service['name']} in {config['location']['city']}, {config['location']['stateAbbr']}"),
            "{{CURRENT_SERVICE_META_DESCRIPTION}}": page_content.get("metaDescription", service["description"]),
            "{{CURRENT_SERVICE_HERO_DESCRIPTION}}": page_content.get("heroDescription", service["description"]),
            "{{CURRENT_SERVICE_HEADLINE}}": page_content.get("headline", service["name"]),
            "{{CURRENT_SERVICE_PARAGRAPH_1}}": page_content.get("paragraph1", ""),
            "{{CURRENT_SERVICE_PARAGRAPH_2}}": page_content.get("paragraph2", ""),
            "{{CURRENT_SERVICE_BULLETS_HTML}}": build_bullets_html(page_content.get("bullets", [])),
            "{{CURRENT_SERVICE_FAQ_HTML}}": build_faq_html(page_content.get("faqs", []), f"Frequently Asked Questions About {service['name']}")
        })

        rendered = render(template, copy)
        (OUTPUT_DIR / service["url"]).write_text(rendered, encoding="utf-8")


def location_content(content: dict, city: str) -> dict:
    for item in content.get("locationPages", []):
        if item.get("city") == city:
            return item
    return {}


def generate_location_pages(config: dict, content: dict, variables: dict) -> None:
    template_path = TEMPLATES_DIR / "location.html"
    if not template_path.exists():
        return

    template = template_path.read_text(encoding="utf-8")

    for location_page in config["locationPages"]:
        copy = variables.copy()
        page_content = location_content(content, location_page["city"])

        copy.update({
            "{{LOCATION_CITY}}": location_page["city"],
            "{{LOCATION_URL}}": location_page["url"],
            "{{LOCATION_TITLE}}": page_content.get("title", f"{config['business']['niche']} in {location_page['city']}, {config['location']['stateAbbr']}"),
            "{{LOCATION_META_DESCRIPTION}}": page_content.get("metaDescription", ""),
            "{{LOCATION_HERO_DESCRIPTION}}": page_content.get("heroDescription", ""),
            "{{LOCATION_PARAGRAPH_1}}": page_content.get("paragraph1", ""),
            "{{LOCATION_PARAGRAPH_2}}": page_content.get("paragraph2", ""),
            "{{LOCATION_FAQ_HTML}}": build_faq_html(page_content.get("faqs", []), f"Frequently Asked Questions About Service in {location_page['city']}")
        })

        rendered = render(template, copy)
        (OUTPUT_DIR / location_page["url"]).write_text(rendered, encoding="utf-8")


def generate_sitemap(config: dict) -> None:
    domain = config["business"]["domain"]
    urls = ["", "about.html", "contact.html", "faq.html"]

    urls += [service["url"] for service in config["services"]]
    urls += [page["url"] for page in config["locationPages"]]

    xml_urls = []
    for url in urls:
        loc = f"https://{domain}/{url}" if url else f"https://{domain}/"
        xml_urls.append(f"  <url>\n    <loc>{loc}</loc>\n  </url>")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(xml_urls)}
</urlset>
"""
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def generate_robots(config: dict) -> None:
    domain = config["business"]["domain"]
    robots = f"""User-agent: *
Allow: /

Sitemap: https://{domain}/sitemap.xml
"""
    (OUTPUT_DIR / "robots.txt").write_text(robots, encoding="utf-8")


def main() -> None:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CONFIG_PATH
    config = load_json(config_path)
    content = load_json(CONTENT_PATH)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    variables = base_variables(config, content)

    copy_assets()
    generate_static_pages(config, content, variables)
    generate_service_pages(config, content, variables)
    generate_location_pages(config, content, variables)
    generate_sitemap(config)
    generate_robots(config)

    print("Site generated successfully.")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()