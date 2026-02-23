import discord
from discord.ext import commands
from discord import Embed
import os
from dotenv import load_dotenv
import requests
from urllib.parse import quote_plus

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")


def get_steam_promos():
    try:
        url = "https://store.steampowered.com/api/featuredcategories?cc=BR&l=portuguese"
        response = requests.get(url, timeout=10)
        data = response.json()
        deals = []

        for game in data["specials"]["items"]:
            title = game["name"]
            sale = game["final_price"] / 100
            normal = game["original_price"] / 100
            discount = game["discount_percent"]
            link = f"https://store.steampowered.com/app/{game['id']}"

            deals.append({
                "title": title,
                "normal": normal,
                "sale": sale,
                "discount": discount,
                "store": "Steam",
                "link": link
            })

            if len(deals) >= 10:
                break

        return deals

    except Exception as e:
        print("Erro Steam:", e)
        return []


def get_epic_promos():
    try:
        url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=pt-BR&country=BR&allowCountries=BR"
        response = requests.get(url, timeout=10)
        data = response.json()
        deals = []

        for game in data["data"]["Catalog"]["searchStore"]["elements"]:
            if "price" not in game:
                continue

            price_info = game["price"]["totalPrice"]
            discount_price = price_info["discountPrice"]
            original_price = price_info["originalPrice"]

            if original_price == 0:
                continue

            
            discount = round(
                ((original_price - discount_price) / original_price) * 100
            )


            if discount <= 0:
                continue

            title = game["title"]
            sale = discount_price / 100
            normal = original_price / 100

            link = (
                "https://store.epicgames.com/pt-BR/browse?"
                f"q={quote_plus(title)}&sortBy=relevancy&sortDir=DESC&count=40"
            )

            deals.append({
                "title": title,
                "normal": normal,
                "sale": sale,
                "discount": discount,
                "store": "Epic Games",
                "link": link
            })

            if len(deals) >= 10:
                break

        return deals

    except Exception as e:
        print("Erro Epic:", e)
        return []


@bot.command(name="promo")
async def promo(ctx):
    embed = Embed(title="🎮 Promoções Steam & Epic", color=0x00ff00)


    steam_deals = get_steam_promos()
    if steam_deals:
        embed.add_field(
            name="🟦 Steam",
            value="Principais promoções da Steam:",
            inline=False
        )
        for deal in steam_deals:
            embed.add_field(
                name=f"{deal['title']} — {deal['sale']:.2f} R$",
                value=(
                    f"Antes: {deal['normal']:.2f} R$ | "
                    f"Desconto: {deal['discount']}%\n"
                    f"[Comprar]({deal['link']})"
                ),
                inline=False
            )

    epic_deals = get_epic_promos()
    if epic_deals:
        embed.add_field(
            name="🟪 Epic Games",
            value="Principais promoções da Epic Games:",
            inline=False
        )
        for deal in epic_deals:
            embed.add_field(
                name=f"{deal['title']} — {deal['sale']:.2f} R$",
                value=(
                    f"Antes: {deal['normal']:.2f} R$ | "
                    f"Desconto: {deal['discount']}%\n"
                    f"[Comprar]({deal['link']})"
                ),
                inline=False
            )
    else:
        embed.add_field(
            name="🟪 Epic Games",
            value="Nenhuma promoção encontrada no momento.",
            inline=False
        )

    await ctx.send(embed=embed)


bot.run(TOKEN)
