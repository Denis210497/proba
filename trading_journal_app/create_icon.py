from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 256x256 image with a white background
    size = 256
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a green/red candlestick chart icon
    margin = 40
    width = size - 2 * margin
    height = size - 2 * margin
    
    # Draw candlesticks
    candle_width = 30
    positions = [(78, 140, 180), (138, 80, 160), (198, 100, 140)]
    colors = ['#22bb33', '#bb2124', '#22bb33']
    
    for (x, top, bottom), color in zip(positions, colors):
        # Draw wick
        draw.line([(x, top-20), (x, bottom+20)], fill=color, width=2)
        # Draw candle body
        draw.rectangle([x-candle_width//2, top, x+candle_width//2, bottom], 
                      fill=color)
    
    # Save as ICO file
    image.save('app_icon.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon() 