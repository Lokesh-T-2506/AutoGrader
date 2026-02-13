from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image():
    # Create a white background
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Text to "handwrite"
    lines = [
        "Calculus Quiz 1",
        "Problem: Integrate x^2",
        "Solution:",
        "The integral of x^2 is (x^3)/3 + C.",
        "Checked by d/dx((x^3)/3) = x^2."
    ]
    
    # Try to find a font, fallback to default
    try:
        # Common Windows paths for fonts
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    y_text = 50
    for line in lines:
        draw.text((50, y_text), line, font=font, fill=(50, 50, 50)) # Dark grey for "pencil" look
        y_text += 50
    
    # Ensure directory exists
    output_dir = "c:/Users/tallu/OneDrive/Desktop/AutoGrader/backend/uploads"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "sample_submission.png")
    image.save(output_path)
    print(f"Sample image created at: {output_path}")

if __name__ == "__main__":
    create_sample_image()
