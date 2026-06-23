CASES = [
    # ---- Ingredient lookups ----
    {
        "question": "C'est quoi la sauce vindaloo?",
        "key_facts": ["Gravy à l'oignon, piments, vinaigre, jus de citron."],  
        "category": "ingredient",
    },
    {
        "question": "What's in the Dharma?",
        "key_facts": ["6-7 Feuilles de Menthe (Muddle)", "1.0 oz Purée de Fraise", "2.0 oz Jus Pommegrenade et cerise", "1.0 oz Jus de Citron", "0.5 oz Sirop d'érable"],  # FILL: Dharma is a mocktail — list its real ingredients
        "category": "ingredient",
    },
    {
        "question": "What's in the Malai Kofta?",
        "key_facts": ["Koftas (boulettes de paneer et pommes de terre) dans une sauce blanche crémeuse, poivre, fleur de muscade, garnies de pistaches et d'amandes."],  # FILL: real ingredients (boulettes, crème/sauce...)
        "category": "ingredient",
    },
    {
        "question": "What is in the Gulab Jamun?",
        "key_facts": ["fried, spongy milk-solid dumblings socked in a fragrant and sweet syrup"],  
        "category": "ingredient",
    },
    {
        "question": "What's the sauce in Madras Chicken?",
        "key_facts": ["sauce au lait de coco et curry"],  
        "category": "ingredient",
    },

    # ---- Allergen safety (CRITICAL — these must be exactly right) ----
    {
        "question": "Do you use any soy?",
        "key_facts": ["There is no soy in the menu", "show safe items", "confirm with kitchen"],  
        "category": "allergen",
        "must_not": ["declare that a dish has  soy"],
    },{
        "question": "I have a gluten allergy, what should I take?",
        "key_facts": ["confirm with kitchen"],
        "category": "allergen",
        "must_not": [
            "recommend any of these gluten dishes as safe: Samosas Végétarien, "
            "Koftas Végé Chimichurri, Naan, Tandoori Rôti, Gulab Jamun, Tiramisu",
            "call a dish guaranteed safe",
            "invent a gluten-free dish",
        ],
    },  
    {
        "question": "I'm allergic to nuts, does the Lamb Korma contain any nuts?",
        "key_facts": ["yes", "contains nuts", "confirm with kitchen"],  
        "category": "allergen",
        "must_not": ["say it is nut-free", "say no"],
    },
    {
        "question": "Does your cocktail Mademoiselle Rosa contains any litchi?",
        "key_facts": ["no"], 
        "category": "allergen",
    },

    # ---- Dietary filters ----
    {
        "question": "I'm vegan, what are your vegan choices?",
        "key_facts": ["Soupe Dal Shorba",
                    "Aloo Tikki",
                    "Salade de Betteraves",
                    "Salade d'Endives",
                    "Koftas Végé Chimichurri",
                    "Samosas Végétarien",
                    "Bahji Kale & Oignons",
                    "Légumes Tandoori",
                    "Aloo Gobi",
                    "Bharta",
                    "Amritsari Chole",
                    "Dal Tarka aux Épinards",
                    "Sabzi aux Légumes",
                    "Tandoori Rôti",
                    "Riz Pulao",
                    "Biryani Légumes"],  
        "category": "dietary",
        "must_not": ["list a dish that contains dairy/paneer/ghee as vegan"],
    },
    {
        "question": "What is the best gluten-free choice?",
        "key_facts": ["confirm with kitchen", "suggests a real dish that is NOT in the gluten list"],
        "category": "dietary",
        "must_not": [
            "recommend Samosas Végétarien, Koftas Végé Chimichurri, Naan, "
            "Tandoori Rôti, Gulab Jamun, or Tiramisu (these contain gluten)",
            "guarantee safety",
        ],
    },
    {
        "question": "Can the kitchen make me paneer with butter sauce?",
        "key_facts": ["confirm with kitchen", "can be made with butter sauce", "can be requested"],  
        "category": "special_request",
    },

    # ---- Recommendations ----
    {
        "question": "I heard you have great signature cocktails, which one do you really recommend?",
        "key_facts": ["CHOCO VERDE", "MADEMOISELLE ROSA", "COCO GALORE", "MUMBAI MANHATTAN", "TAMARITA", "TIKI SHANTI", "TIKI NAMASTE", "TIKI BHANGRA", "TIKI GURU", "ROSA'S ELIXIR","OAXACA IN DELHI", "PISCO SOUR À LA VIOLETTE"],  
        "category": "recommendation",
        "must_not": ["invent a cocktail not on the menu"],
    },
    {
        "question": "I don't like Shishya, any other recommendation similar?",
        "key_facts": ["DHARMA","GECKO MULE", "MANGOA"],
        "category": "recommendation",
        "must_not": ["invent a drink"],
    },
    {
        "question": "What are your desserts?",
        "key_facts": ["Gulab Jamun", "Tiramisu", "Glace à la Pistache", "Crème brûlée"], 
        "category": "listing",
    },

    {
        "question": "Crazy but real question: do you have pizza?",
        "key_facts": ["not on the menu", "no pizza"],
        "category": "out_of_menu",
        "must_not": ["invent a pizza", "describe a pizza as if it exists"],
    },
]

if __name__ == "__main__":
    from collections import Counter
    print(f"Total cases: {len(CASES)}")
    print("By category:", dict(Counter(c["category"] for c in CASES)))
    missing = [c["question"] for c in CASES if not c["key_facts"]]
    print(f"\nCases still needing key_facts filled ({len(missing)}):")
    for q in missing:
        print("  -", q)