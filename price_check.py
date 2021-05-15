#!/usr/bin/env python3
import urllib

import bs4
import requests


base_url = 'https://theportlandgamestore.crystalcommerce.com/products/search?q='

def search_card(card_title):
    # card_title = "akroma's memorial"
    card_title = urllib.parse.quote(card_title)

    search_url = base_url + card_title

    resp = requests.get(search_url)
    bs = bs4.BeautifulSoup(resp.content, features="html.parser")
    products = bs.find_all('li', attrs={'class':'product'})

    results = list()

    for prod in products:
        try:
            meta = prod.find('div', {'class':'meta'})
            if not meta:
                continue

            description = meta.find('span', {'class':'variant-description'}).text
            out_of_stock = 'All variants' in description
            if out_of_stock:
                description = 'All variants out of stock.'
                stock = ''
                price = ''
            else:
                quality, language = description.split(', ')
                description = f"{quality}, {language}"
                qty = meta.find('span', {'class':'variant-qty'}).text.split()[0]
                stock = f": {qty} in stock"
                price = meta.find('span', {'class':'price'}).text.strip().lstrip('$')
                price = f", ${price}"

            title = meta.find('h4').text
            cardset = meta.find('span', {'class':'category'}).text


            results.append(f"{title} ({cardset}) {description}{stock}{price}")
            # results.append(f"{title} ({cardset}) {description}; {qty} in stock, ${price}")

        # can't parse the expected way, probably because it's not an mtg card
        except:
            pass

    return results


if __name__ == '__main__':
    for card in search_card("akroma's memorial"):
        print(card)
