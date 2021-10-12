import asyncio
import cleverbotfree
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# cleverbotfree need run
# playwright install firefox

async def async_chat(send_text):
    async with cleverbotfree.async_playwright() as p_w:
        c_b = await cleverbotfree.CleverbotAsync(p_w)
        bot = await c_b.single_exchange(send_text)
        #print('Cleverbot:', bot)
        await c_b.close()
    return bot

def get_identity(id = 0,fetch_new = True):
    #get fake identity from fake identity generator
    #https://www.fakenamegenerator.com/
    #bs4

    page = requests.get("https://www.fakenamegenerator.com/")
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup.prettify()


if __name__ == "__main__":

    #asyncio.run(async_chat("Okay, let's get started. Please tell me which type of insurance you'd like to get a quote for?"))

    #nw = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    #print(nw)

    #print(get_identity())

    ex = [{'name':'Bryan V. Tyler',
            'address':'203 Glenview Drive Victoria, TX 77901',
            'mother_maiden_name':'Calder',
            'SSN':'461-48-1234',
            'phone':'361-580-9588',
            'bday':'January 2, 1998',
            'age':'23',
            'email':'BryanVTyler@dayrep.com',
            'card':'5294 0842 4688 1724',
            'expire':'2/2025',
            'cvc2':'951',
            'company':'National Shirt Shop',
            'occoputation':'Songwriter',
            'height':'188 centimeters',
            'weight':'146.1 pounds',
            'bloodtype':'O+',
            'favcolor':'Purple',
            'vehicle':'1997 Jaguar XK'},
            {'name':'Evelyn J. Lagunas',
            'address':'2989 Sherwood Circle Greensboro, NC 27410',
            'mother_maiden_name':'Leavitt',
            'SSN':'241-54-4321',
            'phone':'336-995-5196',
            'bday':'May 19, 2002',
            'age':'19 ',
            'email':'EvelynJLagunas@jourrapide.com',
            'card':'4916 0051 4485 1635',
            'expire':'10/2025',
            'cvc2':'083',
            'company':'Total Network Development',
            'occoputation':'Forging machine operator',
            'height':'172 centimeters',
            'weight':'162.8 pounds ',
            'bloodtype':'A+',
            'favcolor':'Green',
            'vehicle':'2004 Ferrari Maranello'},
            ]

    print(ex)
    import json
    with open('profiles.json','w') as json_file:
        data = json.dump(ex,json_file)
    """
        {'name':'',
                'address':'',
                'mother_maiden_name':'',
                'SSN':'',
                'phone':'',
                'bday':'',
                'age':'',
                'email':'',
                'card':'',
                'expire':'',
                'cvc2':'951',
                'company':'',
                'occoputation':'',
                'height':'',
                'weight':'',
                'bloodtype':'',
                'favcolor':'',
                'vehicle':''}
    """