import random
from datetime import datetime, timedelta

class ContentGeneratorService:
    """
    Local AI Content Studio algorithm.
    Generates social media content ideas without external APIs using dynamic template dictionaries.
    """
    
    HOOKS = [
        "Stop scrolling! If you care about {topic}, you need to see this.",
        "Here is the ultimate secret to mastering {topic} 🤫",
        "3 things nobody tells you about {topic}...",
        "Ever wonder why {topic} is so important? Let's dive in.",
        "Unpopular opinion about {topic}: It's easier than you think."
    ]
    
    BODIES = [
        "We've spent years perfecting this approach. The key is consistency and understanding the fundamentals. When you focus on what matters, the results speak for themselves.",
        "It is all about taking that first step. Most people get paralyzed by overthinking, but action creates momentum. Save this post to remind yourself later!",
        "This strategy changed everything for us. By implementing small, daily habits, you can see massive growth over time. Swipe left to see the breakdown.",
        "Don't let the noise distract you. Stick to the proven methods, test what works for your unique situation, and double down on your winners.",
        "The landscape is changing fast. If you aren't adapting your approach to this, you're leaving opportunities on the table. Here is how you can start today."
    ]
    
    CTAS = [
        "Double tap if you agree! ❤️",
        "Save this post for your next session! 📌",
        "Tag a friend who needs to hear this! 👇",
        "Click the link in our bio to learn more! 🔗",
        "What are your thoughts? Let us know in the comments! 💬"
    ]

    HASHTAG_BANK = {
        "default": ["#viral", "#trending", "#explorepage", "#growth", "#mindset", "#success", "#community", "#inspiration"],
        "business": ["#entrepreneur", "#businessgrowth", "#marketing", "#leadership", "#b2b", "#sales", "#startup"],
        "lifestyle": ["#lifestyle", "#dailyvlog", "#aesthetic", "#inspiration", "#wellness", "#selfcare", "#motivation"]
    }

    def generate_captions(self, topic: str) -> list[str]:
        topic = topic.strip() or "growth"
        captions = []
        for _ in range(5):
            hook = random.choice(self.HOOKS).format(topic=topic)
            body = random.choice(self.BODIES)
            cta = random.choice(self.CTAS)
            captions.append(f"{hook}\n\n{body}\n\n{cta}")
        return captions

    def generate_hashtags(self, category: str = "default") -> str:
        bank = self.HASHTAG_BANK.get(category.lower(), self.HASHTAG_BANK["default"])
        # Mix default and category specific
        combined = list(set(bank + self.HASHTAG_BANK["default"]))
        random.shuffle(combined)
        # Return up to 30 hashtags (Instagram limit)
        return " ".join(combined[:30])

    def generate_ctas(self) -> list[str]:
        return random.sample(self.CTAS, k=len(self.CTAS))

    def generate_descriptions(self, topic: str) -> list[str]:
        topic = topic or "this topic"
        descriptions = []
        for _ in range(5):
            descriptions.append(f"Explore the ultimate guide to {topic}. " + random.choice(self.BODIES))
        return descriptions

    def generate_story_ideas(self, topic: str) -> list[str]:
        topic = topic or "your niche"
        templates = [
            f"Behind the scenes of working on {topic}",
            "A day in the life: The reality vs expectations",
            f"Poll: Do you struggle with {topic}? (Yes/No)",
            f"Q&A session about {topic} - Ask me anything!",
            "Customer spotlight / Testimonial screenshot",
            f"Quick tip of the day for {topic}",
            "Sneak peek of an upcoming project or product",
            "This or That interactive sticker game",
            "Mistake I made recently and what I learned",
            "Weekly recap / Friday wins"
        ]
        return templates

    def generate_reel_ideas(self, topic: str) -> list[str]:
        topic = topic or "your niche"
        templates = [
            f"3 Common myths about {topic} debunked (Pointing to text)",
            f"POV: You finally figure out {topic} (Trending audio)",
            f"Tutorial: How to achieve X in 3 simple steps",
            f"Before & After showcasing {topic} results",
            "Stop doing THIS if you want to succeed (Educational)",
            "Day 1 vs Day 100 progress timeline",
            f"The tools I use daily for {topic} (Screen recording)",
            "Pack an order with me / Process breakdown",
            "A quick hack that will save you hours",
            "Answering the most Googled questions about our industry"
        ]
        return templates

    def generate_calendar(self, topic: str) -> list[dict]:
        """Generates a 30-day content calendar."""
        content_types = ["Reel", "Carousel Post", "Single Image", "Story Sequence", "Reel"]
        themes = ["Educational", "Entertaining", "Inspirational", "Promotional", "Community"]
        
        calendar = []
        start_date = datetime.utcnow()
        
        for i in range(30):
            post_date = start_date + timedelta(days=i)
            ctype = content_types[i % len(content_types)]
            theme = themes[i % len(themes)]
            
            calendar.append({
                "day": i + 1,
                "date": post_date.strftime("%Y-%m-%d"),
                "type": ctype,
                "theme": theme,
                "idea": f"{theme} {ctype} focusing on {topic or 'brand awareness'}."
            })
        return calendar