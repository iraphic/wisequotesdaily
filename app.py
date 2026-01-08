import os
import random
import requests
import io
import textwrap
from flask import Flask, render_template, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Configuration
API_URL = "https://api.api-ninjas.com/v1/quotes"
API_KEY = "9zAnv7rg3z+Re3XeiyrFjg==DQRDaDt5Ln0kQm7w"
TARGET_CATEGORIES = ['success', 'wisdom', 'life', 'inspirational', 'happiness', 'future']

# Paths to assets (Must be placed in static folder by user)
IMAGE_TEMPLATE_PATH = os.path.join('static', 'nokia_blank.png')
FONT_PATH = os.path.join('static', 'pixel_font.ttf')

def get_quote():
    category = random.choice(TARGET_CATEGORIES)
    headers = {'X-Api-Key': API_KEY}
    try:
        response = requests.get(f"{API_URL}?category={category}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['quote'], data[0]['author']
    except Exception as e:
        print(f"Error fetching quote: {e}")
    return "Life is simple, but we insist on making it complicated.", "Confucius"

def create_image(quote_text, author):
    try:
        # Open the template
        if not os.path.exists(IMAGE_TEMPLATE_PATH):
            return None, "Template image not found. Please upload 'nokia_blank.png' to the static folder."
        
        img = Image.open(IMAGE_TEMPLATE_PATH)
        draw = ImageDraw.Draw(img)

        # Load font
        font_size = 20  # Adjust as needed based on image resolution
        try:
            if os.path.exists(FONT_PATH):
                font = ImageFont.truetype(FONT_PATH, font_size)
            else:
                # Fallback to default if custom font is missing
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # Text configuration
        # Assuming the text area is roughly in the middle. 
        # Need to adjust these coordinates based on the actual nokia_blank.png
        # Based on typical Nokia 3310/similar screens:
        # Screen width is small. Let's assume the image is around 300-400px wide?
        # I'll use a safe margin.
        
        img_w, img_h = img.size
        margin_x = 20
        margin_y = 80 # Below header "Create memo"
        max_width = img_w - (margin_x * 2)
        
        # approximate character width for wrapping (pillow textlength is better but simple wrap works)
        # For pixel fonts, char width is often constant or close to it.
        # Let's try to wrap based on pixel width.
        
        lines = []
        words = quote_text.split()
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        # Draw text
        y = margin_y
        line_height = bbox[3] - bbox[1] + 5 # Add some padding
        
        # Color: Black text
        text_color = (0, 0, 0)
        
        for line in lines:
            draw.text((margin_x, y), line, font=font, fill=text_color)
            y += line_height
            
        # Optional: Draw author at the bottom or below text
        # y += 10
        # draw.text((margin_x, y), f"- {author}", font=font, fill=text_color)

        # Save to buffer
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return img_io, None

    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    quote, author = get_quote()
    img_io, error = create_image(quote, author)
    
    if error:
        return jsonify({'error': error}), 400
        
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
