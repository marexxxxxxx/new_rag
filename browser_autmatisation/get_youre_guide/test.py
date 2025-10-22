from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, UndetectedAdapter, AdaptiveConfig
import asyncio
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
from time import sleep


browser_conf = BrowserConfig(
    enable_stealth=True,
    headless=True
)
brows = AdaptiveConfig(
    confidence_threshold=0.7,
    max_pages=20,
    top_k_links=2,
    min_gain_threshold=0.1
)

stealth_config = CrawlerRunConfig(
    user_agent_mode="random",
    simulate_user=True,
    override_navigator=True,
    magic=True,  # Auto-handle common bot detection patterns
    excluded_tags=["script", "style", "nav", "footer", "header"],
    capture_network_requests=False,
    capture_console_messages=False,
)



async def get_youre_dat(link):
    async with AsyncWebCrawler(config=browser_conf) as crawl:
        result = await crawl.arun(url=link)
    return result.markdown
#erg = asyncio.run(get_youre_dat("https://www.getyourguide.com/frankfurt-l21/frankfurt-must-see-attractions-walking-tour-with-a-guide-t633639/?ranking_uuid=8937123e-7948-45f5-a838-9dcc849516fe"))






test = """
[Skip to main content](https://www.getyourguide.com/frankfurt-l21/frankfurt-must-see-attractions-walking-tour-with-a-guide-t633639/?ranking_uuid=8937123e-7948-45f5-a838-9dcc849516fe#main-content-wrapper)
[![Get Your Guide logo](data:image/svg+xml,%3Csvg%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20382%20302'%20width='56'%20height='64'%3E%3Cpath%20d='M98.273%20125.538c-5.904%200-10.574%204.553-10.574%2010.574s4.67%2010.574%2010.574%2010.574%2010.574-4.553%2010.574-10.574-4.67-10.574-10.574-10.574zm60.37-51.987h-37.392V55.594h33.329V37.637h-33.329V19.925h36.775V1.84h-56.944v89.795h57.561V73.551zm-41.668%2054.2c5.904%200%2010.574-4.553%2010.574-10.574s-4.67-10.574-10.574-10.574-10.575%204.553-10.575%2010.574%204.671%2010.574%2010.575%2010.574zM38.498%2093.475c13.042%200%2024.478-6.638%2031.243-16.85v15.01h17.713V41.701H39.977v17.222h19.925c-1.84%209.223-9.968%2016.362-19.808%2016.362-10.947%200-19.808-8.862-19.808-21.776V40.222c0-12.67%209.468-22.02%2022.754-22.02%2010.33%200%2019.553%205.659%2022.627%2013.903l18.702-6.52C79.199%209.84%2062.476%200%2043.168%200%2018.818%200%20.606%2016.361.606%2040.222v13.287c.01%2022.988%2016.978%2039.966%2037.892%2039.966zm172.909-66.401h-19.903v28.69h19.903v-28.69zM235.396%201.84h-68.147v18.085h68.147V1.84zM33.829%20195.887h20.17v-34.063l33.817-55.721H65.061l-21.275%2036.775-21.032-36.775H0l33.829%2055.966v33.818zM211.407%2062.923h-19.903v28.68h19.903v-28.68zM364.87%20195.887l-24.478-34.318c11.936-3.692%2020.297-14.149%2020.297-26.935%200-16.234-13.403-28.542-30.382-28.542h-11.808v18.201h11.074c5.904%200%2010.457%204.671%2010.457%2010.819%200%206.149-4.553%2010.83-10.457%2010.83h-11.074v17.222l21.893%2032.723h24.478zm-99.964%2014.35h-29.648v89.912h29.648c27.796%200%2047.477-19.063%2047.477-44.892%200-25.829-19.681-45.02-47.477-45.02zm1.595%2071.827h-11.074v-53.753h11.074c15.01%200%2025.212%2011.563%2025.212%2026.935%200%2015.372-10.202%2026.818-25.212%2026.818zm78.104-17.956h33.328v-17.957h-33.328v-17.712h36.775v-18.074h-56.945v89.784h57.562v-18.085h-37.392v-17.956zm-32.137-98.582-10.426-14.776%2010.287-14.946-10.425-14.766%2010.298-14.935-20.797.01-10.298%2015.095%2010.436%2014.777-10.298%2014.946%2010.436%2014.765-10.297%2014.957%2011.074%2015.372h21.02l-11.308-15.542%2010.298-14.957zm-45.924-4.564v-54.859h-20.053v55.232c0%2010.329-7.383%2017.957-17.467%2017.957-10.085%200-17.468-7.628-17.468-17.957v-55.232h-20.052v54.859c0%2021.159%2015.872%2036.776%2037.52%2036.776%2021.648%200%2037.52-15.627%2037.52-36.776zM156.452%20265.586c0%2010.33-7.383%2017.957-17.468%2017.957-10.084%200-17.467-7.627-17.467-17.957v-55.232h-20.053v54.86c0%2021.159%2015.872%2036.775%2037.52%2036.775%2021.649%200%2037.52-15.616%2037.52-36.775v-54.86h-20.052v55.232zm-116.475%201.851h19.925c-1.84%209.223-9.968%2016.361-19.808%2016.361-10.946%200-19.807-8.861-19.807-21.775v-13.287c0-12.67%209.467-22.021%2022.754-22.021%2010.33%200%2019.553%205.66%2022.627%2013.904l18.701-6.521c-5.17-15.744-21.892-25.584-41.2-25.584-24.35%200-42.563%2016.361-42.563%2040.222v13.287C.606%20285.022%2017.584%20302%2038.488%20302c13.042%200%2024.478-6.638%2031.244-16.85v15.01h17.712v-49.935H39.977v17.212z'%20fill='%23F53'/%3E%3Cpath%20d='M132.102%20104.252v18.946c14.765%200%2026.446%2012.053%2026.446%2027.797s-11.681%2027.797-26.446%2027.797c-14.755%200-26.446-12.053-26.446-27.797h-20.67c0%2026.201%2020.915%2046.743%2047.105%2046.743%2026.201%200%2047.105-20.542%2047.105-46.743%200-26.202-20.893-46.743-47.094-46.743zm82.497%20148.377c2.978-2.691%207.968-7.191%207.968-15.435%200-8.245-4.99-12.744-7.968-15.436a9.787%209.787%200%200%200-.373-.33c-1.489-1.563-1.744-3.808-1.776-4.872v-6.319h-20.201v8.404h.01c0%20.107-.01.202-.01.309%200%208.244%204.989%2012.744%207.967%2015.435%202.139%201.936%202.139%202.032%202.139%202.809%200%20.776%200%20.872-2.139%202.808-2.861%202.585-7.574%206.862-7.925%2014.532h-.021c0%20.148-.021.287-.021.425%200%20.085.01.16.01.234%200%20.085-.01.16-.01.234%200%20.149.01.287.021.426h.021c.351%207.67%205.064%2011.946%207.925%2014.531%202.139%201.936%202.139%202.032%202.139%202.808%200%20.777%200%20.873-2.139%202.809-2.978%202.691-7.967%207.191-7.967%2015.435%200%20.107%200%20.213.01.309h-.01v8.404h20.201v-6.319c.032-1.053.287-3.308%201.776-4.872.117-.107.234-.213.373-.33%202.978-2.691%207.968-7.191%207.968-15.436%200-8.244-4.99-12.744-7.968-15.435-1.904-1.713-2.117-1.989-2.138-2.564.021-.574.234-.851%202.138-2.564z'%20fill='%23F53'/%3E%3C/svg%3E) ](https://www.getyourguide.com/ "GetYourGuide")
Anytime
Search
  * [Become a supplier](https://supplier.getyourguide.com/?utm_source=inbound&utm_medium=b2c_website_supply&utm_campaign=navbar_adp_versionb "Become a supplier")
  *   * [Wishlist](https://www.getyourguide.com/wishlists/ "Wishlist")
  * [ Cart](https://www.getyourguide.com/cart/ "Cart")
  * EN/EUR €
  * [ Profile](https://www.getyourguide.com/frankfurt-l21/frankfurt-must-see-attractions-walking-tour-with-a-guide-t633639/?ranking_uuid=8937123e-7948-45f5-a838-9dcc849516fe "Profile")


  * [Explore Frankfurt](https://www.getyourguide.com/frankfurt-l21/)
  * Places to see
  * Things to do


## Frankfurt: Must-See Attractions Walking Tour with a Guide
Check availability
  * Overview
  * Details
  * Highlights
  * Itinerary
  * Meeting point
  * Reviews


# Frankfurt: Must-See Attractions Walking Tour with a Guide
4.6 out of 5 stars
4.6
[36 reviews](https://www.getyourguide.com/#adp-reviews-info-header-title)
•Activity provider: Guydeez Travel SL 
Add to wishlist
Share
![](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=450,height=450,dpr=2/tour_img/07b49689045f67ec89b734ea673f22c7ad1a10f9bc2b4fa2bb224ea9b72ade37.jpg)
![](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=450,height=450,dpr=2/tour_img/e742874ab93cbd473771eaf3c7d31884123af7c307454f5d63b31b14a5e50fa7.jpg)
![](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=450,height=450,dpr=2/tour_img/fd108d026e659b9022076ec13656e8cf0eb3f503b91d99dc957c8eb0637eb3dd.jpg)
![](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=450,height=450,dpr=2/tour_img/1ef848b0c8031d8dae2e9f942db6681b25aae1afe343d68a93bfb1c0dab325a0.jpg)
![](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=450,height=450,dpr=2/tour_img/9c4968f306cd1a64422e03bbcf8f90f2ead873e408bff1701b92a70448c67cea.jpg)
+1
![image n.1 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=620,height=400,dpr=1/tour_img/07b49689045f67ec89b734ea673f22c7ad1a10f9bc2b4fa2bb224ea9b72ade37.jpg)
![image n.2 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=300,height=400,dpr=1/tour_img/e742874ab93cbd473771eaf3c7d31884123af7c307454f5d63b31b14a5e50fa7.jpg)
![image n.3 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=300,height=195,dpr=1/tour_img/fd108d026e659b9022076ec13656e8cf0eb3f503b91d99dc957c8eb0637eb3dd.jpg)
![image n.4 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=300,height=195,dpr=1/tour_img/1ef848b0c8031d8dae2e9f942db6681b25aae1afe343d68a93bfb1c0dab325a0.jpg)
![image n.1 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=contain,gravity=auto,quality=60,width=1440,height=650,dpr=1/tour_img/07b49689045f67ec89b734ea673f22c7ad1a10f9bc2b4fa2bb224ea9b72ade37.jpg)
![image n.2 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=contain,gravity=auto,quality=60,width=1440,height=650,dpr=1/tour_img/e742874ab93cbd473771eaf3c7d31884123af7c307454f5d63b31b14a5e50fa7.jpg)
![image n.3 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=contain,gravity=auto,quality=60,width=1440,height=650,dpr=1/tour_img/fd108d026e659b9022076ec13656e8cf0eb3f503b91d99dc957c8eb0637eb3dd.jpg)
![image n.4 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=contain,gravity=auto,quality=60,width=1440,height=650,dpr=1/tour_img/1ef848b0c8031d8dae2e9f942db6681b25aae1afe343d68a93bfb1c0dab325a0.jpg)
![image n.5 of Frankfurt: Must-See Attractions Walking Tour with a Guide activity in Frankfurt, uploaded by supplier](https://cdn.getyourguide.com/image/format=auto,fit=contain,gravity=auto,quality=60,width=1440,height=650,dpr=1/tour_img/9c4968f306cd1a64422e03bbcf8f90f2ead873e408bff1701b92a70448c67cea.jpg)
0 / 0
Check availability
Embark on a captivating private walking tour of Frankfurt with a knowledgeable guide who will lead you through the city's rich history and iconic landmarks.
## About this activity Free cancellation 
     Cancel up to 24 hours in advance for a full refund Reserve now & pay later 
     Keep your travel plans flexible — book your spot and pay nothing today. Duration 2 hours 
     Usually available in the morning, afternoon, and evening. Check availability to see starting times Live tour guide 
     English, Spanish, German Wheelchair accessible 
Private group available 

## Highlighted reviews from other travelers
5
5 out of 5 stars
C
Crystal – United StatesSeptember 28, 2025 – Verified booking
The tour guide was very knowledgeable with history! We learned so much about Frankfurt. Very nice!
5
5 out of 5 stars
D
Dawn – NetherlandsSeptember 17, 2025 – Verified booking
Heidrun was absolutely amazing! She was so knowledgeable. Plus she had relationships with various places that got us after hours and/or special access. It was the best tour!!
Read more
See more reviews
##  Select participants, date, and language
Participants 
Select date 
Language 
Check availability
## Itinerary
  * ### Starting location:
Fountain of Justice
  * ### Römer, Frankfurt
Guided tour
  * ### Frankfurt Cathedral
Guided tour
  * ### Iron Bridge, Frankfurt
Guided tour
  * ### Goethe House
Guided tour
  * ### Old Opera House, Frankfurt
Guided tour
  * ### Arrive back at:
Fountain of Justice


Main stop
For reference only. Itineraries are subject to change.
## Highlights
  * Get to know Frankfurt through the eyes of a knowledgeable local Guide
  * See the main tourist sights you want to see as well as discovering areas, venues
  * Private and customizable walking tour
  * Benefit from your guide’s familiarity with the area that interests you
  * Get lots of valuable advice from your guide about other things to do in the city


## Full description
Begin your private walking tour at the fountain of justice, where you'll meet your guide and start your journey through Frankfurt's history. Explore the Römer, a collection of nine medieval houses that have served as the city hall for over 600 years. Learn about its significance and its role in hosting weddings and civil registrations.  
Next, visit the St. Bartholomew Cathedral, the largest Roman Gothic church in Frankfurt. Admire its impressive tower, organ, and vaulted ceilings, and learn about its importance as a symbol of unity during the Empire era. Cross the Iron Footbridge, or Eiserner Steg, a historic iron footbridge that offers stunning views of the city skyline.  
Pass by the Städel Museum, home to a remarkable collection of art, and the Eurotower, a skyscraper that was once the seat of the European Central Bank. Visit the Goethe House, the birthplace and childhood home of Johann Wolfgang von Goethe, and explore his early works.  
Continue your tour to St. Paul's Church, a significant political symbol in Germany and the seat of the first Frankfurt Parliament in 1848. Walk through the Kleinmarkthalle, a bustling market offering a variety of fresh foods and delicacies.  
Conclude your tour at the Alte Oper, the Old Opera House, which has hosted many great operas and concerts. Admire its grand architecture and the Opera Square in front of it, reflecting the city's rich artistic heritage.
## Includes
Private and exclusive tour, there won't be anyone else in your group.
Customization of the tour
Walking tour and public transport (except if you select one of the option)
Help from our team to book the tickets for the desired visits
Food or drinks
Tips (optional)
## Meeting point
Meet your guide near the Foundation of Justice
  * [Open in Google Maps](https://maps.google.com/?q=@50.110435485839844,8.682154655456543)


From~~~~
€45per person
Check availability
Reserve now & pay later to book your spot and pay nothing today. Read more
## You might also like…
Customer reviews
Customer photos
![](https://cdn.getyourguide.com/img/review/b8081bbf0e0d52fdb2ea254421b94f199020940433e40847ecf44bce663766cd.jpg/98.jpg)
![](https://cdn.getyourguide.com/img/review/5372ec9f0075b603f41116f0ab301fac03efbd6acba6959365fc735c69faa500.jpg/97.jpg)
![](https://cdn.getyourguide.com/img/review/7246427a91c2afa2fa7408c3bd949bae4ae310d72fba03434877184b1b9dfed9.jpg/97.jpg)
![](https://cdn.getyourguide.com/img/review/2a8c94ed0e71b94d5645c3d38ac154f0cb9ba0322ff3653152c1c0cd0c7e05f4.jpg/97.jpg)
![](https://cdn.getyourguide.com/img/review/acf20c060c68994c883458f494a69a956e2d9c26aa2e377a6b47fdd2ca730c2c.jpg/97.jpg)
+16
Overall rating
4.6/5
4.611111 out of 5 stars
based on 36 reviews
Review summary
  * Guide4.8/5
  * Value for money4.5/5


Sort by:
Recommended
Recommended
Most recent
Oldest
Highest rated
Lowest rated
Filter
5
5 out of 5 stars
C
Crystal – United StatesSeptember 28, 2025 – Verified booking
The tour guide was very knowledgeable with history! We learned so much about Frankfurt. Very nice!
5
5 out of 5 stars
D
Dawn – NetherlandsSeptember 17, 2025 – Verified booking
Heidrun was absolutely amazing! She was so knowledgeable. Plus she had relationships with various places that got us after hours and/or special access. It was the best tour!!
5
5 out of 5 stars
C
Cheryl – AustraliaSeptember 15, 2025 – Verified booking
Florin was brilliant and was very knowledgeable. would definitely recommend this tour to everyone.
5
5 out of 5 stars
N
Nick – United StatesSeptember 14, 2025 – Verified booking
It went really well, she spoke really good English
5
5 out of 5 stars
L
Lyn – Saudi ArabiaApril 2, 2025 – Verified booking
Chris our private guide was amazing. Very knowledgeable and tailored our walk to the things we were interested in, architecture, history, local culture 😀. Would highly recommend Chris & would use him again when we come back to Frankfurt.
5
5 out of 5 stars
S
Somna – IndiaMarch 30, 2025 – Verified booking
We had an absolutely fantastic private walking tour of Frankfurt’s Old City guided by the incredibly knowledgeable Annibal. The tour was meant to be two hours, but since both he and we had spare time, he generously spent four hours with us—including joining us for a delicious lunch. His deep understanding of German history, especially Frankfurt’s unique past, brought the city to life in such an engaging way. From hidden gems to iconic landmarks, every stop was insightful and memorable. What truly stood out was Annibal’s eye for photography—his knowledge of composition and how to frame the subject with the background was impressive. At every point, he would take our phone, position us perfectly, and capture beautiful photos of us. A delightful bonus was our visit to an Afghan restaurant, where we enjoyed some of the best kebabs we’ve ever had. Annibal’s warmth, passion for history, and thoughtful personal touches made this tour a highlight of our trip. Highly recommended.
5
5 out of 5 stars
J
Jordan – United StatesMarch 18, 2025 – Verified booking
My tour guide Chris did an outstanding job of showing me around Frankfurt. There was so much to see and experience, and while there wasn’t nearly enough time to get to everything, I feel like I was able to gain a much better appreciation of Frankfurt. I’m definitely looking forward to coming back and being able to venture out even more.
5
5 out of 5 stars
C
Carmen – HondurasJanuary 13, 2025 – Verified booking
Our tour with Annibal was great fun. He was highly knowledgable and funny as well. He was very thorough in highlighting the best Frankfurt has to offer and kindly took pictures of us throughout. He went above and beyond for our comfort and wellbeing. I would one hundred percent recommend this activity.
5
5 out of 5 stars
A
ayona – PortugalOctober 17, 2024 – Verified booking
I had a delay, but it was good. I could not see everything i wanted but it was good still. Florian was super pacient and a very good company.
5
5 out of 5 stars
H
Hui – United StatesOctober 13, 2024 – Verified booking
Chris is very knowledgeable and professional tour guide. We enjoyed learning from him during this trip and showed us around all the different historical spots in the city.
See more reviews
Check availability
Product ID: 633639 

Activity provider:
    [Guydeez Travel SL ](https://www.getyourguide.com/guydeez-travel-sl-s368591/)
  * [Germany](https://www.getyourguide.com/germany-l169009/)
  * [Hessen](https://www.getyourguide.com/hessen-l1285/)
  * [Things to do in Frankfurt](https://www.getyourguide.com/frankfurt-l21/ttd/)
  * [Tours in Frankfurt](https://www.getyourguide.com/frankfurt-l21/)
  * [European Central Bank](https://www.getyourguide.com/european-central-bank-l12922/)


  * [Germany](https://www.getyourguide.com/germany-l169009/)
  * [Hessen](https://www.getyourguide.com/hessen-l1285/)
  * [Things to do in Frankfurt](https://www.getyourguide.com/frankfurt-l21/ttd/)
  * [Tours in Frankfurt](https://www.getyourguide.com/frankfurt-l21/)
  * [European Central Bank](https://www.getyourguide.com/european-central-bank-l12922/)


Language
Currency
Mobile
![Get it on Google Play](https://cdn.getyourguide.com/tf/assets/static/badges/google-play-badge-en-us.svg)![Download on the App Store](https://cdn.getyourguide.com/tf/assets/static/badges/app-store-badge-en-us.svg)
Support
  * [Contact](https://www.getyourguide.com/contact/?referrer_source=site_footer)
  * [Legal Notice](https://www.getyourguide.com/c/legal/)
  * [Privacy Policy](https://www.getyourguide.com/c/privacy-policy/)
  * [Cookies and Marketing Preferences](https://www.getyourguide.com/frankfurt-l21/frankfurt-must-see-attractions-walking-tour-with-a-guide-t633639/?ranking_uuid=8937123e-7948-45f5-a838-9dcc849516fe)
  * [General Terms and Conditions](https://www.getyourguide.com/c/general-terms-and-conditions/)
  * [Information according to the Digital Services Act](https://www.getyourguide.com/c/dsa/)
  * [Sitemap](https://www.getyourguide.com/destinations/)
  * [Do not Sell or Share my Personal Information](https://www.getyourguide.com/c/tc-ccpa/)


Company
  * [About Us](https://www.getyourguide.com/about/)
  * [Careers](https://careers.getyourguide.com/)
  * [Blog](https://inside.getyourguide.com/)
  * [Press](https://press.getyourguide.com/)
  * [Gift Cards](https://www.getyourguide.com/coupon/)
  * [Explorer](https://www.getyourguide.com/explorer/)


Work With Us
  * [As a Supply Partner](https://supplier.getyourguide.com/?utm_source=inbound&utm_medium=b2c_website_supply&utm_campaign=footer_link_adp)
  * [As a Content Creator](https://partner.getyourguide.com/en-us/content-creators/?partner_id=VPFQWBY&cmp=gyg_footer_creator)
  * [As an Affiliate Partner](https://partner.getyourguide.com/en-us/content-creators/?partner_id=VPFQWBY&cmp=gyg_footer_affiliate)


Ways You Can Pay
![Paypal](https://cdn.getyourguide.com/tf/assets/static/payment-methods/paypal_border.svg)
![Mastercard](https://cdn.getyourguide.com/tf/assets/static/payment-methods/mastercard.svg)
![Visa](https://cdn.getyourguide.com/tf/assets/static/payment-methods/visa.svg)
![Maestro](https://cdn.getyourguide.com/tf/assets/static/payment-methods/maestro.svg)
![American Express](https://cdn.getyourguide.com/tf/assets/static/payment-methods/amex.svg)
![Jcb](https://cdn.getyourguide.com/tf/assets/static/payment-methods/jcb.svg)
![Discover](https://cdn.getyourguide.com/tf/assets/static/payment-methods/discover.svg)
![Klarna](https://cdn.getyourguide.com/tf/assets/static/payment-methods/klarna.svg)
![Google Pay](https://cdn.getyourguide.com/tf/assets/static/payment-methods/googlepay.svg)
![Apple Pay](https://cdn.getyourguide.com/tf/assets/static/payment-methods/applepay.svg)
![Ideal](https://cdn.getyourguide.com/tf/assets/static/payment-methods/ideal.svg)
![Bancontact](https://cdn.getyourguide.com/tf/assets/static/payment-methods/bancontact.svg)
© 2008 – 2025 GetYourGuide. Made in Zurich & Berlin. 
[ Facebook ](https://www.facebook.com/GetYourGuide "Facebook")[ Instagram ](https://www.instagram.com/getyourguide/ "Instagram")[ Twitter ](https://www.twitter.com/GetYourGuide "Twitter")[ Pinterest ](https://pinterest.com/getyourguide/ "Pinterest")[ LinkedIn ](https://www.linkedin.com/company/getyourguide-ag/ "LinkedIn")
"""

import re



testa = re.findall(r"^(## .*?)(?=\n^##|\Z)", test, re.MULTILINE | re.DOTALL)

keywords = ["## Itinerary","## Highlights", "## Meeting point","## Full description","## Includes"]

action_map = {
    # Spezifische Aktionen
    "## Highlights": lambda: print("High: Aktion für Highlights"),
    "## Meeting point": lambda: print("Meet: Aktion für Meeting Point"),
    
    # Standard-Aktionen für die restlichen Keywords
    "## Itinerary": lambda: print("-> Aktion für Itinerary (Standard)"),
    "## Full description": lambda: print("-> Aktion für Full description (Standard)"),
    "## Includes": lambda: print("-> Aktion für Includes (Standard)")
    
    # Alternativ, wenn sie nichts tun sollen:
    # "## Itinerary": default_action,
    # "## Full description": default_action,
    # "## Includes": default_action,
}

from state import highlights
from pydantic import BaseModel
link = '![](https://cdn.getyourguide.com/image/format=auto,fit=crop,gravity=auto,quality=60,width=270,height=180/tour_img/6d72bc1d50214d19.jpeg)\n'
if ".jpeg" in link:
    print("wuhuuuuuuuuuuuuuuu")