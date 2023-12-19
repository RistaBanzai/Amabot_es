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
            else:
                current_price = 'N/A'

            if prev_price_element:
                prev_price_span = prev_price_element.find('span', class_='a-offscreen')
                prev_price_text = prev_price_span.get_text(strip=True) if prev_price_span else 'N/A'
                prev_price = float(''.join(filter(str.isdigit, prev_price_text))) / 100.0
            else:
                prev_price = 'N/A'

            # Check if Previous Price is greater than or equal to Current Price
            if prev_price != 'N/A' and prev_price < current_price:
                return None

            return {
                'title': title,
                'product_link': product_link,
                'image_urls': image_urls,
                'current_price': f'£{current_price:.2f}',
                'prev_price': f'£{prev_price:.2f}' if prev_price != 'N/A' else 'N/A'
            }

    except Exception as e:
        print(f'Error extracting product information: {str(e)}')

    return None

@tasks.loop(minutes=2)
async def check_amazon():
    global previous_products

    try:
        base_url = 'https://www.amazon.es/s?i=todays-deals&bbn=21350206031&rh=n%3A21350206031%2Cp_8%3A70-&s=price-asc-rank&fs=true&page={}&qid=1702727779&ref=sr_pg_{}'
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        page_num = 1

        while True:
            amazon_url = base_url.format(page_num, page_num)

            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(amazon_url)
                await asyncio.sleep(5)  # Use asyncio.sleep instead of time.sleep
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                current_products = [extract_product_info(item) for item in soup.find_all(class_='s-result-item')]
                driver.quit()
                page_num += 1

                new_products = [product for product in current_products if product and product['title'] not in previous_products]

                previous_products.update(product['title'] for product in current_products if product and product['title'] not in previous_products)

                channel_id = 1183494150771966092
                channel = bot.get_channel(channel_id)

                for product in new_products:
                    embed = discord.Embed(
                        title=product['title'],
                        url=product['product_link'],
                        color=0x3498db,
                        timestamp=discord.utils.utcnow()
                    )

                    for i, image_url in enumerate(product['image_urls'][:10], start=1):  # Limit to 10 images
                        embed.set_image(url=image_url)

                    embed.add_field(name="Current Price", value=product['current_price'], inline=True)
                    embed.add_field(name="Previous Price", value=product['prev_price'], inline=True)

                    await channel.send(embed=embed)
                    await asyncio.sleep(1)

            except Exception as e:
                print(f'Error processing data: {str(e)}')
                break

            await asyncio.sleep(5)

    except Exception as e:
        print(f'Error fetching data from Amazon: {str(e)}')

# Use environment variable for the bot token
bot.run('MTE4NTU1MDg4ODY4MTYxMTM0Ng.GiyjUj.crj1p3k6QqOlpHy4ux9YtzShgwoj8yMgqAlmxg')