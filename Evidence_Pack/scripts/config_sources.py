"""Source registry for the Evidence Pack.

Every source the pod needs, with the rubric cell it supports and the exact thing
to capture. `status` is maintained by 03_fetch_public_data.py; it is never
guessed here. Only URLs and capture instructions live in this file.

status values:
    NOT_ATTEMPTED   declared but not fetched yet
    OK              fetched, content saved under data/03_external/raw/
    HTTP_ERROR      server answered with an error code
    NETWORK_ERROR   could not reach the host (offline, blocked, DNS)
"""

RUBRIC = {
    "D": "Desirability",
    "F": "Feasibility",
    "V": "Viability",
    "S": "Strategic fit",
}

SOURCES = [
    # ---- P0: blocks a score or changes the position ------------------------
    {
        "id": "iap_ios_coach",
        "priority": "P0",
        "cells": ["V"],
        "url": "https://apps.apple.com/us/app/id1005052173",
        "capture": "In-app purchase list: SKU, price, period (month/year), trial days, date checked",
        "note": "Apple shows IAPs on the listing; needs a browser or a user agent that renders JS.",
    },
    {
        "id": "iap_play_coach",
        "priority": "P0",
        "cells": ["V"],
        "url": "https://play.google.com/store/apps/details?id=com.bellabeat.cacao",
        "capture": "In-app purchase price range and SKU list, date checked",
        "note": "Play shows 'In-app purchases  $X - $Y per item'.",
    },
    {
        "id": "iap_ios_tracker",
        "priority": "P0",
        "cells": ["V"],
        "url": "https://apps.apple.com/us/app/id436762566",
        "capture": "In-app purchase list: SKU, price, period, trial, date checked",
        "note": "Compare against the Coach list to answer one-subscription-or-two.",
    },
    {
        "id": "iap_play_tracker",
        "priority": "P0",
        "cells": ["V"],
        "url": "https://play.google.com/store/apps/details?id=org.nanobit.perioddiary",
        "capture": "In-app purchase price range and SKU list, date checked",
        "note": "",
    },
    {
        "id": "ivy_support_home",
        "priority": "P0",
        "cells": ["F"],
        "url": "https://support.ivyhealth.ai/",
        "capture": "Search the help centre for export, backup, restore, transfer, account merge",
        "note": "Decides whether growth lever 1 is 'restore' or 'rebuild'.",
    },
    {
        "id": "ivy_support_update",
        "priority": "P0",
        "cells": ["F"],
        "url": "https://support.ivyhealth.ai/hc/en-us/articles/28733719986066-Keeping-your-IVY-updated",
        "capture": "Whether history survives a device change; any stated backup behaviour",
        "note": "",
    },
    {
        "id": "kff_women_online_health",
        "priority": "P0",
        "cells": ["D", "S"],
        "url": "https://www.kff.org/womens-health-policy/womens-experiences-accessing-health-information-online-trusted-sources-and-contraceptive-information/",
        "capture": "Share who used AI chatbots for health information and share who trust it; sampling note",
        "note": "Local file data-PmfG5.csv already holds the 42% use figure by gender/age/race/income.",
    },
    {
        "id": "ivy_support_section_gs",
        "priority": "P0",
        "cells": ["F"],
        "url": "https://support.ivyhealth.ai/hc/en-us/sections/28711125734418-Getting-Started",
        "capture": "Full article inventory for the IVY+ section (what the help centre does and does not document)",
        "note": "If no article covers export, backup or restore, say so in the limits rather than claiming a capability.",
    },
    {
        "id": "ivy_support_search_export",
        "priority": "P0",
        "cells": ["F"],
        "url": "https://support.ivyhealth.ai/hc/en-us/search?query=export",
        "capture": "Number of results and article titles for 'export'",
        "note": "",
    },
    {
        "id": "ivy_support_search_backup",
        "priority": "P0",
        "cells": ["F"],
        "url": "https://support.ivyhealth.ai/hc/en-us/search?query=backup",
        "capture": "Number of results and article titles for 'backup'",
        "note": "",
    },
    {
        "id": "ivy_support_search_restore",
        "priority": "P0",
        "cells": ["F"],
        "url": "https://support.ivyhealth.ai/hc/en-us/search?query=restore",
        "capture": "Number of results and article titles for 'restore'",
        "note": "",
    },
    # ---- P1: strengthens a score ------------------------------------------
    {
        "id": "trends_google",
        "priority": "P1",
        "cells": ["D"],
        "url": "https://trends.google.com/trends/explore",
        "capture": "5-year US index for: period tracker, perimenopause, AI health assistant",
        "note": "Index 0-100, never a search count.",
    },
    {
        "id": "fda_den170052",
        "priority": "P1",
        "cells": ["F"],
        "url": "https://www.accessdata.fda.gov/cdrh_docs/pdf17/DEN170052.pdf",
        "capture": "Indication for use, decision date, device type name",
        "note": "Illustrates the wellness / medical-claim line.",
    },
    {
        "id": "natural_cycles_hcp",
        "priority": "P1",
        "cells": ["F"],
        "url": "https://www.naturalcycles.com/hcp",
        "capture": "How the product describes its own regulatory status",
        "note": "",
    },
    {
        "id": "flo_health",
        "priority": "P1",
        "cells": ["V", "S"],
        "url": "https://flo.health/",
        "capture": "Membership price and what the AI assistant does; date checked",
        "note": "Pricing usually sits inside the app store listing.",
    },
    {
        "id": "clue",
        "priority": "P1",
        "cells": ["V"],
        "url": "https://helloclue.com/",
        "capture": "Membership tiers and price; date checked",
        "note": "",
    },
    {
        "id": "oura_membership",
        "priority": "P1",
        "cells": ["V"],
        "url": "https://ouraring.com/membership",
        "capture": "Monthly price and what membership includes; date checked",
        "note": "Contrast for hardware-plus-subscription.",
    },
    # ---- P2: background only, never scored --------------------------------
    {
        "id": "rock_health",
        "priority": "P2",
        "cells": ["S"],
        "url": "https://rockhealth.com/insights/",
        "capture": "Wearable and smart-ring ownership figures with the survey year",
        "note": "Background; does not enter a score.",
    },
    {
        "id": "pew_trackers_2020",
        "priority": "P2",
        "cells": ["F"],
        "url": "https://www.pewresearch.org/short-reads/2020/01/09/about-one-in-five-americans-use-a-smart-watch-or-fitness-tracker/",
        "capture": "Tracker use by gender, noting the 2020 fieldwork year",
        "note": "Background.",
    },
    {
        "id": "grand_view_femtech",
        "priority": "P2",
        "cells": ["S"],
        "url": "https://www.grandviewresearch.com/industry-analysis/femtech-market-report",
        "capture": "One market-size figure with its edition year",
        "note": "Cite one edition only.",
    },
    {
        "id": "ivy_home",
        "priority": "P2",
        "cells": ["S"],
        "url": "https://ivyhealth.ai/",
        "capture": "How the company describes the AI-first platform, with the date",
        "note": "Marketing intent, not usage behaviour.",
    },
]

# Review keyword groups, mirroring the definitions used in the pod's notes.
# Each entry: name, rubric cell, python regex (case-insensitive), and the note.
KEYWORDS = [
    ("lost_data", "D", r"lost|lost data|deleted|erased|disappear|gone|wipe"),
    ("paywall", "V", r"subscri|premium|paywall|pay for|locked"),
    ("perimenopause", "D", r"perimenopause|menopause|irregular"),
    ("ai_assistant", "S", r"\bai\b|chatbot|chat bot|assistant"),
    ("sync_device", "F", r"sync|connect|pair|bluetooth|device"),
    ("privacy", "S", r"privacy|data sharing|third party|openai|sell my data"),
    ("price", "V", r"\$|price|cost|charge|refund"),
]
