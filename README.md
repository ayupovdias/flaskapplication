# flaskapplication

Main Features:

User Accounts

-Registration is done with username, email and password

-User can log in and log out of his account

-All users get their own dashboard


Product Management

-New items with images add the latest products with images

-Edit existing products

-Delete products

-Show all the products on the front page

Technical Information:

-Developed on Python and using Flask based framework

-Records data into a SQLite database

-The password field is hashed securely

-Supports image uploads (3mb png, jpg, jpeg)

-Clean, responsive design

Security:

-Passwords are never in plain text

AI integration
This app use hugging face transformer model (distilbert-base-uncased-finetuned-sst-2-english)to determine the sentiment score of the product descriptions when new or edit a product. 
The model estimates if the description is positive or negative helping users to write better


