"""
Disruption intelligence sourced from major consulting firms, April 2026.
Scraped from EY, Deloitte, McKinsey and KPMG insights pages.
"""

SCRAPED_DATE = "April 2026"

DISRUPTION_THEMES = [
    {
        "theme": "AI Operationalisation",
        "icon": "🤖",
        "summary": (
            "The question has shifted from 'should we adopt AI?' to 'why aren't we "
            "capturing value from it yet?' Agentic AI, AI governance, and AI's cultural "
            "and human impacts are the frontier topics."
        ),
        "firms": {
            "Deloitte": [
                "Bridging the AI value gap: Are team dynamics the missing link? — "
                "Larger, cognitively diverse, highly connected teams drive the strongest AI outcomes.",
                "AI's cultural debt — the human/organisational baggage slowing AI adoption.",
                "Fact or fabrication? AI is blurring the line when it comes to people and work.",
                "Navigating the AI-enabled workforce shift: From managing exits to orchestrating ecosystems.",
            ],
            "McKinsey": [
                "AI is everywhere. The agentic organisation isn't — yet. Most companies are still "
                "experimenting, not redesigning workflows or culture.",
                "Sovereign AI: nations seeking control over their own AI stack as a strategic priority.",
                "AI agents in biology R&D and drug discovery (Stanford/McKinsey research).",
                "Winning the race to rewire in 2026: companies redesigning end-to-end operations "
                "will define the next wave of competitive advantage.",
            ],
            "KPMG": [
                "2026 US Technology Survey: data and tech leaders face unprecedented opportunities "
                "and complex challenges in the evolving AI landscape.",
                "AI is the top transformation driver across industries.",
            ],
            "EY": [
                "NAVI framework: Nonlinear, Accelerated, Volatile, Interconnected — "
                "positioning disruption as an opportunity, not just a threat.",
                "EYQ platform: advancing GenAI capabilities for enterprise use.",
            ],
        },
    },
    {
        "theme": "Geopolitical & Economic Uncertainty",
        "icon": "🌍",
        "summary": (
            "Geopolitical risk has shot up the C-suite agenda sharply in 2026. CFOs are "
            "building cash buffers and doubling down on performance. Trade, tariffs, and "
            "regulatory change are creating significant pressure on non-AI businesses."
        ),
        "firms": {
            "McKinsey": [
                "CFOs have been concerned about geopolitical impacts for months (April 2026 survey) — "
                "doubling down on performance and building cash/liquidity buffers.",
                "MGI: The race takes off in the next big arenas of competition — investment cycles "
                "accelerating, value pools shifting.",
            ],
            "Deloitte": [
                "US Economic Forecast Q1 2026: AI investments may drive near-term momentum, but "
                "non-AI businesses face pressure from geopolitical conflicts and uncertainty.",
                "Changing inflation dynamics pose new risks for the US economy.",
                "Eurozone economic outlook April 2026.",
                "Global trade and tariffs as a top-read executive topic this quarter.",
            ],
            "EY": [
                "Geostrategic Analysis (monthly series, March 2026): political risk impact on "
                "international business.",
                "CFOs and tax leaders innovating with AI to manage geopolitical turbulence, "
                "talent shortages, and regulatory developments.",
            ],
            "KPMG": [
                "Policy in motion: regulatory changes across industries positioned as a top C-suite concern.",
                "Winners Don't Wait: Transforming with Confidence and Clarity in Volatile Times.",
            ],
        },
    },
    {
        "theme": "Workforce & Human Capital",
        "icon": "👥",
        "summary": (
            "The AI/work interface is a major disruption theme. Organisations are moving from "
            "managing headcount to orchestrating human-machine ecosystems. Gen Z expectations "
            "and organisational structures are both under pressure."
        ),
        "firms": {
            "Deloitte": [
                "2026 Global Human Capital Trends: shift from tensions to tipping points. "
                "Key choices: adapt continuously, move with speed, lead with a human edge.",
                "AI and the future of human decision-making.",
                "Have organisational functions outlived their function?",
                "Gen Z and millennials at work: pursuing a balance of money, meaning, and well-being.",
                "Staying relevant in a world that won't sit still.",
            ],
            "McKinsey": [
                "Building the AI-powered organisation — three tectonic forces reshaping orgs "
                "(survey of 10,000+ leaders).",
                "Preparing the next generation of confident communicators in an AI-driven economy "
                "(JA Worldwide / McKinsey GenAI coaching).",
            ],
            "KPMG": [
                "Third-party risk management evolving to AI-optimised strategies — workforce and "
                "supplier ecosystems converging.",
            ],
        },
    },
    {
        "theme": "Supply Chain Fragility",
        "icon": "⛓️",
        "summary": (
            "Supply chains need to predict and adapt, not just react. Semiconductor fragility, "
            "biopharma sustainability, and US manufacturing labour shortages are the "
            "live pressure points."
        ),
        "firms": {
            "Deloitte": [
                "New technologies and familiar challenges could make semiconductor supply chains "
                "more fragile.",
                "Making biopharma's supply chains more environmentally sustainable.",
                "A shrinking workforce may thwart US manufacturing ambitions.",
                "Is your supply chain trustworthy? — trust as a supply chain KPI.",
            ],
            "KPMG": [
                "2026 Global Third-Party Risk Management Survey: key findings to power "
                "AI-optimised third-party risk management strategies.",
            ],
        },
    },
    {
        "theme": "M&A & Ownership Transitions",
        "icon": "🤝",
        "summary": (
            "Strong deal optimism in 2026, but strategies are diverging sharply between "
            "corporates and PE. The Great Ownership Transfer — boomer retirements — is "
            "creating a wave of small business transitions with systemic economic implications."
        ),
        "firms": {
            "McKinsey": [
                "The Great Ownership Transfer (MGI, Feb 2026): millions of baby boomers retiring "
                "= unprecedented wave of small-business ownership transitions in the US.",
                "How top economic performers lean into their competitive advantage to guide strategy.",
            ],
            "KPMG": [
                "2026 M&A Deal Market Study: strong dealmaker optimism with distinct strategies "
                "for corporate and PE firms.",
            ],
            "Deloitte": [
                "Shifting M&A strategies — a top-read executive topic this quarter.",
                "Workforce planning in the AI era as a key M&A integration consideration.",
            ],
        },
    },
    {
        "theme": "Sustainability & Climate Regulation",
        "icon": "🌱",
        "summary": (
            "EU sustainability regulation is creating both compliance pressure and competitive "
            "opportunity. Climate data is increasingly framed as an economic asset. "
            "Decarbonisation is shifting from aspiration to operational requirement."
        ),
        "firms": {
            "Deloitte": [
                "EU 2025 Sustainability Regulation Outlook: unlocking competitiveness and growth.",
                "Can Earth's data create a US$3.8T economic opportunity?",
                "Green progress or green gap: how does the automotive sector align with EU "
                "sustainability targets?",
            ],
            "EY": [
                "Climate change and sustainability services as a core service line.",
                "What makes today's climate leaders tomorrow's business leaders?",
            ],
            "McKinsey": [
                "McKinsey Health Institute: The health of nations — return to better health "
                "by country, linking population health to economic performance.",
            ],
        },
    },
]
