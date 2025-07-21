// Get canvas and context
const canvas = document.getElementById('mugCanvas');
const ctx = canvas.getContext('2d');

// Image elements
const mugImage = new Image();
// Using a more realistic mug image with a transparent background
mugImage.src = 'https://m.media-amazon.com/images/I/71CyPu9Ph+L._UF894,1000_QL80_.jpg';
const uploadedImage = new Image();

// Image properties for drawing
let uploadedImageLoaded = false;
let imageScale = 1.0;
let imageX = 0;
let imageY = 0;
let distortionStrength = 0.1; // Adjusted default for better initial look

// Dragging variables
let isDragging = false;
let dragStartX, dragStartY;
let initialImageX, initialImageY;

// Get input elements
const imageUpload = document.getElementById('imageUpload');
const scaleRange = document.getElementById('scaleRange');
const xOffsetRange = document.getElementById('xOffsetRange');
const yOffsetRange = document.getElementById('yOffsetRange');
const orderForm = document.getElementById('orderForm');
const messageBox = document.getElementById('messageBox');



// Function to draw everything on the canvas
function drawCanvas() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw mug image
    // Ensure the mug image covers the canvas appropriately
    ctx.drawImage(mugImage, 0, 0, canvas.width, canvas.height);

    // Draw uploaded image if loaded
    if (uploadedImageLoaded) {
        // Calculate target dimensions for the distorted image based on mug area
        // These values might need fine-tuning based on the specific mug image
        const mugPrintAreaWidth = canvas.width * 0.6; // Example: 60% of canvas width
        const mugPrintAreaHeight = canvas.height * 0.7; // Example: 70% of canvas height

        // Calculate scaled dimensions for the distorted image
        const scaledWidth = canvas.width * imageScale;
        const scaledHeight = canvas.height * imageScale;

        // Calculate position to center the image within the mug's print area, then apply offset
        const drawX = (canvas.width - scaledWidth) / 2 + imageX;
        const drawY = (canvas.height - scaledHeight) / 2 + imageY;

        ctx.drawImage(uploadedImage, drawX, drawY, scaledWidth, scaledHeight);
    }
}

// Event listener for mug image load
mugImage.onload = () => {
    drawCanvas(); // Draw mug once it's loaded
};

// Fallback for mug image if it fails to load
mugImage.onerror = () => {
    console.error("Failed to load mug image. Using a placeholder.");
    mugImage.src = 'https://placehold.co/500x400/ffffff/000000?text=Mug';
    mugImage.onload = drawCanvas; // Try drawing again with placeholder
};

// Event listener for image upload
imageUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImage.src = e.target.result;
            uploadedImage.onload = () => {
                uploadedImageLoaded = true;
                // Reset position and scale when new image is uploaded
                imageScale = 0.6; // Default scale for better initial fit
                imageX = 0;
                imageY = 0;
                scaleRange.value = 1.0;
                xOffsetRange.value = 0;
                yOffsetRange.value = 0;
                drawCanvas();
            };
        };
        reader.readAsDataURL(file);
    } else {
        showMessage('Please upload a valid image.', 'error');
        uploadedImageLoaded = false;
        uploadedImage.src = ''; // Clear image source
        drawCanvas(); // Redraw without the uploaded image
    }
});

// Event listeners for range sliders
scaleRange.addEventListener('input', (event) => {
    imageScale = parseFloat(event.target.value);
    drawCanvas();
});

xOffsetRange.addEventListener('input', (event) => {
    imageX = parseInt(event.target.value);
    drawCanvas();
});

yOffsetRange.addEventListener('input', (event) => {
    imageY = parseInt(event.target.value);
    drawCanvas();
});

distortionStrengthRange.addEventListener('input', (event) => {
    distortionStrength = parseFloat(event.target.value);
    drawCanvas();
});

// Mouse events for dragging the uploaded image on canvas
canvas.addEventListener('mousedown', (e) => {
    if (uploadedImageLoaded) {
        isDragging = true;
        const rect = canvas.getBoundingClientRect();
        dragStartX = e.clientX - rect.left;
        dragStartY = e.clientY - rect.top;
        initialImageX = imageX;
        initialImageY = imageY;
    }
});

canvas.addEventListener('mousemove', (e) => {
    if (isDragging && uploadedImageLoaded) {
        const rect = canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        imageX = initialImageX + (currentX - dragStartX);
        imageY = initialImageY + (currentY - dragStartY);
        xOffsetRange.value = imageX; // Update slider
        yOffsetRange.value = imageY; // Update slider
        drawCanvas();
    }
});

canvas.addEventListener('mouseup', () => {
    isDragging = false;
});

canvas.addEventListener('mouseout', () => {
    isDragging = false;
});

// Touch events for dragging the uploaded image on canvas
canvas.addEventListener('touchstart', (e) => {
    if (uploadedImageLoaded) {
        isDragging = true;
        const touch = e.touches[0];
        const rect = canvas.getBoundingClientRect();
        dragStartX = touch.clientX - rect.left;
        dragStartY = touch.clientY - rect.top;
        initialImageX = imageX;
        initialImageY = imageY;
        e.preventDefault(); // Prevent scrolling
    }
});

canvas.addEventListener('touchmove', (e) => {
    if (isDragging && uploadedImageLoaded) {
        const touch = e.touches[0];
        const rect = canvas.getBoundingClientRect();
        const currentX = touch.clientX - rect.left;
        const currentY = touch.clientY - rect.top;
        imageX = initialImageX + (currentX - dragStartX);
        imageY = initialImageY + (currentY - dragStartY);
        xOffsetRange.value = imageX; // Update slider
        yOffsetRange.value = imageY; // Update slider
        drawCanvas();
        e.preventDefault(); // Prevent scrolling
    }
});

canvas.addEventListener('touchend', () => {
    isDragging = false;
});

// Order form submission
orderForm.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission

    const customerName = document.getElementById('customerName').value;
    const customerEmail = document.getElementById('customerEmail').value;
    const quantity = document.getElementById('quantity').value;

    if (!uploadedImageLoaded) {
        showMessage('Please upload an image for your mug design before ordering.', 'error');
        return;
    }

    // In a real application, you would send this data to a backend server.
    // For this mockup, we'll just display a success message.
    console.log('Order Details:', {
        name: customerName,
        email: customerEmail,
        quantity: quantity,
        image: uploadedImage.src // In real app, send image data or URL
    });

    showMessage('Order placed successfully! We will contact you shortly.', 'success');
    orderForm.reset(); // Clear the form
    uploadedImageLoaded = false; // Clear the uploaded image
    uploadedImage.src = '';
    imageScale = 1.0; // Reset image properties
    imageX = 0;
    imageY = 0;
    scaleRange.value = 1.0;
    xOffsetRange.value = 0;
    yOffsetRange.value = 0;
    distortionStrengthRange.value = 0.1; // Reset distortion
    drawCanvas(); // Redraw canvas to clear design
});

// Function to show messages
function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`; // Apply success or error class
    messageBox.classList.remove('hidden');
    setTimeout(() => {
        messageBox.classList.add('hidden');
    }, 5000); // Hide after 5 seconds
}

// Initial draw when page loads
drawCanvas();