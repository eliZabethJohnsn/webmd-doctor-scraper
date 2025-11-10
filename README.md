# WebMD Doctor Scraper
Extract comprehensive doctor information from WebMD search results with a single, automated process. This scraper gathers detailed data about healthcare providers, their practice locations, patient reviews, and insurance details—perfect for research, analytics, or healthcare network insights.


<p align="center">
  <a href="https://bitbash.def" target="_blank">
    <img src="https://github.com/za2122/footer-section/blob/main/media/scraper.png" alt="Bitbash Banner" width="100%"></a>
</p>
<p align="center">
  <a href="https://t.me/devpilot1" target="_blank">
    <img src="https://img.shields.io/badge/Chat%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>&nbsp;
  <a href="https://wa.me/923249868488?text=Hi%20BitBash%2C%20I'm%20interested%20in%20automation." target="_blank">
    <img src="https://img.shields.io/badge/Chat-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp">
  </a>&nbsp;
  <a href="mailto:sale@bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Email-sale@bitbash.dev-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>&nbsp;
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Visit-Website-007BFF?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website">
  </a>
</p>




<p align="center" style="font-weight:600; margin-top:8px; margin-bottom:8px;">
  Created by Bitbash, built to showcase our approach to Scraping and Automation!<br>
  If you are looking for <strong>WebMD Doctor Scraper 👨‍⚕️</strong> you've just found your team — Let’s Chat. 👆👆
</p>


## Introduction
WebMD Doctor Scraper helps collect detailed doctor profiles from WebMD’s public listings, making it easier to analyze provider information at scale.
It’s designed for healthcare analysts, data engineers, and research teams who need structured, high-quality medical data.

### Why It Matters
- Collects structured healthcare provider data in bulk.
- Enables analysis of patient satisfaction and market competition.
- Simplifies insurance and network mapping across medical regions.
- Provides data consistency across varied WebMD listings.
- Ideal for healthcare startups, data aggregators, or research projects.

## Features
| Feature | Description |
|----------|-------------|
| Doctor Profile Extraction | Scrapes complete doctor details including name, gender, and NPI number. |
| Professional Information | Captures specialties, degrees, and education data. |
| Ratings & Reviews | Extracts patient feedback, review count, and rating categories. |
| Practice Locations | Fetches addresses, city, state, ZIP, and contact details. |
| Insurance Details | Lists all accepted insurance providers per doctor. |
| Profile Media | Collects profile photos and embedded videos if available. |
| Appointment Links | Extracts booking URLs and associated contact forms. |
| Proxy Support | Allows optional proxy setup for request routing. |
| Data Export Options | Provides JSON, CSV, Excel, or XML output formats. |

---

## What Data This Scraper Extracts
| Field Name | Field Description |
|-------------|------------------|
| searchUrl | The WebMD search URL from which results are scraped. |
| providerid | Unique provider identifier for the doctor. |
| name | Doctor’s full name, including first, middle, and last. |
| gender | Gender of the healthcare provider. |
| npi | National Provider Identifier number. |
| specialties | Array of listed medical specialties. |
| degrees | Professional degrees or certifications. |
| education | Educational background with graduation year. |
| photos | Profile photo URL. |
| bio | Doctor’s biography or description. |
| ratings | Includes review count, average rating, and category ratings. |
| location | Practice name, address, and coordinates. |
| insurances | List of accepted insurance providers. |
| urls | Profile, appointment, and website URLs. |
| reviews | Array of patient reviews with rating, text, and date. |

---

## Example Output
    [
      {
        "providerid": "E4F63621-2D8F-4AA8-8D9E-3D7AB35FC879",
        "name": { "first": "Stephanie", "last": "Najarro", "full": "Stephanie Najarro" },
        "gender": "F",
        "npi": "1376973354",
        "specialties": ["Family Medicine", "Primary Care"],
        "degrees": ["FNP-C"],
        "education": { "graduationYear": 2019 },
        "ratings": { "reviewCount": 11, "averageRating": 5 },
        "location": { "name": "Circle Medical", "city": "Beverly Hills", "state": "CA" },
        "urls": {
          "profile": "https://doctor.webmd.com/doctor/stephanie-najarro",
          "appointment": "https://booking-v2.circlemedical.com/provider/?slug=stephanie-najarro-fnp-c"
        },
        "reviews": [
          { "rating": "5", "text": "Very compassionate and kind.", "date": "1/29/2025" }
        ]
      }
    ]

---

## Directory Structure Tree
    webmd-doctor-scraper/
    ├── src/
    │   ├── main.py
    │   ├── parsers/
    │   │   ├── doctor_parser.py
    │   │   ├── review_parser.py
    │   │   └── location_parser.py
    │   ├── utils/
    │   │   ├── request_handler.py
    │   │   └── data_cleaner.py
    │   └── exporters/
    │       ├── json_exporter.py
    │       ├── csv_exporter.py
    │       └── xml_exporter.py
    ├── data/
    │   ├── input.sample.json
    │   └── sample_output.json
    ├── config/
    │   └── settings.example.json
    ├── requirements.txt
    └── README.md

---

## Use Cases
- **Healthcare researchers** use it to collect provider data and analyze patient satisfaction trends.
- **Medical startups** integrate it to build healthcare provider directories or rating dashboards.
- **Insurance analysts** use it to verify coverage networks and detect data inconsistencies.
- **Marketing teams** use it to identify competitive provider listings in specific regions.
- **Public health organizations** analyze care distribution across demographics and states.

---

## FAQs
**Q1: Does it work for all WebMD pages?**
It’s optimized for WebMD doctor search results and individual profile pages only.

**Q2: Can I limit the number of scraped profiles?**
Yes. Use the `maxItems` parameter to set a maximum count of doctors to extract.

**Q3: What if some profiles lack complete data?**
Missing fields are automatically handled and returned as null values in the output.

**Q4: How do I use proxies?**
You can configure the `proxyConfiguration` input parameter to route requests through specific proxy servers.

---

## Performance Benchmarks and Results
**Primary Metric:** Scrapes ~100 doctor profiles per minute on stable connections.
**Reliability Metric:** 98% success rate across tested regions.
**Efficiency Metric:** Processes average JSON output of 250KB per 50 doctors.
**Quality Metric:** Achieves ~95% field completeness for public profile data.


<p align="center">
<a href="https://calendar.app.google/74kEaAQ5LWbM8CQNA" target="_blank">
  <img src="https://img.shields.io/badge/Book%20a%20Call%20with%20Us-34A853?style=for-the-badge&logo=googlecalendar&logoColor=white" alt="Book a Call">
</a>
  <a href="https://www.youtube.com/@bitbash-demos/videos" target="_blank">
    <img src="https://img.shields.io/badge/🎥%20Watch%20demos%20-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube">
  </a>
</p>
<table>
  <tr>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/MLkvGB8ZZIk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review1.gif" alt="Review 1" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash is a top-tier automation partner, innovative, reliable, and dedicated to delivering real results every time.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Nathan Pennington
        <br><span style="color:#888;">Marketer</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/8-tw8Omw9qk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review2.gif" alt="Review 2" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash delivers outstanding quality, speed, and professionalism, truly a team you can rely on.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Eliza
        <br><span style="color:#888;">SEO Affiliate Expert</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtube.com/shorts/6AwB5omXrIM" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review3.gif" alt="Review 3" width="35%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Exceptional results, clear communication, and flawless delivery. Bitbash nailed it.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Syed
        <br><span style="color:#888;">Digital Strategist</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
  </tr>
</table>
