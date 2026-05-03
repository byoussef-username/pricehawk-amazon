import re
from groq import Groq

client = Groq(
    api_key="myapikey")


def get_legit_items(data_list, keyword):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[
                {"role": "system", "content": f"""You are a product filter for Amazon search results.
                The user searched for: "{keyword}"

                Your job is to remove results that are clearly unrelated to the search.

                KEEP an item if:
                - It is the exact product
                - It is a color variant (white, black, blue etc.)
                - It is a size variant (small, large, XL etc.)
                - It is a condition variant (renewed, refurbished, used)
                - It is a bundle or pack of the same product
                - It is the same model with slightly different specs
                - The title contains the main words of the keyword

                FLAG an item ONLY if:
                - It is a completely different brand AND different product
                - It is a different model number (G203, G309 are NOT G305)
                - It is a completely unrelated product category
                - It is media about the product (book, movie, audiobook)

                STRICT RULE: When in doubt → KEEP IT. Never flag something you are not 100% sure about.

                Return ONLY a Python list of 0-based indices like [1, 3]. 
                If nothing should be flagged return [].
                No explanation. No text. Just the list."""},
                {"role": "user", "content": str(data_list)}
            ]
        )
        res = completion.choices[0].message.content

        
        bracket_match = re.search(r"\[(.*?)\]", res)
        search_area = bracket_match.group(1) if bracket_match else res

        raw_numbers = re.findall(r"\d+", search_area)

        
        valid_indices = [int(n)
                         for n in raw_numbers if int(n) < len(data_list)]

        return sorted(list(set(valid_indices)))
    except Exception as e:
        print(f"Error: {e}")
        return []
