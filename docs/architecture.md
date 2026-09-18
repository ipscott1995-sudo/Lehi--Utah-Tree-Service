# Architecture

## Core Structure

The system uses:

config.json = factual business/site data  
content.json = AI-generated page copy  
templates/ = reusable HTML templates  
generate_site.py = static site generator  
output/ = finished deployable website  

## Folder Structure

Local SEO Template/

config/
- config.json
- content.json

templates/
- home.html
- about.html
- contact.html
- faq.html
- service.html
- location.html

scripts/
- generate_site.py

css/
- styles.css

js/
- main.js

images/

output/

docs/

## Data Flow

1. User fills out config.json
2. AI generates content.json
3. generate_site.py reads config.json and content.json
4. Templates are rendered into static HTML
5. Static assets are copied into output/
6. Sitemap.xml and robots.txt are generated
7. output/ is deployed to Cloudflare Pages

## Config Responsibilities

config.json contains facts only:

- business name
- niche
- city
- state
- domain
- phone
- email
- form URL
- services
- location pages
- image paths

## Content Responsibilities

content.json contains generated copy:

- homepage text
- about page text
- service page copy
- FAQs
- location page copy
- footer copy
- meta descriptions

## Template Responsibilities

Templates define layout only.

Templates should not contain hardcoded city, business, phone, or niche content except as fallback placeholders.

## Generator Responsibilities

generate_site.py:

- loads config
- loads content
- creates variables
- renders templates
- creates service pages
- creates location pages
- creates sitemap
- creates robots.txt
- copies assets
- outputs finished static site

## Deployment

Deployment automation is future scope.

For V1, the generator creates an output folder that can be manually deployed or connected to GitHub/Cloudflare later.