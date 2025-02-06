import pygame
import pygame_gui

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
CARD_WIDTH, CARD_HEIGHT = 80, 120
HAND_Y = HEIGHT - 150
CARD_SPACING = 100
PLAY_AREA_CENTER = (WIDTH // 2, HEIGHT // 3)

# Colors
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
BLUE = (70, 130, 180)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Pygame Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Digital Card Game Mock-up")
clock = pygame.time.Clock()

# Pygame GUI Setup
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Player Info UI
health_bar = pygame_gui.elements.UIStatusBar(
    relative_rect=pygame.Rect((20, 20), (200, 25)),
    manager=manager,
    sprite=None
)
energy_bar = pygame_gui.elements.UIStatusBar(
    relative_rect=pygame.Rect((20, 50), (200, 25)),
    manager=manager,
    sprite=None
)
player_name = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 80), (200, 30)),
    text="Player: Hero",
    manager=manager
)

# Deck, Hand, and Discard Pile
deck_rect = pygame.Rect(20, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
discard_pile_rect = pygame.Rect(300, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
play_area_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 - 60, 200, 140)

# Generate a mock hand of 6 cards
hand = []
for i in range(6):
    hand.append({
        "rect": pygame.Rect(150 + i * CARD_SPACING, HAND_Y, CARD_WIDTH, CARD_HEIGHT),
        "color": GREEN,
        "text": f"Card {i+1}",
        "hover": False,
        "dragging": False,
        "original_pos": (150 + i * CARD_SPACING, HAND_Y),
        "tooltip": None
    })

# Card being played (None if no card in play area)
card_in_play = None
animation_active = False
animation_progress = 0.0

# Game loop
running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0

    # FILL BACKGROUND TO PREVENT BLACK SCREEN
    screen.fill(DARK_GRAY)

    # EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Fix window not closing issue

        # Handle Pygame GUI events
        manager.process_events(event)

        # Mouse Hover Tooltips
        for card in hand:
            if card["rect"].collidepoint(pygame.mouse.get_pos()):
                card["hover"] = True
                if not card["tooltip"]:
                    card["tooltip"] = pygame_gui.elements.UITooltip(card["text"], (10, 10), manager)
            else:
                card["hover"] = False
                if card["tooltip"]:
                    card["tooltip"].kill()
                    card["tooltip"] = None

        # Drag and Drop Events
        if event.type == pygame.MOUSEBUTTONDOWN:
            for card in hand:
                if card["rect"].collidepoint(event.pos):
                    card["dragging"] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            for card in hand:
                if card["dragging"]:
                    card["dragging"] = False
                    if play_area_rect.collidepoint(card["rect"].center):
                        # Snap to play area
                        card_in_play = card
                        card["rect"].center = PLAY_AREA_CENTER
                        animation_active = True
                        animation_progress = 0.0
                    else:
                        # Snap back to original position
                        card["rect"].topleft = card["original_pos"]

        elif event.type == pygame.MOUSEMOTION:
            for card in hand:
                if card["dragging"]:
                    card["rect"].move_ip(event.rel)

    # Update animation
    if animation_active and card_in_play:
        animation_progress += 0.02
        if animation_progress >= 1.0:
            animation_active = False
            # Move to discard pile
            card_in_play["rect"].topleft = discard_pile_rect.topleft
            card_in_play["original_pos"] = discard_pile_rect.topleft
            card_in_play = None

    # DRAW UI ELEMENTS
    pygame.draw.rect(screen, WHITE, deck_rect)  # Deck
    pygame.draw.rect(screen, WHITE, discard_pile_rect)  # Discard Pile
    pygame.draw.rect(screen, GRAY, play_area_rect)  # Play Area

    # Draw Cards in Hand
    for card in hand:
        pygame.draw.rect(screen, card["color"], card["rect"])
        font = pygame.font.Font(None, 24)
        text_surf = font.render(card["text"], True, WHITE)
        text_rect = text_surf.get_rect(center=card["rect"].center)
        screen.blit(text_surf, text_rect)

    # UPDATE PYGAME GUI
    manager.update(time_delta)
    manager.draw_ui(screen)

    # REFRESH SCREEN TO AVOID BLACK BACKGROUND
    pygame.display.flip()

pygame.quit()
