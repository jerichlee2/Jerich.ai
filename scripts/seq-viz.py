import pygame
import pygame_gui
from latex2sympy2 import latex2sympy
from sympy import lambdify, symbols
from sympy import latex
import matplotlib.pyplot as plt
import io
from PIL import Image


# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1024, 768  # Window size
CANVAS_WIDTH = int(WIDTH * 0.67)  # Reserve 2/3 of the window width for the canvas
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
# Global declarations at the top of the file
sliders = {}
slider_labels = {}
slider_ranges = {}
slider_range_values = {}
max_n_slider = None
n_domain_input = None  # Add this global declaration

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sequence Visualization")

# Create a manager for UI elements
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create input box for LaTeX sequence
latex_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 50), (CANVAS_WIDTH - 100, 40)),
    manager=manager
)

# Font
font = pygame.font.SysFont(None, 24)

# Initialize sliders dictionary and input boxes
sliders = {}
slider_ranges = {}  # Dictionary to hold slider range input boxes
slider_range_values = {}  # Store the current range for comparison
max_n_slider = None  # Slider for maximum value of n
slider_labels = {}  # Dictionary to hold labels for each slider

def create_sliders(params):
    global sliders, max_n_slider, slider_labels, slider_ranges, slider_range_values, n_domain_input
    
    # Remove existing sliders and input boxes
    for slider in sliders.values():
        slider.kill()
    for input_box in slider_ranges.values():
        input_box.kill()
    if max_n_slider:
        max_n_slider.kill()
    if n_domain_input:
        n_domain_input.kill()

    # Reset any existing sliders and input boxes
    sliders = {}  # Clear old sliders
    slider_labels = {}  # Clear old slider labels
    new_slider_ranges = {}  # Temporary dictionary for new input boxes
    slider_height = 100  # Start height for sliders on the right-hand side
    domain_input_y = HEIGHT - 200  # Set the position for input boxes near the bottom

    for i, param in enumerate(params):
        # Create the input box for each slider's domain ([-x, x])
        if param in slider_ranges:
            # Preserve the old value if it exists
            current_value = slider_ranges[param].get_text()
        else:
            current_value = '5'  # Default range [-5, 5]
        
        new_slider_ranges[param] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((WIDTH - 160, domain_input_y), (100, 20)),
            manager=manager
        )
        new_slider_ranges[param].set_text(current_value)
        slider_range_values[param] = float(current_value)  # Preserve the old value in the range dictionary
        
        # Create the slider for each parameter
        sliders[param] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((CANVAS_WIDTH + 20, slider_height), (300, 20)),
            start_value=0.0,
            value_range=(-slider_range_values[param], slider_range_values[param]),  # Set range from preserved value
            manager=manager
        )
        
        # Create the label for each parameter slider (initial value will be 0), using pygame font rendering
        slider_labels[param] = font.render(f'{str(param)}: {sliders[param].get_current_value():.2f}', True, BLACK)
        
        slider_height += 50  # Stack sliders vertically
        domain_input_y += 30  # Stack domain inputs vertically from the bottom

    slider_ranges.update(new_slider_ranges)  # Update the main slider_ranges dictionary

    # Create a label and slider for max_n (range of n)
    max_n_label = font.render('max_n:', True, BLACK)
    screen.blit(max_n_label, (CANVAS_WIDTH + 20, slider_height - 30))  # Label above the slider
    
    max_n_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((CANVAS_WIDTH + 20, slider_height), (300, 20)),
        start_value=100,
        value_range=(10, 200),  # Set the range for n, adjust as necessary
        manager=manager
    )
    
    # Add input box for custom n domain
    n_domain_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((WIDTH - 160, domain_input_y + 30), (100, 20)),
        manager=manager
    )
    n_domain_input.set_text('200')  # Default n-domain value
def update_slider_labels(params):
    # Update slider labels with the current value of each slider
    for param in params:
        slider_labels[param] = font.render(f'{str(param)}: {sliders[param].get_current_value():.2f}', True, BLACK)
def update_slider_range(param):
    try:
        x = float(slider_ranges[param].get_text())
    except ValueError:
        x = slider_range_values.get(param, 5)  # Default to 5 if input is invalid

    # Check if the range has changed
    if slider_range_values[param] != x:
        slider_range_values[param] = x  # Update stored value

        # Remove the existing slider
        sliders[param].kill()

        # Recreate the slider with the new range
        sliders[param] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=sliders[param].rect,  # Use the same position
            start_value=0.0,
            value_range=(-x, x),  # Set the new range
            manager=manager
        )

def draw_sequence(func, params):
    # Update slider ranges based on input
    for param in params:
        update_slider_range(param)

    # Prepare parameter values from sliders, converting SymPy symbols to strings
    param_values = {str(param): sliders[param].get_current_value() for param in params}
    
    # Get max_n from the slider
    max_n = max_n_slider.get_current_value()
    
    # Clear the canvas area (left side)
    pygame.draw.rect(screen, WHITE, (0, 100, CANVAS_WIDTH, HEIGHT - 100))
    
    # Draw axes on the canvas area
    pygame.draw.line(screen, BLACK, (50, HEIGHT - 150), (CANVAS_WIDTH - 50, HEIGHT - 150))  # X-axis
    pygame.draw.line(screen, BLACK, (50, HEIGHT // 2), (50, 100))  # Y-axis centered
    
    # Draw x and y axis labels
    x_label = font.render('n', True, BLACK)
    y_label = font.render('Sequence Value', True, BLACK)
    screen.blit(x_label, (CANVAS_WIDTH - 60, HEIGHT - 160))  # X-axis label
    screen.blit(y_label, (10, 110))  # Y-axis label
    
    # Calculate the sequence value at max_n and update the label
    try:
        sequence_value_at_max_n = func(max_n, **param_values)
        max_n_label_text = font.render(f'max_n: {int(max_n)} (Value: {sequence_value_at_max_n:.2f})', True, BLACK)
        screen.blit(max_n_label_text, (CANVAS_WIDTH + 20, max_n_slider.rect.top - 30))  # Update max_n label
    except ZeroDivisionError:
        # Handle zero division by displaying a warning or skipping drawing this value
        sequence_value_at_max_n = float('inf')
        max_n_label_text = font.render(f'max_n: {int(max_n)} (Value: undefined)', True, BLACK)
        screen.blit(max_n_label_text, (CANVAS_WIDTH + 20, max_n_slider.rect.top - 30))

    # Draw sequence with adjusted scaling for negative values
    for n in range(1, int(max_n) + 1):
        x = 50 + n * (CANVAS_WIDTH - 100) / max_n
        try:
            y_value = func(n, **param_values)
            y = (HEIGHT // 2) - y_value * 10  # Scale output and center y around the middle of the canvas
            
            # Convert float to int for drawing the circle
            if 0 <= x < CANVAS_WIDTH and 100 <= y < HEIGHT - 100:  # Ensure points are within the canvas bounds
                pygame.draw.circle(screen, BLUE, (int(x), int(y)), 3)
        except ZeroDivisionError:
            # Skip drawing this point if division by zero occurs
            continue
# Function to convert LaTeX input to Python function
def process_latex_input(latex_input_str):
    try:
        # Convert LaTeX to sympy-compatible expression using latex2sympy
        sympy_expr = latex2sympy(latex_input_str)
    except Exception as e:
        print(f"Failed to parse LaTeX: {e}")
        return None, []

    # Identify free symbols (parameters)
    params = list(sympy_expr.free_symbols)  # Extract parameters
    n = symbols('n')  # Assume 'n' is the main variable
    
    # Ensure 'n' is not treated as a parameter
    if n in params:
        params.remove(n)

    # Create a Python function from the sympy expression
    func = lambdify([n] + params, sympy_expr)
    
    # Generate sliders for the parameters
    create_sliders(params)
    
    return func, params

def main():
    clock = pygame.time.Clock()
    running = True
    sequence_func = None
    params = []

    while running:
        time_delta = clock.tick(60) / 1000.0  # Control the frame rate

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Process text input events
            manager.process_events(event)

            # Check if the user has pressed enter to process the LaTeX input
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                latex_input_str = latex_input.get_text()  # Get the LaTeX input
                sequence_func, params = process_latex_input(latex_input_str)  # Parse input

        # Update the UI manager
        manager.update(time_delta)

        # Clear the screen before drawing
        screen.fill(WHITE)

        # If a sequence function is defined, visualize it
        if sequence_func:
            draw_sequence(sequence_func, params)

        # Update the slider labels to reflect current values
        update_slider_labels(params)

        # Draw the UI elements (including sliders and text entry)
        manager.draw_ui(screen)

        # Draw slider labels
        for param, label in slider_labels.items():
            screen.blit(label, (CANVAS_WIDTH + 20, sliders[param].rect.top - 30))  # Position the labels above sliders

        if max_n_slider:
            screen.blit(font.render('max_n:', True, BLACK), (CANVAS_WIDTH + 20, max_n_slider.rect.top - 30))

        # Update the display (flip only once at the end of each frame)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()