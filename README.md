# Pawpals
## Participants
- Dang Khoa Nguyen
- Nhat Trang Linh Le
- Ngoc Han
- Quynh Vy
- Anh Khoa
- Shaurya Jain

## Technology Uses
- Figma
- Google Doc
- HTML, CSS
- Boostrap
- Python (Flask, Flask Mail, numpy, os, mysql.connector, Boto3, dotenv)
- CNN Models (Tensorflow)
- Jinja

## [About our product]()

Inspiration
Being part of a community of devoted animal lovers, we deeply understand the heartbreak of losing a beloved pet. We’ve witnessed firsthand the pain, anxiety, and helplessness that come with searching for a missing furry friend. While miracles don’t always happen, we believe in creating solutions that can bring pet owners and their lost companions one step closer to reunion. This passion is what drives us to develop PawPals.

We recognised that pet owners have multiple ways to search for their lost pets online, whether through social media, community groups, or pet rescue organisations. While these methods can be helpful, they often rely on luck and visibility. That’s why we’re introducing a website that harnesses the power of AI to make the search smarter and more efficient. By using AI-generated image recognition, our platform compares lost and found pet photos, assigns similarity scores, and suggests potential matches, helping to bridge the gap between worried owners and their missing pets.

With this website, we hope to give more pets a fighting chance to be rescued and reunited with their families. Our goal is not just to provide a tool but to create moments of joy, relief, and hope. We want to make miracles happen - one paw at a time.

## Challenge we ran into
we’re facing several challenges in developing PawPals. One of our main concerns is ensuring that our users receive timely email notifications at every stage of the reporting and searching process. However, setting up and integrating the email system into our website has been difficult for us.
Additionally, we are struggling with deploying our database using AWS, as we lack experience in cloud-based infrastructure. Managing and maintaining a secure and efficient database is essential for our platform, but setting up and configuring AWS services has proven to be a challenge.
Another major hurdle is integrating advanced technologies like TensorFlow into our web application. Since our platform relies on AI-powered image matching, properly implementing TensorFlow and its machine learning models is crucial. However, integrating these components seamlessly into the website has been complex due to our limited technical expertise.
Despite these challenges, we are committed to overcoming them and ensuring that PawPals functions smoothly to help reunite lost pets with their owners. We are actively seeking guidance and support to address these technical difficulties and improve our platform’s efficiency.

Accomplishment we’re proud of
The biggest achievement for us is stepping out of our safe zone and tackling something completely new. Despite having little experience, we pushed through challenges together, constantly encouraging one another to keep going even when things didn’t go as planned. We’re especially proud that PawPals turned out to be 80% of what we originally imagined - a lost and found website with a cute and lovable design to its useful core functionalities. More importantly, we successfully created a platform that conveys trust and warmth to users.
Beyond that, we’re incredibly proud that PawPals actually works! While it may not be 100% complete, knowing that we built something genuinely useful for pet lovers and those desperately searching for their lost companions is incredibly fulfilling. The journey wasn’t easy, but we embraced the learning process, not just within our own areas of expertise, but from each other as well, specially when the coders started to bombard the business kids’ ears with all these front-end and back-end stuff =))
Initially, we expected UniHack to be a draining experience, a nonstop focus competition. However, reality turned out to be much more than that. Of course, there were hours of intense concentration and heated debates over ideas, but in between, we found moments of laughter, deep conversations, and sharing KFC as the clock ticked down. Looking back, we’re proud that we didn’t just power through a high-pressure competition, we made memories, took control of every step, and turned this journey into something truly unforgettable in our youth.

## What we learnt

Turning Passion into Reality: Many of us have always dreamed of creating something meaningful for society, using the skills and knowledge we’ve gained. Our journey began by identifying a real-world problem - a challenge that resonated with our personal experiences, our ‘pain point’. And unlike any other traditional university projects, UniHack pushed us to connect multiple disciplines, from IT and design to business strategy, making it feel like we were running a small startup rather than just completing an assignment for higher grade.

This experience ignited our passion for innovation, driving us to work as a team with the shared goal of building something truly impactful. It’s this passion that has kept us motivated, pushing us forward to bring PawPals to life.

Stepping out of the Safe Zone: Entering UniHack 2025, we were uncertain whether our current skills would be enough to accomplish everything we envisioned. Doubts filled our minds, but we chose to step out of our comfort zones, embrace new challenges, and take on something beyond what we had ever done before. Despite being first-timers, we pushed ourselves to apply everything we’ve learned as university students and give it our all.

Of course, there were obstacles, things we hadn’t learned yet, concepts that seemed beyond our reach, and challenges that required hand-on experience even before taking a related course. We had to rely on self-learning, researching online, and figuring things out within a tight timeframe. While the outcome may not be flawless or exactly as we envisioned, it represents our efforts, growth, and determination. To us, this journey wasn’t just about the competition, it was a meaningful step in turning our passion into reality.

Embracing Differences & Teamwork: Coming from diverse backgrounds, majors, and personalities, each of us brought unique strengths and weaknesses to the team. At first, our vision was so unclear, we weren’t sure where to begin or what to expect. We barely knew each other, but as we talked, worked, and even shared meals together, everything started to fall into place.

What we didn’t anticipate was how much we would enjoy the process, collaborating, brainstorming, and sharing personal stories. Through this journey, we discovered that teamwork isn’t just about working together, but it’s all about communicating, understanding, and appreciating our differences.

## What’s next for PawPals

We're always looking for ways to improve PawPals and make it even more effective in reuniting lost pets with their families. Our next steps include introducing a dashboard that displays the latest found pets and those in urgent need of help. We also plan to keep the website updated with real-time success stories, reassuring users that PawPals is a trusted and effective platform.
To spread hope and inspire more people to take action, we aim to feature videos and interviews with pet owners and rescuers who have experienced the joy of reuniting lost pets. These heartwarming stories will help build a stronger, more connected pet-loving community.
To further assist users and help PawPals grows globally, we recognise the importance of inclusivity. We plan to implement multi-language support, ensuring that pet owners from different backgrounds can easily navigate and use the platform. Our goal is to create a universal space where every lost pet has a chance to be found, no matter where they are.
At the heart of PawPals, we believe that every paw deserves a way home. As we continue to innovate and expand, our mission remains the same, to bring pets and their families back together, one reunion at a time.

## How we built it
Our project contains frontend, and backend components. The breakdown for each component is as follows:

Backend CNN Model - We employed a Convolutional Neural Network (CNN) for object detection, enabling accurate identification and similarity calculations between lost and found paws. 
Flask - Flask served as the backbone of our backend infrastructure, facilitating HTTP request handling, routing, and communication with the frontend. 
AWS S3 - AWS S3 was utilised for database management and secure cloud storage of images.
The Request library was utilised for making HTTP requests to external APIs, enabling communication with third-party services and data retrieval. 
Flask mail -  We implement Flask Mail for automated notifications and updates, ensuring timely alerts for users. 
Jinja language -The Jinja templating engine helps us dynamically display database-driven content on the website.

Frontend HTML,CSS were chosen for frontend development. We have used Boostrap framework which provides a robust and efficient framework for building interactive user interfaces. In additional, our frontend also created the new style to make user interface look fanstastic. The frontend displays the paw images, with having high similarities rate, to the client so they can have more opportunities to identify their paw. 

## How to use Pawpals website
### Finding a paw
1. Click to the missing paw, this link will direct you to the form.
2. Fill in the information about the paw, and submit it.
3. Wait for seconds, some watches will show you. Otherwise, it display a message to announce you wait.
   
### Found a paw
1. Click to the paw found, this link will direct you to the form.
2. Fill in the information about the paw, and submit it.
3. After submiting, a thankful message will be displayed.

### Checking Updates
1. Click to the Updates, and fill your email.
2. Some updates will show you.
 

