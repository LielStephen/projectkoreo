import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, font
from PIL import Image, ImageTk
import os

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

BG_COLOR = "#FFF5F5"
ACCENT_COLOR = "#FF6B6B"
BUTTON_COLOR = "#FF8B8B"
BUTTON_HOVER = "#FF6B6B"
TEXT_COLOR = "#4A4A4A"
FRAME_BG = "#FFFFFF"
TITLE_COLOR = "#FF4757"
SECTION_BG = "#FFE8E8"
SWATCH_BORDER = "#FF8B8B"
ANTI_RACISM_BG = "#1E1E1E"
ANTI_RACISM_TEXT = "#FFFFFF"

FONT_FAMILY = "Segoe UI"
FONT_SIZE_TITLE = 28
FONT_SIZE_HEADER = 18
FONT_SIZE_NORMAL = 13
FONT_SIZE_SMALL = 11

def load_custom_font_safe(size_map):
    """Safely loads custom fonts with fallbacks."""
    font_objects = {}
    fallback_fonts = [
        "Segoe UI",
        "Arial",
        "Helvetica",
        "Tahoma",
        "Verdana"
    ]
    
    for role, size in size_map.items():
        found_font = False
        for f_name in fallback_fonts:
            try:
                if role == "title":
                    font_objects[role] = font.Font(family=f_name, size=size, weight="bold")
                elif role == "header":
                    font_objects[role] = font.Font(family=f_name, size=size, weight="bold")
                else:
                    font_objects[role] = font.Font(family=f_name, size=size)
                found_font = True
                break
            except Exception:
                continue
        if not found_font:
            font_objects[role] = font.Font(family="System", size=size)
    return font_objects

def get_average_skin_color(image_path):
    img = cv2.imread(image_path)
    if img is None:
        messagebox.showerror("Error", "Could not load image. Please check the path.")
        return None, None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        return None, img

    (x, y, w, h) = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]

    skin_roi_x = x + int(w * 0.3)
    skin_roi_y = y + int(h * 0.2)
    skin_roi_w = int(w * 0.4)
    skin_roi_h = int(h * 0.3)

    skin_roi_x = max(0, skin_roi_x)
    skin_roi_y = max(0, skin_roi_y)
    skin_roi_w = min(skin_roi_w, img.shape[1] - skin_roi_x)
    skin_roi_h = min(skin_roi_h, img.shape[0] - skin_roi_y)

    if skin_roi_w <= 0 or skin_roi_h <= 0:
        return None, img

    skin_region = img[skin_roi_y:skin_roi_y + skin_roi_h, skin_roi_x:skin_roi_x + skin_roi_w]

    average_bgr = np.mean(skin_region, axis=(0, 1))

    average_rgb = (int(average_bgr[2]), int(average_bgr[1]), int(average_bgr[0]))

    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.rectangle(img, (skin_roi_x, skin_roi_y), (skin_roi_x + skin_roi_w, skin_roi_y + skin_roi_h), (0, 255, 0), 2)

    return average_rgb, img

def classify_skin_tone(average_rgb):
    if average_rgb is None:
        return "Unknown"

    r, g, b = average_rgb

    hsv = cv2.cvtColor(np.array([[average_rgb]], dtype=np.uint8), cv2.COLOR_RGB2HSV)[0][0]
    hue, saturation, value = hsv[0], hsv[1], hsv[2]

    warm_cool_score = (r - b) * 0.7 + (g - b) * 0.3

    if hue <= 20 or hue >= 160:
        warm_cool = "Warm"
    elif hue >= 80 and hue <= 140:
        warm_cool = "Cool"
    elif warm_cool_score > 20:
        warm_cool = "Warm"
    elif warm_cool_score < -20:
        warm_cool = "Cool"
    else:
        warm_cool = "Warm" if r > b else "Cool"

    if value > 180:
        light_dark = "Light"
    elif value > 100:
        light_dark = "Medium"
    else:
        light_dark = "Dark"

    return f"{warm_cool} {light_dark}"

COLOR_PALETTES = {
    "Warm Light": [
        "#FFDAB9", "#FFDEAD", "#F0E68C", "#BDB76B", "#D2B48C",
        "#FFE4C4", "#FFA07A", "#FF7F50", "#EE82EE", "#ADD8E6"
    ],
    "Warm Medium": [
        "#CD853F", "#A0522D", "#D2691E", "#B8860B", "#DAA520",
        "#FF8C00", "#FF4500", "#DC143C", "#8B0000", "#4B0082"
    ],
    "Warm Dark": [
        "#8B4513", "#694025", "#3D2B1F", "#556B2F", "#A52A2A",
        "#C04000", "#800000", "#6B8E23", "#483C32", "#2F4F4F"
    ],
    "Cool Light": [
        "#E0FFFF", "#AFEEEE", "#B0C4DE", "#ADD8E6", "#DDA0DD",
        "#C6E2FF", "#B0E0E6", "#87CEEB", "#6A5ACD", "#D8BFD8"
    ],
    "Cool Medium": [
        "#4682B4", "#6A5ACD", "#483D8B", "#4169E1", "#87CEEB",
        "#5F9EA0", "#20B2AA", "#7B68EE", "#48D1CC", "#663399"
    ],
    "Cool Dark": [
        "#191970", "#000080", "#0000CD", "#00008B", "#008B8B",
        "#006400", "#483D8B", "#8A2BE2", "#4B0082", "#2F4F4F"
    ],
    "Unknown": [
        "#CCCCCC", "#AAAAAA", "#888888", "#666666", "#444444"
    ]
}

OUTFIT_RECOMMENDATIONS = {
    "Warm Light": {
        "vibe": "Soft, natural, and friendly. Emphasize comfort and subtle elegance.",
        "styles": [
            "Pastel Korean Minimalist: Oversized knit cardigans in cream or peach, flowy white blouses, light wash denim, beige wide-leg pants.",
            "Cozy Casual: Soft cotton t-shirts in earthy tones (light olive, terracotta), relaxed-fit beige trousers, layered with a light brown shacket.",
            "Feminine Chic: Floral dresses with small prints in warm pastels (like coral or light yellow), paired with delicate gold accessories and white sneakers or espadrilles.",
            "Autumnal Comfort: Muted orange or mustard yellow sweaters, corduroy skirts in warm neutrals, simple loafers or ankle boots."
        ]
    },
    "Warm Medium": {
        "vibe": "Earthy, vibrant, and approachable. Embrace rich, inviting colors.",
        "styles": [
            "Urban Comfy: Caramel or brick-red oversized hoodies, charcoal grey joggers, chunky sneakers, and a practical cross-body bag.",
            "Smart Casual: Structured blazers in deep olive green or warm brown, cream mock-neck tops, tailored straight-leg jeans, and leather loafers.",
            "Bohemian Touch: Flowy maxi skirts in burnt orange or rust, peasant blouses with embroidery, layered with denim jackets, and stacked bracelets.",
            "Sophisticated Everyday: Deep teal or mustard yellow knit sweaters, dark wash jeans or tailored trousers, simple gold jewelry, and sleek ankle boots."
        ]
    },
    "Warm Dark": {
        "vibe": "Rich, grounded, and striking. Focus on depth and bold natural tones.",
        "styles": [
            "Elegant and Bold: Deep burgundy or forest green velvet skirts, black high-neck tops, long trench coats in camel or dark brown, and statement gold earrings.",
            "Modern Athleisure: Dark olive green oversized hoodies, black cargo pants, high-top sneakers, and a sleek backpack.",
            "Power Minimalist: Tailored suits in deep brown or charcoal, paired with a simple black or cream top, and minimalist silver or gold accents.",
            "Dramatic Layering: Deep rust-colored oversized coat, black culottes, chunky knit sweater in a rich mustard, and robust boots."
        ]
    },
    "Cool Light": {
        "vibe": "Bright, fresh, and serene. Ideal for soft, delicate shades.",
        "styles": [
            "Spring Pastel Aesthetic: Lavender, mint green, or sky blue knit sweaters, pleated midi skirts in white or light grey, and white sneakers.",
            "Clean & Crisp: White blouses with delicate details, light blue denim, pastel blazers (e.g., light pink or baby blue), and silver accessories.",
            "Understated Elegance: Soft grey tailored trousers, a crisp white shirt, layered with a light periwinkle or powder blue cardigan, and subtle silver jewelry.",
            "Dreamy Feminine: Flowy dresses in light cool tones (e.g., dusty rose, light teal), paired with delicate sandals or ballet flats, and a pearl necklace."
        ]
    },
    "Cool Medium": {
        "vibe": "Vibrant, refreshing, and chic. Embrace clear, jewel-toned colors.",
        "styles": [
            "Dynamic Casual: Royal blue or emerald green graphic tees, black wide-leg pants, white sneakers, and a bold colored beanie.",
            "Sophisticated Professional: Navy blue blazers, crisp white button-downs, charcoal grey pencil skirts or trousers, and silver watch.",
            "Modern Artsy: Deep plum or forest green oversized tunics, black leggings, chunky platform shoes, and unique statement earrings.",
            "Sporty Chic: Cobalt blue track jackets, black athletic leggings, white sneakers, and a minimalist black backpack."
        ]
    },
    "Cool Dark": {
        "vibe": "Dramatic, intense, and elegant. Command attention with deep, rich hues.",
        "styles": [
            "Edgy Urban: Black leather jackets, dark wash slim-fit jeans, deep sapphire blue tops, and chunky combat boots.",
            "Glamorous Evening: Emerald green or royal blue satin slip dresses, paired with a black oversized blazer, and silver heels.",
            "Powerful Minimalist: Tailored black suits, crisp white shirts, long dark grey coats, and bold silver jewelry.",
            "Winter Warmth: Deep burgundy or forest green chunky knit sweaters, black denim, and dark-colored ankle boots, accessorized with a dark scarf."
        ]
    },
    "Unknown": {
        "vibe": "Neutral and versatile. Focus on classic Korean fashion staples.",
        "styles": [
            "Classic Neutrals: Black, white, grey, and navy combinations. Think oversized hoodies, simple tees, wide-leg pants, and minimalist sneakers.",
            "Denim Focused: Various washes of denim (light, medium, dark) paired with white or black tops. Add a pop of color with accessories.",
            "Layering Basics: Essential t-shirts, basic sweaters, and versatile outerwear (trench coats, denim jackets) in neutral tones.",
            "Comfort Chic: Loose-fitting clothing in comfortable fabrics like cotton and linen. Focus on silhouettes and simple patterns."
        ]
    }
}

class OutfitRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korean Outfit Recommender")
        self.root.geometry("800x750")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.fonts = load_custom_font_safe({
            "title": FONT_SIZE_TITLE,
            "header": FONT_SIZE_HEADER,
            "normal": FONT_SIZE_NORMAL,
            "small": FONT_SIZE_SMALL
        })

        self.image_path = None

        main_container = tk.Frame(root, bg=BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = tk.Label(main_container,
                             text="Korean Fashion Color Analysis",
                             font=self.fonts["title"],
                             bg=BG_COLOR,
                             fg=TITLE_COLOR)
        title_label.pack(pady=(0, 20))

        image_frame = tk.Frame(main_container, bg=FRAME_BG, bd=2, relief="solid")
        image_frame.pack(fill="x", pady=(0, 20))
        
        self.image_label = tk.Label(image_frame,
                                  text="Upload an image to get started!",
                                  font=self.fonts["normal"],
                                  bg=FRAME_BG,
                                  fg=TEXT_COLOR)
        self.image_label.pack(pady=20)

        self.upload_button = tk.Button(main_container,
                                     text="Upload Image",
                                     command=self.load_image,
                                     font=self.fonts["normal"],
                                     bg=BUTTON_COLOR,
                                     fg="white",
                                     activebackground=BUTTON_HOVER,
                                     activeforeground="white",
                                     relief="flat",
                                     padx=20,
                                     pady=10)
        self.upload_button.pack(pady=(0, 20))

        self.skin_tone_label = tk.Label(main_container,
                                      text="Detected Skin Tone: N/A",
                                      font=self.fonts["header"],
                                      bg=BG_COLOR,
                                      fg=TITLE_COLOR)
        self.skin_tone_label.pack(pady=(0, 20))

        self.color_frame = tk.Frame(main_container,
                                  bg=SECTION_BG,
                                  bd=2,
                                  relief="solid",
                                  padx=15,
                                  pady=15)
        self.color_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(self.color_frame,
                text="Recommended Colors:",
                font=self.fonts["normal"],
                bg=SECTION_BG,
                fg=TITLE_COLOR).pack(pady=(0, 10))
        
        self.color_swatches = []
        swatch_frame = tk.Frame(self.color_frame, bg=SECTION_BG)
        swatch_frame.pack()
        
        for _ in range(8):
            swatch = tk.Label(swatch_frame,
                            width=5,
                            height=2,
                            relief="solid",
                            bd=1,
                            bg=FRAME_BG,
                            highlightbackground=SWATCH_BORDER,
                            highlightthickness=1)
            swatch.pack(side="left", padx=5, pady=5)
            self.color_swatches.append(swatch)

        self.outfit_frame = tk.Frame(main_container,
                                   bg=SECTION_BG,
                                   bd=2,
                                   relief="solid",
                                   padx=15,
                                   pady=15)
        self.outfit_frame.pack(fill="both", expand=True)
        
        tk.Label(self.outfit_frame,
                text="Outfit Suggestions (Korean Fashion Inspired):",
                font=self.fonts["normal"],
                bg=SECTION_BG,
                fg=TITLE_COLOR).pack(anchor="nw", pady=(0, 10))
        
        self.outfit_vibe_label = tk.Label(self.outfit_frame,
                                        text="",
                                        wraplength=700,
                                        justify="left",
                                        font=self.fonts["small"],
                                        bg=SECTION_BG,
                                        fg=TEXT_COLOR)
        self.outfit_vibe_label.pack(anchor="nw", pady=(0, 10))
        
        self.outfit_text = tk.Label(self.outfit_frame,
                                  text="",
                                  wraplength=700,
                                  justify="left",
                                  font=self.fonts["small"],
                                  bg=SECTION_BG,
                                  fg=TEXT_COLOR)
        self.outfit_text.pack(anchor="nw")

        anti_racism_frame = tk.Frame(root, bg=ANTI_RACISM_BG, height=50)
        anti_racism_frame.pack(fill="x", side="bottom")
        
        message_parts = [
            ("NO", "#FF0000"),
            (" TO ", "#FFFFFF"),
            ("RACISM", "#FFD700"),
            (" - ", "#FFFFFF"),
            ("EVERY", "#00FF00"),
            (" SKIN ", "#FFFFFF"),
            ("TONE", "#FF69B4"),
            (" IS ", "#FFFFFF"),
            ("BEAUTIFUL", "#4169E1")
        ]
        
        message_frame = tk.Frame(anti_racism_frame, bg=ANTI_RACISM_BG)
        message_frame.pack(expand=True)
        
        for text, color in message_parts:
            label = tk.Label(message_frame,
                           text=text,
                           font=self.fonts["header"],
                           bg=ANTI_RACISM_BG,
                           fg=color)
            label.pack(side="left", padx=2)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if not file_path:
            return

        self.image_path = file_path
        self.process_image()

    def process_image(self):
        if not self.image_path:
            return

        average_rgb, display_img_cv = get_average_skin_color(self.image_path)
        skin_tone = classify_skin_tone(average_rgb)

        self.skin_tone_label.config(text=f"Detected Skin Tone: {skin_tone}")

        if display_img_cv is not None:
            display_img_rgb = cv2.cvtColor(display_img_cv, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(display_img_rgb)
            pil_image.thumbnail((300, 300))
            self.tk_image = ImageTk.PhotoImage(pil_image)
            self.image_label.config(image=self.tk_image)
        else:
            self.image_label.config(text="Could not process image or detect face.", image='')
            self.tk_image = None

        colors = COLOR_PALETTES.get(skin_tone, COLOR_PALETTES["Unknown"])
        for i, swatch in enumerate(self.color_swatches):
            if i < len(colors):
                swatch.config(bg=colors[i], relief="raised")
            else:
                swatch.config(bg="lightgray", relief="flat")

        recommendations = OUTFIT_RECOMMENDATIONS.get(skin_tone, OUTFIT_RECOMMENDATIONS["Unknown"])
        self.outfit_vibe_label.config(text=f"Vibe: {recommendations['vibe']}")
        self.outfit_text.config(text="\n".join([f"- {s}" for s in recommendations['styles']]))

if __name__ == "__main__":
    root = tk.Tk()
    app = OutfitRecommenderApp(root)
    root.mainloop()
