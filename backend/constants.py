import pandas as pd

class _Constants():
    def __init__(self, suburb_file: str):
        suburb_df = pd.read_csv(suburb_file, delimiter=";")
        suburb_df = suburb_df[["Official Name Suburb", "Official Name State"]]
        suburb_df["Official Name Suburb"] = suburb_df["Official Name Suburb"].str.extract(r"([^\(\)]*)(?:\(.*\))?")
        suburb_df["Official Name Suburb"] = suburb_df["Official Name Suburb"].str.strip()

        self.suburbs = suburb_df["Official Name Suburb"]

        self.regex_suburb = "|".join(self.suburbs.sort_values(key=lambda x: x.str.len(), ascending=False)).lower()
        """a regex that matches any suburb in Australia"""

        # truncated suburbs
        max_suburb_missing = 5
        self.suburb_missing_set = set()
        for s in self.suburbs:
            for i in range(1, max_suburb_missing+1):
                if len(s[:-i]) <= 3: break
                if s[:-i].endswith(" "): break
                if s[:-i].lower() in {"north", "south", "east", "west"}: break
                self.suburb_missing_set.add(s[:-i])
        self.regex_suburb_truncated = "|".join(self.suburb_missing_set).lower()
        """a regex that matches any suburb that is truncated by up to 5 characters"""

        self.regex_state = "|".join(["nsw", "ns", "vic", "vi", "qld", "ql", "act", "ac", "nt", "wa", "tas", "ta", "sa"])
        """a regex that matches any state in Australia, possibly truncated to 2 characters"""

        self.regex_country = "|".join(["au", "aus", "us", "usa"])

        self.regex_post_suburb = fr"\s*({self.regex_state})?\s*({self.regex_state})?\s*({self.regex_country})?\s*({self.regex_country})\s*$"
        """a regex that matches what should come after the suburb in the description"""

        self.category_dict = {
            "Youtube Premium": "shopping",
            "Star Discount Chemist": "health",
            "Fortune Paradise": "restaurant",
            "Unisuper Voluntary Contribution": "investment",
            "Caltex": "fuel",
            "Usyd Salary": "income",
            "Xiangyao Asian Supermarket": "groceries",
            "Sydney Motorcycle Wizard": "motorbike",
            "Decathlon": "sports",
            "Macquarie Oral and Maxillofacial": "health",
            "Opal Card": "public transport",
            "Beem": None,
            "Duoway Restaurant": "restaurant",
            "Usyd Union": "restaurant",
            "7-Eleven": "fuel",
            "Woolworths": "groceries",
            "Coles": "groceries",
            "EG Group": "fuel",
            "Cash Deposit": None,
            "Mobil": "fuel",
            "Speedway": "fuel",
            "Rent": "rent",
            "St Peters Fruitworld": "groceries",
            "BWS": "shopping",
            "Pharmacy 4 Less": "health",
            "Ikea": "shopping",
            "Youtube Music": "shopping",
            "Amazon Marketplace": "shopping",
            "Aldi": "grocery",
            "Kmart": "shopping",
            "Bikebiz": "motorbike",
            "Big W": "shopping",
            "JB Hi Fi": "shopping",
            "Tonyon": "grocery",
            "AMX": "motorbike",
            "BP": "fuel",
            "Metro Petroleum": "fuel",
            "Bunnings": "shopping",
            "Apex": "fuel",
            "Live Group": "groceries",
            "Priceline Pharmacy": "health",
            "Ampol": "fuel",
            "Paypal": "shopping",
            "Youth Allowance": "income",
            "Usyd Scholarship": "income",
            "Medicare Rebate": "health",
            "Ebay": "shopping",
            "ISG Salary": "income",
            "Hmart": "groceries",
            "Aliexpress": "shopping",
        }
        """maps description to category"""

class _DescRules:
    def __init__(self):
        self.display_name_dict = {"TRANSPORTFORNSW TAP": "Opal Card",
                         "Salary The University o 1180325": "Usyd Salary",
                         "ST. PETERS FRUITWORL": "St Peters Fruitworld",
                         "STAR DISCOUNT CHEMIS": "Star Discount Chemist",
                         "TRANSPORTFORNSW OPAL": "Opal Card",
                         "DUOWAY GROUP PTY LTD": "Duoway Restaurant",
                         "GOOGLE*YOUTUBE MUSIC": "Youtube Music",
                         "AMAZON AU MARKETPLACE": "Amazon Marketplace",
                         "Google YouTube": "Youtube Premium",
                         "Google YouTubePremium": "Youtube Premium",
                         "AMAZON AU SYDNEY SOUTH NS AUS ": "Amazon Marketplace",
                         "GOOGLE*YOUTUBE MUSIC G.CO/HELPPAY# AU AUS ": "Youtube Music",
                         "GOOGLE*YOUTUBEPREMIUM G.CO/HELPPAY# AU AUS ": "Youtube Music",
                         "Transfer to CBA A/c NetBank rent": "Rent",
                         "Transfer to other Bank NetBank rent": "Rent",
                         "Sydney Motorcycle": "Sydney Motorcycle Wizard",
                         "UNI OF SYDNEY UNION UNI OF": "Usyd Union",
                         "XIANGYAO ASIAN SUPERMA": "Xiangyao Asian Supermarket",
                         "EG GROUP 5500": "EG Group",
                         "MCQRE ORL & MXIL S P": "Macquarie Oral and Maxillofacial",
                         }
        self.starts_with_set = {"Woolworths",
                        "Coles",
                        "Amazon Marketplace",
                        "Live Group",
                        "Bunnings",
                        "Kmart",
                        "Aldi",
                        "Big W",
                        "EG Group",
                        "JB Hi Fi",
                        "Bikebiz",
                        "Tonyon",
                        "Ikea",
                        "Fortune Paradise",
                        "Decathlon",
                        "Speedway",
                        "Apex",
                        "Mobil",
                        "Ampol",
                        "BWS",
                        "Caltex",
                        "BP",
                        "7-Eleven",
                        "Cash Deposit",
                        "Beem",
                        "Pharmacy 4 Less",
                        "Discount Chemist"
                        "Douglas Hanly Moir",
                        "AMX",
                        "Metro Petroleum",
                        "Ebay",
                        "Hmart"}

        self.starts_with_dict = {"pline": "Priceline Pharmacy",
                        "UNISUPER MEM VOL CON": "Unisuper Voluntary Contribution",
                        "Refund Purchase Beem": "Beem",
                        "Fast Transfer From Stamen Engineering": "ISG Salary"
                    }

        self.regex_dict = {r"Direct Debit [0-9]+ Paypal": "Paypal",
              r"Direct Credit [0-9]+ Paypal": "Paypal",
                  r"Direct Credit [0-9]+ Ctrlink Yth All": "Youth Allowance",
                  r"Direct Credit [0-9]+ Central Accounts Sam": "Usyd Scholarship",
                  r"Direct Credit [0-9]+ Mcare Benefits": "Medicare Rebate"}

Constants = _Constants(suburb_file = "georef-australia-state-suburb.csv")
DescRules = _DescRules()