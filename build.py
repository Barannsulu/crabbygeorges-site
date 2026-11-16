#!/usr/bin/env python3
"""Builds the static crabbygeorges.com site into ./site from ./src.

Edit content in src/ (partials, data below), then run: python3 build.py
Netlify publishes the ./site folder as-is (no build step needed there).
"""
import html, json, re, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "site"
DOMAIN = "https://crabbygeorges.com"
TODAY = datetime.date.today().isoformat()

def part(name):
    s = (SRC / "partials" / f"{name}.html").read_text()
    # root-relative asset paths so every page depth works
    s = re.sub(r'(src|poster|data-img)="(media|img)/', r'\1="/\2/', s)
    return s

BUSINESS = {
    "@type": "Restaurant",
    "@id": DOMAIN + "/#restaurant",
    "name": "Crabby George's Seafood Buffet",
    "alternateName": "Crabby George's Calabash Seafood Buffet",
    "url": DOMAIN + "/",
    "telephone": "+1-843-839-4044",
    "image": [DOMAIN + "/media/crab-pile.webp", DOMAIN + "/media/sign.webp"],
    "logo": DOMAIN + "/img/logo.png",
    "servesCuisine": ["Seafood", "Calabash seafood", "Buffet", "Steak"],
    "acceptsReservations": True,
    "hasMenu": DOMAIN + "/menu/",
    "address": {"@type": "PostalAddress", "streetAddress": "7904 N Kings Hwy", "addressLocality": "Myrtle Beach",
                "addressRegion": "SC", "postalCode": "29572", "addressCountry": "US"},
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "15:30", "closes": "21:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "14:00", "closes": "21:30"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "12:00", "closes": "22:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "12:00", "closes": "21:30"},
    ],
}

FAQ = [
    ("How much is the buffet?", "Buffet prices change by day and time. Call (843) 839-4044 or stop by for today's price. Coupons: $2 off anytime or $5 off before 4 PM on the adult buffet."),
    ("Do you have all-you-can-eat king crab legs?", "Yes. Crabby George's is the only restaurant in Myrtle Beach with all-you-can-eat Alaskan king crab legs. Add it to your adult buffet for an additional price and your server brings king crab legs to your table from the kitchen, as many rounds as you want. You can also order a single 1 lb plate from the menu for $79.99."),
    ("Are crab legs on the buffet?", "Yes. Alaskan snow crab legs are on the buffet line at no extra charge. All-you-can-eat Alaskan king crab legs are an add-on served by your server, and the 22 oz whole Maine lobster is ordered from the menu."),
    ("Can I order without the buffet?", "Yes. Seafood and steak entrées come with 2 sides, and you can order online for pickup at order.crabbygeorges.com."),
    ("Do you take reservations?", "Yes. Book online at reserve.crabbygeorges.com or call (843) 839-4044."),
    ("Is there a kids menu?", "Yes. Kids meals for ages 5 and under include chicken tenders, corn dogs, fried rice and corn on the cob."),
    ("What are your hours?", "Monday to Thursday 3:30 PM to 9 PM, Friday 2 PM to 9:30 PM, Saturday 12 PM to 10 PM and Sunday 12 PM to 9:30 PM. Holiday hours may differ."),
    ("Where are you located?", "7904 N Kings Hwy, Myrtle Beach, SC 29572, a few blocks from the oceanfront and minutes from Broadway at the Beach."),
    ("What is Calabash style seafood?", "Calabash style means seafood that is lightly breaded and quickly fried, a tradition from the Carolina coast. Our fried bar has Calabash style shrimp, oysters, scallops, flounder and more."),
    ("How many items are on the buffet?", "More than 120 items, including snow crab legs, raw oysters, shrimp, mussels, clams, prime rib, steaks, fried seafood, Southern sides and desserts."),
    ("Do you have outdoor seating?", "Yes, we have a patio for outdoor dining."),
    ("Can I use more than one coupon?", "No. Coupons are for the adult buffet only, cannot be combined with other discounts, and must be shown when you arrive."),
]

DRINKS = {
    "Cocktails": [
        ("Strawberry Daiquiri", "Light rum, strawberry syrup, lime juice"),
        ("Pirate's Punch", "Spiced rum, silver rum, coconut rum, pineapple juice, orange juice, fruit punch"),
        ("Piña Colada", "Light rum, pineapple juice, lime juice, cream of coconut"),
        ("Watermelon Martini", "Watermelon, vodka, lime juice, Cointreau"),
        ("Tequila Sunrise", "Tequila, orange juice, grenadine"),
        ("Long Island Iced Tea", "Gin, vodka, rum, triple sec, sour mix, cola"),
        ("Liquid Marijuana", "Coconut rum, spiced rum, blue curaçao, melon liqueur, pineapple juice, sweet & sour"),
        ("Blue Lagoon", "Vodka, blue curaçao, Sprite, sour mix"),
        ("Walk the Plank Margarita", "Gold tequila, margarita mix, topped with Grand Marnier"),
        ("Bahama Mama", "Silver rum, coconut rum, pineapple juice, orange juice, grenadine"),
    ],
    "Bottled Beer": [("Budweiser", ""), ("Bud Light", ""), ("Coors Light", ""), ("Miller Lite", ""), ("Michelob Ultra", ""), ("Yuengling", ""),
                     ("Corona", ""), ("Corona Premier", ""), ("Modelo", ""), ("Stella Artois", ""), ("Heineken", ""), ("Blue Moon", ""), ("Hard Seltzer", "")],
    "Wine": [("Cabernet", ""), ("Merlot", ""), ("Sweet Red", ""), ("Chardonnay", ""), ("Pinot Grigio", ""), ("Moscato", ""), ("White Zinfandel", "")],
    "Soft Drinks": [("Coke products", ""), ("Apple juice", ""), ("Orange juice", ""), ("Root beer", ""), ("Milk", ""), ("Chocolate milk", ""), ("Bottled water", "")],
}

NAV_FIX = [('href="#top"', 'href="/"'), ('href="#menu"', 'href="/menu/"'), ('href="#coupons"', 'href="/coupons-and-discounts/"'),
           ('href="#visit"', 'href="/location/"')]

def fix_links(s):
    for a, b in NAV_FIX:
        s = s.replace(a, b)
    return s

def faq_html(items, heading="Good to know", eyebrow="FAQ", tag="h2", more=False):
    qs = "\n".join(f"    <details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in items)
    link = '\n    <p style="margin-top:28px"><a class="btn line-btn" href="/faq/">More questions</a></p>' if more else ""
    return f'''<section class="light section faq" id="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">{eyebrow}</p><{tag} id="faq-h">{heading}</{tag}></div></div>
{qs}{link}
  </div>
</section>'''

def pagehead(h1, lede, eyebrow):
    return f'''<section class="pagehead">
  <div class="wrap"><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lede">{lede}</p></div>
</section>'''

def menu_schema():
    s = (SRC / "partials" / "menu.html").read_text()
    sections = []
    for sec in re.findall(r'<section class="msec"[^>]*>(.*?)</section>', s, re.S):
        name = re.search(r"<h3>(.*?)</h3>", sec).group(1)
        items = []
        for it in re.findall(r'<div class="item"[^>]*>(.*?)</div>\s*(?=<div class="item"|$)', sec + "<div class=\"item\"", re.S):
            h4 = re.search(r"<h4>(.*?)</h4>", it)
            pr = re.search(r'class="price">\$([\d.]+)', it)
            if not h4 or not pr:
                continue
            nm = html.unescape(re.sub(r"<[^>]+>", " ", h4.group(1))).replace("*", "")
            nm = re.sub(r"\s+", " ", nm).strip()
            ds = re.search(r"<p>(.*?)</p>", it)
            mi = {"@type": "MenuItem", "name": nm,
                  "offers": {"@type": "Offer", "price": pr.group(1), "priceCurrency": "USD"}}
            if ds:
                mi["description"] = html.unescape(ds.group(1))
            items.append(mi)
        if items:
            sections.append({"@type": "MenuSection", "name": html.unescape(name).capitalize(), "hasMenuItem": items})
    return {"@type": "Menu", "@id": DOMAIN + "/menu/#menu", "name": "Crabby George's Menu", "url": DOMAIN + "/menu/",
            "hasMenuSection": sections}

def drinks_html():
    out = []
    for cat, items in DRINKS.items():
        rows = "".join(
            f'<div class="item"><div class="name"><h4>{html.escape(n)}</h4></div>' + (f"<p>{html.escape(d)}</p>" if d else "") + "</div>"
            for n, d in items)
        out.append(f'<section class="msec"><h3>{cat}</h3>{rows}</section>')
    return f'''<section class="light section" aria-label="Drinks">
  <div class="wrap drinks">{"".join(out)}<p class="advisory">Must be 21 or older to order alcohol. Ask your server for today's beer, wine and cocktail prices.</p></div>
</section>'''

def form_page(name, fields, button):
    f = "\n".join(fields)
    return f'''<section class="light section">
  <div class="wrap narrow">
    <form name="{name}" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="company" class="form">
      <input type="hidden" name="form-name" value="{name}">
      <p class="hp"><label>Leave this empty <input name="company"></label></p>
{f}
      <button class="btn red" type="submit">{button}</button>
    </form>
  </div>
</section>'''

def field(label, name, kind="text", required=True, options=None):
    rq = " required" if required else ""
    star = " *" if required else ""
    if kind == "textarea":
        ctl = f'<textarea id="{name}" name="{name}" rows="5"{rq}></textarea>'
    elif kind == "select":
        ops = "".join(f"<option>{html.escape(o)}</option>" for o in options)
        ctl = f'<select id="{name}" name="{name}"{rq}><option value="">Choose one</option>{ops}</select>'
    else:
        ctl = f'<input id="{name}" name="{name}" type="{kind}"{rq}>'
    return f'      <label for="{name}">{label}{star}</label>\n      {ctl}'

FOOTER_NAV = '''<nav class="foot-nav" aria-label="Footer">
      <a href="/menu/">Menu &amp; Prices</a><a href="/all-you-can-eat-buffet/">Buffet</a><a href="/coupons-and-discounts/">Coupons</a><a href="/drinks/">Drinks</a>
      <a href="/location/">Hours &amp; Directions</a><a href="/faq/">FAQ</a><a href="/contact/">Contact</a><a href="/job-application/">Jobs</a>
      <a href="https://order.crabbygeorges.com">Order Online</a><a href="https://reserve.crabbygeorges.com">Reservations</a>
    </nav>'''

def footer():
    s = part("footer")
    s = re.sub(r'\s*<p class="proto">.*?</p>', "", s)
    return s.replace("</div>\n</footer>", f"  {FOOTER_NAV}\n  </div>\n</footer>")

def page(path, title, desc, body, schema=None, crumbs=None, peek=False, og="/media/og.jpg"):
    graph = [BUSINESS] if path in ("/", "/location/") else [{"@type": "Restaurant", "@id": DOMAIN + "/#restaurant", "name": BUSINESS["name"], "url": DOMAIN + "/"}]
    if schema:
        graph += schema if isinstance(schema, list) else [schema]
    if crumbs:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": crumbs, "item": DOMAIN + path}]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    canon = DOMAIN + path
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="restaurant">
<meta property="og:site_name" content="Crabby George's Seafood Buffet">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0E1B33">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/img/icon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900&family=Instrument+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={TODAY}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{fix_links(part("header"))}
<main id="top">
{body}
</main>
{footer()}
{'<div class="peek" id="peek" aria-hidden="true"><img alt="" src="/media/snow-crab-plate.webp"></div>' if peek else ''}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/site.js?v={TODAY}" defer></script>
</body>
</html>
'''
    dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    if path.endswith(".html"):
        dest = OUT / path.strip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc)
    return path

TEASER = '''<section class="light section" id="menu" aria-labelledby="menu-h">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">Menu &amp; prices</p><h2 id="menu-h">Favorites from the menu</h2></div><p>Not doing the buffet? Every entrée comes with 2 sides. Order at your table or <a href="https://order.crabbygeorges.com">online for pickup</a>.</p></div>
    <div class="teaser">
      <div class="item" data-img="/media/king-crab.webp"><div class="name"><h3 class="h4">King Crab Legs <span class="tag">1 lb</span> <span class="tag">or all you can eat</span></h3><span class="lead"></span></div><span class="price">$79.99</span></div>
      <div class="item" data-img="/img/maine-lobster.webp"><div class="name"><h3 class="h4">Maine Lobster Plate <span class="tag">22 oz</span></h3><span class="lead"></span></div><span class="price">$44.99</span></div>
      <div class="item"><div class="name"><h3 class="h4">Twin Lobster Tail</h3><span class="lead"></span></div><span class="price">$44.99</span></div>
      <div class="item" data-img="/media/snow-crab-plate.webp"><div class="name"><h3 class="h4">Snow Crab Legs <span class="tag">1 lb</span></h3><span class="lead"></span></div><span class="price">$32.99</span></div>
      <div class="item" data-img="/img/ny-strip.webp"><div class="name"><h3 class="h4">14 oz Ribeye or New York Strip</h3><span class="lead"></span></div><span class="price">$34.99</span></div>
    </div>
    <p style="margin-top:28px"><a class="btn red" href="/menu/">See the full menu &amp; prices</a></p>
  </div>
</section>'''

RES_FORM = '''<section class="light section">
  <div class="wrap narrow">
    <p class="res-msg warn" id="resNotice" hidden></p>
    <form id="resForm" class="form" novalidate>
      <p class="hp"><label>Leave this empty <input name="company" tabindex="-1" autocomplete="off"></label></p>
      <div class="res-row">
        <div><label for="resDate">Date *</label><input id="resDate" name="date" type="date" required></div>
        <div><label for="resTime">Time *</label><select id="resTime" name="time" required><option value="">Pick a date first</option></select></div>
        <div><label for="resParty">Guests *</label><select id="resParty" name="party" required></select></div>
      </div>
      <p class="res-hint" id="resDayNote"></p>
      <p class="res-hint" id="resLarge"></p>
      <label for="resName">Name *</label><input id="resName" name="name" type="text" autocomplete="name" required>
      <label for="resPhone">Phone *</label><input id="resPhone" name="phone" type="tel" autocomplete="tel" required>
      <label for="resEmail">Email (for your confirmation)</label><input id="resEmail" name="email" type="email" autocomplete="email">
      <div id="resExtra"></div>
      <label for="resNotes">Anything we should know?</label><textarea id="resNotes" name="notes" rows="3" placeholder="Birthday, high chair, wheelchair access…"></textarea>
      <button class="btn red" type="submit">Reserve my table</button>
    </form>
    <div class="res-msg" id="resMsg" role="status" hidden></div>
  </div>
</section>
<script src="/assets/reserve.js?v=''' + TODAY + '''" defer></script>'''

def build():
    css = (SRC / "site.css").read_text() + (SRC / "extra.css").read_text()
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "site.css").write_text(css)
    (OUT / "assets" / "site.js").write_text((SRC / "site.js").read_text())
    (OUT / "assets" / "reserve.js").write_text((SRC / "reserve.js").read_text())
    (OUT / "reservations").mkdir(parents=True, exist_ok=True)
    (OUT / "reservations" / "rules.json").write_text((SRC / "reservations.json").read_text())

    hero = fix_links(part("hero"))
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    pages = []
    pages.append(page("/", "Crabby George's Seafood Buffet | All You Can Eat Seafood in Myrtle Beach, SC",
        "Myrtle Beach's only all-you-can-eat Alaskan king crab legs, plus a 120+ item Calabash seafood buffet with snow crab, raw oysters and slow roast prime rib at 7904 N Kings Hwy, Myrtle Beach.",
        "\n".join([hero, part("band"), part("feature"), part("gallery"), part("buffet"), part("coupons"), TEASER, part("visit"), faq_html(FAQ[:6], more=True)]), peek=True))
    pages.append(page("/menu/", "Menu & Prices | Crabby George's Seafood Buffet, Myrtle Beach",
        "Full menu with prices: king crab legs $79.99, Maine lobster $44.99, snow crab legs $32.99, steaks, fried seafood, appetizers, soups and kids meals. Order online for pickup.",
        pagehead("Menu &amp; Prices", "Seafood and steak entrées with 2 sides, appetizers, soups and kids meals. Buffet prices change by day and time, so call (843) 839-4044 for today's buffet price.", "Crabby George's Seafood Buffet") + "\n" + part("menu").replace('<h2 id="menu-h">Order from the menu</h2>', '<h2 id="menu-h">Order from the menu</h2>'),
        schema=menu_schema(), crumbs="Menu & Prices", peek=True))
    pages.append(page("/all-you-can-eat-buffet/", "All You Can Eat Seafood Buffet in Myrtle Beach | Crabby George's",
        "120+ buffet items: Alaskan snow crab legs, raw oysters, steamed shrimp, mussels, clams, slow roast prime rib, Calabash style fried seafood, Southern sides and desserts.",
        pagehead("All You Can Eat Seafood Buffet", "More than 120 items on North Kings Highway in Myrtle Beach: snow crab legs, oysters, shrimp, prime rib and Calabash style fried seafood.", "The buffet") + "\n" + "\n".join([part("buffet"), part("feature"), part("gallery")]),
        crumbs="Seafood Buffet"))
    pages.append(page("/coupons-and-discounts/", "Seafood Buffet Coupons: $2 Off Anytime, $5 Off Before 4 PM | Crabby George's",
        "Save on the Crabby George's adult seafood buffet in Myrtle Beach: $2 off anytime or $5 off before 4 PM. Show the coupon on your phone when you arrive.",
        pagehead("Coupons &amp; Discounts", "Show these coupons on your phone at the host stand. Adult buffet only, one discount per guest.", "Save on the buffet") + "\n" + part("coupons"),
        crumbs="Coupons"))
    pages.append(page("/location/", "Hours & Directions | Crabby George's Seafood Buffet, 7904 N Kings Hwy, Myrtle Beach",
        "Crabby George's Seafood Buffet is at 7904 N Kings Hwy, Myrtle Beach, SC 29572. Open Mon–Thu 3:30–9 PM, Fri 2–9:30 PM, Sat 12–10 PM, Sun 12–9:30 PM. Call (843) 839-4044.",
        pagehead("Hours &amp; Directions", "A few blocks from the oceanfront on North Kings Highway, minutes from Broadway at the Beach.", "Visit us") + "\n" + part("visit"),
        crumbs="Hours & Directions"))
    pages.append(page("/drinks/", "Drinks & Cocktails | Crabby George's Seafood Buffet, Myrtle Beach",
        "Cocktails like the Pirate's Punch, Walk the Plank Margarita and Bahama Mama, plus bottled beer, wine and soft drinks at Crabby George's in Myrtle Beach.",
        pagehead("Drinks &amp; Cocktails", "Tropical cocktails, cold beer and wine to go with your crab legs.", "From the bar") + "\n" + drinks_html(),
        crumbs="Drinks"))
    pages.append(page("/faq/", "FAQ | Crabby George's Seafood Buffet, Myrtle Beach",
        "Answers about buffet prices, crab legs, reservations, kids meals, hours, coupons and Calabash style seafood at Crabby George's in Myrtle Beach.",
        faq_html(FAQ, heading="Frequently asked questions", tag="h1"), schema=faq_ld, crumbs="FAQ"))
    pages.append(page("/contact/", "Contact | Crabby George's Seafood Buffet, Myrtle Beach",
        "Call (843) 839-4044 or send us a message. Crabby George's Seafood Buffet, 7904 N Kings Hwy, Myrtle Beach, SC 29572.",
        pagehead("Contact us", "Call <span class=\"sel\">(843) 839-4044</span> or send a message below. For large groups and bus tours, please call ahead.", "We'd love to hear from you") + "\n" +
        form_page("contact", [field("Name", "name"), field("Email", "email", "email"), field("Phone", "phone", "tel", False),
                              field("Subject", "subject", "select", True, ["General question", "Large group or bus tour", "Feedback", "Other"]),
                              field("Message", "message", "textarea")], "Send message"),
        crumbs="Contact"))
    pages.append(page("/reservations/", "Reservations | Book a Table at Crabby George's Seafood Buffet, Myrtle Beach",
        "Reserve a table at Crabby George's Seafood Buffet, 7904 N Kings Hwy, Myrtle Beach. Pick a date, time and party size online, or call (843) 839-4044.",
        pagehead("Reserve a table", "Pick a date, time and party size. You will get a confirmation code right away.", "Reservations") + "\n" + RES_FORM,
        crumbs="Reservations"))
    pages.append(page("/job-application/", "Jobs | Work at Crabby George's Seafood Buffet, Myrtle Beach",
        "Apply to work at Crabby George's Seafood Buffet in Myrtle Beach: servers, hosts, bussers, kitchen and buffet staff.",
        pagehead("Join our crew", "Fill out the form and we'll get back to you.", "Jobs") + "\n" +
        form_page("job-application", [field("Full name", "name"), field("Phone", "phone", "tel"), field("Email", "email", "email", False),
                                      field("Position", "position", "select", True, ["Server", "Host", "Busser", "Kitchen / Cook", "Buffet attendant", "Dishwasher", "Bartender", "Any position"]),
                                      field("Availability (days and times)", "availability", "text", False),
                                      field("Experience", "experience", "textarea", False)], "Submit application"),
        crumbs="Jobs"))
    page("/thanks/", "Thank you | Crabby George's Seafood Buffet", "Thanks for your message.",
         pagehead("Thank you!", "We got your message and will get back to you soon.", "Sent") + '\n<section class="light section"><div class="wrap"><a class="btn red" href="/">Back to home</a></div></section>')
    page("/404.html", "Page not found | Crabby George's Seafood Buffet", "This page doesn't exist.",
         pagehead("Page not found", "That page moved or doesn't exist. Try the menu or our hours and directions.", "404") + '\n<section class="light section"><div class="wrap ctas"><a class="btn red" href="/menu/">Menu &amp; prices</a> <a class="btn line-btn" href="/location/">Hours &amp; directions</a></div></section>')

    # noindex the utility pages
    for p in ("thanks/index.html", "404.html"):
        f = OUT / p
        f.write_text(f.read_text().replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"', 1))

    urls = "".join(f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    bots = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Applebot", "Applebot-Extended"]
    (OUT / "robots.txt").write_text("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\nDisallow: /thanks/\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    (OUT / "llms.txt").write_text(f"""# Crabby George's Seafood Buffet

> All-you-can-eat Calabash seafood buffet with 120+ items at 7904 N Kings Hwy, Myrtle Beach, SC 29572. Phone (843) 839-4044.

- Hours: Mon–Thu 3:30–9 PM, Fri 2–9:30 PM, Sat 12–10 PM, Sun 12–9:30 PM
- Buffet price: changes by day and time; call (843) 839-4044. Coupons: $2 off anytime, $5 off before 4 PM (adult buffet).
- On the buffet: Alaskan snow crab legs, raw oysters, shrimp, mussels, clams, slow roast prime rib, Calabash style fried seafood
- All-you-can-eat Alaskan king crab legs: the only one in Myrtle Beach; add-on to the adult buffet for an additional price, served to the table by your server
- From the menu: King crab legs 1 lb $79.99, Maine lobster plate 22 oz $44.99, snow crab legs $32.99
- Online ordering: https://order.crabbygeorges.com  Reservations: https://reserve.crabbygeorges.com

## Pages
- [Menu & prices]({DOMAIN}/menu/)
- [Seafood buffet]({DOMAIN}/all-you-can-eat-buffet/)
- [Coupons]({DOMAIN}/coupons-and-discounts/)
- [Hours & directions]({DOMAIN}/location/)
- [FAQ]({DOMAIN}/faq/)
""")
    print("built", len(pages), "indexed pages")

if __name__ == "__main__":
    build()
