You are generating a local service business website from config.json.

Use the values in config.json as the source of truth.

Rules:
- Do not invent fake reviews, ratings, years in business, awards, founders, addresses, or certifications.
- Do not use placeholder phone numbers.
- Use the provided CallRail phone number everywhere.
- Use the provided form URL for all estimate buttons.
- Use the provided email address.
- Use clean, local, human-sounding copy.
- Avoid generic AI phrases.
- Make the site conversion-focused.
- Make the phone number prominent.
- Every page should include internal links to service pages.
- Every page should include a call CTA and form CTA.
- Generate valid HTML.
- Generate clean schema without fake aggregateRating.
- Use canonical URLs with the non-www domain unless config says otherwise.

Output:
- index.html
- about.html
- contact.html
- faq.html
- one page for each service
- one page for each location page
- sitemap.xml
- robots.txt