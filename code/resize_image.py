from pillow import Image

def resize_with_padding(image_path, max_size=600):
    # Open the image
    img = Image.open(image_path)
    
    # Get the original dimensions
    original_width, original_height = img.size
    
    # If the image is already smaller than max_size in both dimensions, center with white padding
    if original_width < max_size and original_height < max_size:
        # Create a new image with size (max_size, max_size)
        new_img = Image.new("1", (max_size, max_size), 0)  
        
        # Calculate the position to paste the original image at the center
        left = (max_size - original_width) // 2
        top = (max_size - original_height) // 2
        new_img.paste(img, (left, top))  # Paste the original image onto the new image
        
    else:
        # Calculate the scaling factor while maintaining aspect ratio
        scale_factor = min(max_size / original_width, max_size / original_height)
        
        # Calculate the new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Resize the image to the new dimensions
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        
        # Create a new image with size (max_size, max_size)
        new_img = Image.new("1", (max_size, max_size), 0) 
        
        # Calculate the position to paste the resized image at the center
        left = (max_size - new_width) // 2
        top = (max_size - new_height) // 2
        new_img.paste(img, (left, top))  # Paste the resized image onto the new image
    
    return new_img

# Example usage
image_path = "logo.jpg"  # Replace with your image path
result_image = resize_with_padding(image_path)

# Show the resulting image
result_image.show()

# Optionally, save the result
result_image.save("output_image.jpg")