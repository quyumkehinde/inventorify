# Inventorify

View live version [here](https://inventorify-7pge.onrender.com/products)

Inventorify is an inventory management web application built using the Python Flask framework. It help businesses to keep proper product inventory by providing an intuitive interface for them to manage and monitor their products.

## Database Schema

The database schema consists of three tables:

- **users**: represents users of the application. Each user has a business name, email address, and password. A user can create multiple categories and products.
- **products**: represents products in the inventory. Each product has a name, price, quantity, user_id, and category_id.
- **categories**: represents the categories of products in the inventory. Each category has a name and user_id.

## Setting up the app

To set up the application locally, follow these steps:

- Install Python 3.x on your computer if it's not already installed.
- Clone this repository to your local machine.
- Install the required packages by running the command `pip install -r requirements.txt`.
- Start the application by running `flask run`
- And voila! The application should be running on your machine at `http://127.0.0.1:5000`

## Live website

The application has been deployed online using [Render](https://render.com). You can access the live version of the website [here](https://inventorify-7pge.onrender.com/products)

## Using the app

I've recorded a video providing a detailed step-by-step guide on how to use the app, you can check it out on [here](https://www.awesomescreenshot.com/video/15485807)
