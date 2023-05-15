# BIKE WORLD
Welcome to **Bike World**! 

The ecommerce store offers a wide selection of top-quality mountain bikes, suitable for both beginners and seasoned riders.

At Bike World, we understand that mountain biking is not just a hobby, it's a passion. That's why we are committed to providing our customers with the best possible products and services. We carefully curate our selection of mountain bikes from trusted brands to ensure that our customers have access to the latest and greatest equipment.

Our user-friendly website allows you to browse our extensive collection of mountain bikes.

Please note that at this stage, **Bike World** is a fictitious store which has been created for the purposes of satisfying the requirements for the **Code Institute** Full Stack Development Course Project 5.


![Mockup]()

# Live Project

[View live project here]()

## Contents

---
- [Target Audience](#target-audience)
- [Business Objectives](#business-objectives)
- [User Objectives](#user-objectives)
- [User Experience (UX)](#user-experience-ux)
    - [User Demographics](#user-demographics)
    - [User Requirements](#user-requirements)
    - [Site Map](#site-map)
    - [User Stories](#user-stories)
- [Design](#design)
    - [Colour Palette](#colour-palette)
    - [Fonts](#fonts)
    - [Images](#images)
    - [Wireframes](#wireframes)
- [Agile methodology](#agile-methodology)
    - [MoSCoW method and story points](#moscow-method-and-story-points)
    - [Iterations](#iterations)
- [Database Model](#database-model)
    - [Database](#database)
    - [Entity Relationship Diagram](#entity-relationship-diagram)
    - [Models](#models)
- [Features](#features)
    - [Implemented Features](#implemented-features)
    - [Future Features](#future-features)
- [Marketing and Social Media](#marketing-and-social-media)
    - [User Group](#user-group)
    - [Online Platforms](#online-platforms)
    - [Facebook Page](#watches--clocks---facebook-page)
- [Privacy Policy](#privacy-policy)
- [Search Engine Optimization](#search-engine-optimization)
    - [sitemap.xml](#sitemapxml)
    - [robots.txt](#robotstxt)
    - [Sitemap Google Registration](#sitemap-google-registration)
- [AWS Setup Process](#aws-setup-process)
    - [AWS S3 Bucket](#aws-s3-bucket)
    - [IAM Set Up](#iam-set-up)
    - [Connecting AWS to the Project](#connecting-aws-to-the-project)
- [Stripe Payments](#stripe-payments)
    - [Payments](#payments)
    - [Webhooks](#webhooks)
- [Technologies Used](#technologies-used)
    - [Languages](#languages)
    - [Framework](#framework)
    - [Programs](#programs)
- [Testing](#testing)
- [Deployment](#deployment)
- [References & Credit](#references-credit)

---

# <a name="target-audience">Target Audience</a>
The target audience for **Bike World** are mountain biking enthusiasts of all ages and experience levels. **Bike World** appeals to a wide range of customers, from beginners who are just starting out in the sport, to experienced riders who demand the latest and greatest equipment. **Bike World** understands that mountain biking is more than just a hobby, it's a lifestyle, and **Bike World** aims to provide a platform where like-minded individuals can come together and find the best equipment to support their passion.

# <a name="business-objectives">Business Objectives</a>
The primary business objective is to provide customers with a comprehensive online platform for purchasing top-quality mountain bikes. **Bike World** strives to offer a diverse selection of bikes from trusted brands, at competitive prices, with the convenience of online shopping. The goal is to establish **Bike World** as a leading ecommerce store for mountain bikes, with a reputation for excellent customer service and a commitment to providing the latest and greatest equipment. **Bike World** is committed to provid customers with an intuitive and enjoyable shopping experience. The website is designed with a user-friendly interface that is easy to navigate, with clear categories and filters that allow customers to quickly find the products they are looking for. 

# <a name="user-objectives">User Objectives</a>
The primary user objectives are to provide a wide range of high-quality mountain bikes at competitive prices, with a user-friendly online shopping experience. **Bike World** strives to offer customers the convenience of online shopping with the added benefit of expert product knowledge and exceptional customer service. Additionally, **Bike World** provides customers with access to detailed product information and reviews to help them make informed decisions about their purchase.

# <a name="user-experience-ux">User Experience (UX)</a>

## <a name="user-demographics">User Demographics</a>
The user demographics for Bike World are diverse, as mountain biking is a sport enjoyed by people of all ages and backgrounds. However, the primary target audience consists of males and females between the ages of 18 and 45 who are passionate about mountain biking. Bike World also caters to beginners who are just starting out in the sport, as well as experienced riders who are looking for the latest and greatest equipment.

## <a name="user-requirements">User Requirements</a>
Bike World customers require a comprehensive selection of high-quality mountain bikes, ranging from entry-level to premium models, with detailed product information and competitive pricing. We also recognize the importance of customer service and support, providing responsive and knowledgeable assistance to answer any questions or concerns. Additionally, customers require a secure and easy-to-use online platform, with a streamlined checkout process. To enhance the user experience, Bike World understands the importance of providing a wishlist feature to save products for later purchase and an intuitive platform that is easy to navigate.

## <a name="site-map">Site Map</a>

## <a name="user-stories">User Stories</a>

# <a name="design">Design</a>

## <a name="colour-palette">Colour Palette</a>
![Colour Palette](documentation/colours.png)

To create a simple design that does not distract customers from the essential areas, only few colors are used. ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) White is used as the main background color, which creates a clear and bright design. 
The font is predominantly black, which creates a good contrast and is easily readable for customers. 
Certain areas and segments have a ![#DFDFDF](https://placehold.co/15x15/DFDFDF/DFDFDF.png) light gray color to highlight and accentuate them. This provides a subtle contrast to the predominantly white background and draws attention to important elements of the design. 
An ![#CD4C1D](https://placehold.co/15x15/CD4C1D/CD4C1D.png) orange color has been chosen for all call-to-action buttons and promotional/sale segments. This color stands out and grabs the user's attention, as Bike World wants to guide the customer to the checkout and purchase process as easily as possible. The orange color creates a sense of urgency and encourages the user to take action. By using this color, Bike World aims to optimize the user experience, drive sales and reduce the abondend cart rate.

After testing the accessibility, the inital orange was changed to a darker orange to achieve a better contrast between the orange background and the white text from buttons.

## <a name="fonts">Fonts</a>
[_Sourced via Google Fonts._](https://fonts.google.com/)

Using a consistent font throughout a website is important for creating a cohesive and easy-to-use experience for the user. This is why **Roboto** was choosen as font for Bike world.
Roboto is a versatile sans-serif font that was designed by Google in 2011 specifically for use on the Android operating system. Roboto has a clean and modern appearance, legibility, and versatility. Roboto is designed to be easily legible at various sizes, making it a great choice for both body text and headings. Its clean lines and open letterforms make it easy to read on both small screens and large displays.
Overall, using a consistent font helps to create a polished and professional look for Bike World, while also improving the user experience by providing clear and easy-to-read text.

## <a name="images">Images</a> 

[*Sourced via Pexels.*](https://www.pexels.com/)

In an online shop, images are an essential element of the user experience. They provide visual cues and help users understand what the products look like in real life. In my shop, I have used images in the hero banner and category callouts to showcase the bikes in action. The hero banner is the first thing that users see when they arrive on the site. By using an image that shows a bike in action, users can quickly understand the main purpose of the site and the type of products that are being sold. This helps to create an emotional connection with the user and encourages them to explore the site further. Similarly, the category callouts use images to showcase the different types of bikes that are available. By showing the bikes in action, users can understand how they might use the bikes in their own lives. This helps to make the products more relatable and can encourage users to make a purchase.
Product images from the [**Kegel**](https://www.kaggle.com/datasets/tysonpo/bike-ads-images-prices-specifications?select=data_bike_exchange.json) data set were used for the PDPs. Improvements are still desirable in this regard. In an ideal scenario, there would be several pictures of the bike with detail shots. The format would be webp and the quality a slightly better so that a zoom could also be built in. 

# <a name="marketing-and-social-media">Marketing and Social media</a>

## <a name="user-group">User Group</a>

As already mentioned in [Target Audience](#target-audience) the users of **Bike World** would primarily be individuals who are interested in purchasing high-class mountain bikes. They are likely to be cycling enthusiasts, outdoor adventurers, sports enthusiasts, and individuals who value quality and performance. They may range from beginners looking for their first mountain bike to experienced riders seeking top-of-the-line models.

## <a name="online-platforms">Online Platforms</a>