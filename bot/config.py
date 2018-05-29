FILTER_WORDS = set(["skank",
                    "wetback",
                    "bitch",
                    "cunt",
                    "dick",
                    "douchebag",
                    "dyke",
                    "fag",
                    "nigger",
                    "tranny",
                    "trannies",
                    "paki",
                    "pussy",
                    "retard",
                    "slut",
                    "titt",
                    "tits",
                    "wop",
                    "whore",
                    "chink",
                    "fatass",
                    "shemale",
                    "nigga",
                    "daygo",
                    "dego",
                    "dago",
                    "gook",
                    "kike",
                    "kraut",
                    "spic",
                    "twat",
                    "lesbo",
                    "homo",
                    "fatso",
                    "lardass",
                    "jap",
                    "biatch",
                    "tard",
                    "gimp",
                    "gyp",
                    "chinaman",
                    "chinamen",
                    "golliwog",
                    "crip",
                    "raghead",
                    "negro",
                    "hooker"])

# Sentences we'll respond with if the user greeted us
GREETING_KEYWORDS = ("hello", "hi", "greetings", "sup", "what's up",)
GREETING_RESPONSES = ["'sup bro", "hey", "*nods*", "hey you get my snap?"]

# Sentences we'll respond with if we have no idea what the user just said
NONE_RESPONSES = [
    "uh whatever",
    "meet me at the football table, bro?",
    "code hard bro",
    "want to bro down and crush code?",
    "I'd like to add you to my professional network on LinkedIn",
    "Have you closed your seed round, dog?",
]

# If the user tries to tell us something about ourselves, use one of these responses
COMMENTS_ABOUT_SELF = [
    "You're just jealous",
    "I worked really hard on that",
    "My Klout score is 9000",
]

# Template for responses that include a direct noun which is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "Were you aware I was a serial entrepreneur in the {noun} sector?",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]
