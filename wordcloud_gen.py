import io
import re
from wordcloud import WordCloud, STOPWORDS
import numpy as np
from PIL import Image, ImageDraw

# Extra space/generic stopwords to filter out noise
CUSTOM_STOPWORDS = STOPWORDS | {
    "said", "will", "also", "new", "one", "two", "three",
    "first", "year", "years", "may", "can", "would", "could",
    "the", "a", "an", "to", "of", "in", "for", "on", "with",
    "at", "by", "from", "that", "this", "it", "is", "was",
    "are", "been", "be", "has", "have", "had", "which", "who",
    "its", "their", "they", "we", "us", "but", "or", "not",
    "about", "more", "than", "into", "after", "during", "through",
    "over", "up", "out", "as", "like", "so", "if", "when",
    "while", "just", "than", "then", "now", "made", "make",
}

# Skull palette for the outer shape
SKULL_COLORS = [
    "#f7f7f7",
    "#e6eef8",
    "#d7d7d7",
    "#bfd6ee",
    "#ffffff",
]

# Warmer palette for the brain interior
BRAIN_COLORS = [
    "#ff97a8",
    "#ff7b97",
    "#ffb3c1",
    "#ff8fab",
    "#ffd1dc",
]


def skull_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    import random
    rng = random_state or random.Random()
    return rng.choice(SKULL_COLORS)


def brain_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    import random
    rng = random_state or random.Random()
    return rng.choice(BRAIN_COLORS)


def _make_skull_and_brain_masks(width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    """Create masks for a skull silhouette and an inner brain region."""
    skull = Image.new("L", (width, height), 255)
    brain = Image.new("L", (width, height), 255)
    skull_draw = ImageDraw.Draw(skull)
    brain_draw = ImageDraw.Draw(brain)

    # Cranium dome plus a tapered facial structure for realistic cheekbones/jaw.
    skull_draw.ellipse((150, 70, 750, 610), fill=0)
    skull_draw.polygon(
        [
            (255, 470),
            (645, 470),
            (690, 560),
            (665, 760),
            (595, 860),
            (305, 860),
            (235, 760),
            (210, 560),
        ],
        fill=0,
    )
    skull_draw.rounded_rectangle((300, 620, 600, 860), radius=45, fill=0)

    # Temporal hollows and orbital cavities.
    skull_draw.ellipse((165, 265, 275, 430), fill=255)
    skull_draw.ellipse((625, 265, 735, 430), fill=255)
    skull_draw.ellipse((250, 275, 440, 500), fill=255)
    skull_draw.ellipse((460, 275, 650, 500), fill=255)

    # Brow bridge and nasal opening.
    skull_draw.rounded_rectangle((420, 315, 480, 420), radius=25, fill=0)
    skull_draw.polygon([(450, 470), (375, 620), (525, 620)], fill=255)
    skull_draw.ellipse((408, 520, 492, 610), fill=255)

    # Teeth and gaps.
    skull_draw.rectangle((320, 700, 580, 850), fill=0)
    for x in (352, 386, 420, 450, 480, 514, 548):
        skull_draw.rectangle((x, 712, x + 8, 848), fill=255)
    skull_draw.rectangle((300, 760, 600, 775), fill=255)

    # Brain volume inside the cranium.
    brain_draw.ellipse((245, 155, 655, 500), fill=0)
    brain_draw.ellipse((300, 130, 600, 465), fill=0)
    brain_draw.ellipse((365, 120, 535, 445), fill=0)

    # Midline fissure and soft gyri grooves for a brain-like texture.
    brain_draw.rounded_rectangle((442, 145, 458, 470), radius=8, fill=255)
    brain_draw.arc((280, 190, 430, 320), start=200, end=20, fill=255, width=10)
    brain_draw.arc((325, 230, 455, 360), start=200, end=25, fill=255, width=9)
    brain_draw.arc((280, 300, 430, 430), start=210, end=30, fill=255, width=9)
    brain_draw.arc((470, 190, 620, 320), start=160, end=340, fill=255, width=10)
    brain_draw.arc((445, 240, 575, 365), start=160, end=335, fill=255, width=9)
    brain_draw.arc((470, 300, 620, 430), start=155, end=330, fill=255, width=9)

    # Keep the brain layer away from eye sockets and lower face.
    brain_draw.ellipse((265, 290, 440, 505), fill=255)
    brain_draw.ellipse((460, 290, 635, 505), fill=255)
    brain_draw.rectangle((250, 500, 650, 880), fill=255)

    return np.array(skull), np.array(brain)


def generate_wordcloud(text: str) -> bytes:
    """
    Generate a word cloud PNG from `text`.
    Returns raw PNG bytes.
    """
    if not text or len(text.strip()) < 20:
        text = (
            "space NASA rocket satellite orbit moon Mars Jupiter "
            "telescope galaxy nebula cosmos astronaut mission launch "
            "SpaceX Artemis ISS lunar solar exoplanet star black hole"
        )

    # Clean text
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)

    skull_mask, brain_mask = _make_skull_and_brain_masks(900, 900)

    skull_wc = WordCloud(
        width=900,
        height=900,
        background_color=None,         # transparent bg
        mode="RGBA",
        stopwords=CUSTOM_STOPWORDS,
        max_words=240,
        mask=skull_mask,
        color_func=skull_color_func,
        prefer_horizontal=0.75,
        min_font_size=10,
        max_font_size=105,
        relative_scaling=0.5,
        collocations=True,
    ).generate(text)

    brain_wc = WordCloud(
        width=900,
        height=900,
        background_color=None,
        mode="RGBA",
        stopwords=CUSTOM_STOPWORDS,
        max_words=120,
        mask=brain_mask,
        color_func=brain_color_func,
        prefer_horizontal=0.85,
        min_font_size=8,
        max_font_size=72,
        relative_scaling=0.55,
        collocations=True,
    ).generate(text)

    # Composite onto a deep-space background
    skull_img = skull_wc.to_image().convert("RGBA")
    brain_img = brain_wc.to_image().convert("RGBA")
    bg = Image.new("RGBA", skull_img.size, (5, 5, 20, 255))  # very dark navy

    # Add subtle star-noise
    import random
    star_layer = Image.new("RGBA", skull_img.size, (0, 0, 0, 0))
    pixels = star_layer.load()
    rng = random.Random(42)
    for _ in range(1200):
        x = rng.randint(0, skull_img.width - 1)
        y = rng.randint(0, skull_img.height - 1)
        b = rng.randint(180, 255)
        pixels[x, y] = (b, b, b, rng.randint(120, 220))

    bg.alpha_composite(star_layer)
    bg.alpha_composite(skull_img)
    bg.alpha_composite(brain_img)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, format="PNG", optimize=True)
    return buf.getvalue()
