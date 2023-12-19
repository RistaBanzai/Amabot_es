import os
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import asyncio

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

previous_products = set()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    check_amazon.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


def extract_product_info(item):
    try:
        title_element = item.find('h2')
        product_link_element = item.find('a', class_='a-link-normal')
        image_elements = item.find_all('img', class_='s-image')
        price_element = item.find(class_='a-price')
        prev_price_element = item.find(class_='a-text-price')

        if title_element and product_link_element and image_elements and price_element:
            title = title_element.get_text(strip=True)
            product_link = f'https://www.amazon.co.uk{product_link_element["href"]}'
            image_urls = [image.get('src') for image in image_elements]

            if price_element:
                price_span = price_element.find('span', class_='a-offscreen')
                current_price_text = price_span.get_text(strip=True) if price_span else 'N/A'
                current_price = float(''.join(filter(str.isdigit, current_price_text))) / 100.0
        

                previous_products.update(product['title'] for product in current_products if product and product['title'] not in previous_products)

                channel_id = 1183494150771966092
                channel = bot.get_channel(channel_id)

                for product in new_products:
                    embed = discord.Embed(
                        title=product['title'],
                        url=product['product_link'],
                        color=0x3498db,
     
