import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Math Challenge Game Suite")
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 48)

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = font
   
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
   
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
       
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.val = max(self.min_val, min(self.max_val, self.val))
   
    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, GRAY, self.rect)
        # Draw slider handle
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(surface, BLUE, handle_rect)
        # Draw label and value
        label_surface = small_font.render(f"{self.label}: {self.val:.3f}", True, BLACK)
        surface.blit(label_surface, (self.rect.x, self.rect.y - 25))

class ScatterPlotGame:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
        self.score = 0
        self.total_questions = 0
        self.current_point = None
        self.input_x = ""
        self.input_y = ""
        self.input_active = "x"
        self.feedback = ""
        self.feedback_timer = 0
        
        # Set graph bounds based on difficulty BEFORE generating point
        if difficulty == 1:
            self.graph_bounds = 10
        elif difficulty == 2:
            self.graph_bounds = 20
        else:
            self.graph_bounds = 50
            
        self.generate_new_point()
   
    def generate_new_point(self):
        self.current_point = (
            random.randint(-self.graph_bounds, self.graph_bounds),
            random.randint(-self.graph_bounds, self.graph_bounds)
        )
        self.input_x = ""
        self.input_y = ""
        self.input_active = "x"
   
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.input_active = "y" if self.input_active == "x" else "x"
            elif event.key == pygame.K_BACKSPACE:
                if self.input_active == "x":
                    self.input_x = self.input_x[:-1]
                else:
                    self.input_y = self.input_y[:-1]
            elif event.key == pygame.K_RETURN:
                self.check_answer()
            elif event.unicode.isdigit() or event.unicode == '-':
                if self.input_active == "x":
                    self.input_x += event.unicode
                else:
                    self.input_y += event.unicode
   
    def check_answer(self):
        try:
            user_x = int(self.input_x) if self.input_x else 0
            user_y = int(self.input_y) if self.input_y else 0
           
            if user_x == self.current_point[0] and user_y == self.current_point[1]:
                self.score += 1
                self.feedback = "Correct!"
            else:
                self.feedback = f"Wrong! Answer: ({self.current_point[0]}, {self.current_point[1]})"
           
            self.total_questions += 1
            self.feedback_timer = 120  # 2 seconds at 60 FPS
            self.generate_new_point()
        except ValueError:
            self.feedback = "Please enter valid numbers"
            self.feedback_timer = 60
   
    def update(self):
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
   
    def draw(self, surface):
        surface.fill(WHITE)
       
        # Draw graph
        graph_x, graph_y = 50, 50
        graph_width, graph_height = 500, 400
       
        # Draw graph background
        pygame.draw.rect(surface, LIGHT_GRAY, (graph_x, graph_y, graph_width, graph_height))
       
        # Draw grid lines
        grid_spacing = max(1, self.graph_bounds // 5)
        for i in range(-self.graph_bounds, self.graph_bounds + 1, grid_spacing):
            x = graph_x + graph_width // 2 + (i * graph_width) // (2 * self.graph_bounds)
            y = graph_y + graph_height // 2 - (i * graph_height) // (2 * self.graph_bounds)
           
            if x >= graph_x and x <= graph_x + graph_width:
                pygame.draw.line(surface, GRAY, (x, graph_y), (x, graph_y + graph_height), 1)
            if y >= graph_y and y <= graph_y + graph_height:
                pygame.draw.line(surface, GRAY, (graph_x, y), (graph_x + graph_width, y), 1)
       
        # Draw axes
        center_x = graph_x + graph_width // 2
        center_y = graph_y + graph_height // 2
        pygame.draw.line(surface, BLACK, (center_x, graph_y), (center_x, graph_y + graph_height), 2)
        pygame.draw.line(surface, BLACK, (graph_x, center_y), (graph_x + graph_width, center_y), 2)
       
        # Draw current point
        if self.current_point[0] >= -self.graph_bounds and self.current_point[0] <= self.graph_bounds:
            if self.current_point[1] >= -self.graph_bounds and self.current_point[1] <= self.graph_bounds:
                point_x = center_x + (self.current_point[0] * graph_width) // (2 * self.graph_bounds)
                point_y = center_y - (self.current_point[1] * graph_height) // (2 * self.graph_bounds)
                pygame.draw.circle(surface, RED, (point_x, point_y), 8)
       
        # Draw UI
        title = large_font.render(f"Scatter Plot Game - Difficulty {self.difficulty}", True, BLACK)
        surface.blit(title, (600, 50))
       
        score_text = font.render(f"Score: {self.score}/{self.total_questions}", True, BLACK)
        surface.blit(score_text, (600, 100))
       
        # Input boxes
        x_label = font.render("X coordinate:", True, BLACK)
        surface.blit(x_label, (600, 150))
        x_color = BLUE if self.input_active == "x" else LIGHT_GRAY
        pygame.draw.rect(surface, x_color, (600, 180, 150, 30), 2)
        x_text = font.render(self.input_x, True, BLACK)
        surface.blit(x_text, (605, 185))
       
        y_label = font.render("Y coordinate:", True, BLACK)
        surface.blit(y_label, (600, 230))
        y_color = BLUE if self.input_active == "y" else LIGHT_GRAY
        pygame.draw.rect(surface, y_color, (600, 260, 150, 30), 2)
        y_text = font.render(self.input_y, True, BLACK)
        surface.blit(y_text, (605, 265))
       
        # Instructions
        instructions = [
            "Click on a coordinate point and",
            "enter its (x, y) coordinates.",
            "Use TAB to switch between fields",
            "Press ENTER to submit"
        ]
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, BLACK)
            surface.blit(text, (600, 320 + i * 20))
       
        # Feedback
        if self.feedback_timer > 0:
            feedback_color = GREEN if "Correct" in self.feedback else RED
            feedback_surface = font.render(self.feedback, True, feedback_color)
            surface.blit(feedback_surface, (600, 420))

class AlgebraGame:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
        self.score = 0
        self.total_questions = 0
        self.current_problem = None
        self.current_answer = None
        self.input_answer = ""
        self.feedback = ""
        self.feedback_timer = 0
        self.generate_new_problem()
   
    def generate_new_problem(self):
        if self.difficulty == 1:
            # One-step problems with small numbers
            num_range = 20
            problem_type = random.choice(["add", "subtract", "multiply", "divide"])
        elif self.difficulty == 2:
            # Two-step problems with medium numbers
            num_range = 50
            problem_type = random.choice(["two_step_add", "two_step_mult"])
        else:
            # Complex problems with large numbers
            num_range = 100
            problem_type = random.choice(["two_step_add", "two_step_mult", "complex"])
       
        x = random.randint(1, num_range)
       
        if problem_type == "add":
            b = random.randint(-num_range, num_range)
            self.current_problem = f"x + {b} = {x + b}"
            self.current_answer = x
        elif problem_type == "subtract":
            b = random.randint(-num_range, num_range)
            self.current_problem = f"x - {b} = {x - b}"
            self.current_answer = x
        elif problem_type == "multiply":
            b = random.randint(2, 10)
            self.current_problem = f"{b}x = {b * x}"
            self.current_answer = x
        elif problem_type == "divide":
            b = random.randint(2, 10)
            self.current_problem = f"x / {b} = {x}"
            self.current_answer = x * b
        elif problem_type == "two_step_add":
            a = random.randint(2, 10)
            b = random.randint(-num_range, num_range)
            result = a * x + b
            self.current_problem = f"{a}x + {b} = {result}"
            self.current_answer = x
        elif problem_type == "two_step_mult":
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            result = (x + a) * b
            self.current_problem = f"{b}(x + {a}) = {result}"
            self.current_answer = x
        elif problem_type == "complex":
            a = random.randint(2, 5)
            b = random.randint(-20, 20)
            c = random.randint(2, 5)
            d = random.randint(-20, 20)
            result = (a * x + b) * c + d
            self.current_problem = f"{c}({a}x + {b}) + {d} = {result}"
            self.current_answer = x
       
        self.input_answer = ""
   
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_answer = self.input_answer[:-1]
            elif event.key == pygame.K_RETURN:
                self.check_answer()
            elif event.unicode.isdigit() or event.unicode == '-':
                self.input_answer += event.unicode
   
    def check_answer(self):
        try:
            user_answer = int(self.input_answer) if self.input_answer else 0
           
            if user_answer == self.current_answer:
                self.score += 1
                self.feedback = "Correct!"
            else:
                self.feedback = f"Wrong! Answer: x = {self.current_answer}"
           
            self.total_questions += 1
            self.feedback_timer = 120
            self.generate_new_problem()
        except ValueError:
            self.feedback = "Please enter a valid number"
            self.feedback_timer = 60
   
    def update(self):
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
   
    def draw(self, surface):
        surface.fill(WHITE)
       
        title = large_font.render(f"Algebra Game - Difficulty {self.difficulty}", True, BLACK)
        surface.blit(title, (50, 50))
       
        score_text = font.render(f"Score: {self.score}/{self.total_questions}", True, BLACK)
        surface.blit(score_text, (50, 100))
       
        # Problem
        problem_text = large_font.render("Solve for x:", True, BLACK)
        surface.blit(problem_text, (50, 200))
       
        equation_text = large_font.render(self.current_problem, True, BLUE)
        surface.blit(equation_text, (50, 250))
       
        # Input
        answer_label = font.render("x = ", True, BLACK)
        surface.blit(answer_label, (50, 350))
       
        pygame.draw.rect(surface, LIGHT_GRAY, (100, 345, 200, 35), 2)
        answer_text = font.render(self.input_answer, True, BLACK)
        surface.blit(answer_text, (105, 350))
       
        # Instructions
        instruction_text = small_font.render("Enter your answer and press ENTER", True, BLACK)
        surface.blit(instruction_text, (50, 400))
       
        # Feedback
        if self.feedback_timer > 0:
            feedback_color = GREEN if "Correct" in self.feedback else RED
            feedback_surface = font.render(self.feedback, True, feedback_color)
            surface.blit(feedback_surface, (50, 450))

class ProjectileGame:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
        self.score = 0
        self.total_questions = 0
        self.generate_new_wall()
        
        # Launch position
        self.launch_x = 50
        self.launch_y = SCREEN_HEIGHT - 80
       
        if difficulty == 1:
            # Slider mode - easier ranges
            self.a_slider = Slider(50, 480, 200, 20, -0.008, -0.001, -0.004, "a")
            self.h_slider = Slider(50, 520, 200, 20, 50, 200, 80, "h")
            self.k_slider = Slider(50, 560, 200, 20, 400, 650, 500, "k")
            self.input_mode = False
        else:
            # Input mode - need precise values
            self.input_mode = True
            self.input_a = "-0.004"
            self.input_h = "80"
            self.input_k = "500"
            self.input_active = "a"
       
        self.feedback = ""
        self.feedback_timer = 0
        self.trajectory_points = []
        self.last_test_passed = False
   
    def generate_new_wall(self):
        # Generate wall with random height and position
        self.wall_height = random.randint(80, 300)
        self.wall_x = random.randint(200, 600)
        self.wall_width = 25
        
    def get_parabola_values(self):
        if self.input_mode:
            try:
                a = float(self.input_a) if self.input_a else -0.004
                h = float(self.input_h) if self.input_h else 80
                k = float(self.input_k) if self.input_k else 500
            except ValueError:
                a, h, k = -0.004, 80, 500
        else:
            a = self.a_slider.val
            h = self.h_slider.val
            k = self.k_slider.val
        return a, h, k
   
    def calculate_trajectory(self):
        a, h, k = self.get_parabola_values()
        self.trajectory_points = []
        
        # Calculate trajectory starting from launch point
        start_x = self.launch_x
        for x in range(start_x, SCREEN_WIDTH, 3):
            y = a * (x - h) ** 2 + k
            if y <= SCREEN_HEIGHT - 50:  # Above ground level
                self.trajectory_points.append((x, y))
            else:
                break  # Stop when hitting ground
   
    def check_wall_clearance(self):
        a, h, k = self.get_parabola_values()
        
        # Check if trajectory clears the wall at multiple points across wall width
        wall_left = self.wall_x - self.wall_width // 2
        wall_right = self.wall_x + self.wall_width // 2
        wall_top = SCREEN_HEIGHT - self.wall_height
        
        # Check trajectory height at wall position
        for x in range(wall_left, wall_right + 1):
            y_at_wall = a * (x - h) ** 2 + k
            if y_at_wall >= wall_top:  # If trajectory is at or below wall top
                return False
        return True
   
    def handle_event(self, event):
        if not self.input_mode:
            self.a_slider.handle_event(event)
            self.h_slider.handle_event(event)
            self.k_slider.handle_event(event)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if self.input_active == "a":
                        self.input_active = "h"
                    elif self.input_active == "h":
                        self.input_active = "k"
                    else:
                        self.input_active = "a"
                elif event.key == pygame.K_BACKSPACE:
                    if self.input_active == "a":
                        self.input_a = self.input_a[:-1]
                    elif self.input_active == "h":
                        self.input_h = self.input_h[:-1]
                    else:
                        self.input_k = self.input_k[:-1]
                elif event.unicode.replace('.', '').replace('-', '').isdigit() or event.unicode in '.-':
                    if self.input_active == "a":
                        self.input_a += event.unicode
                    elif self.input_active == "h":
                        self.input_h += event.unicode
                    else:
                        self.input_k += event.unicode
       
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.test_trajectory()
   
    def test_trajectory(self):
        clears_wall = self.check_wall_clearance()
        
        if clears_wall:
            self.score += 1
            self.feedback = f"Success! Trajectory clears the wall! ({self.score} cleared)"
            self.last_test_passed = True
        else:
            self.feedback = f"Failed! Trajectory hits the wall. Try adjusting your parameters."
            self.last_test_passed = False
       
        self.total_questions += 1
        self.feedback_timer = 180
        
        # Only generate new wall after success (makes it more challenging)
        if clears_wall:
            self.generate_new_wall()
   
    def generate_new_wall(self):
        # Generate wall with random height and position, making it progressively harder
        base_height = 80 + (self.score * 10)  # Gets harder with more successes
        self.wall_height = random.randint(base_height, base_height + 100)
        self.wall_x = random.randint(180, 500)
        self.wall_width = 25
   
    def update(self):
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        self.calculate_trajectory()
   
    def draw(self, surface):
        surface.fill(WHITE)
       
        title = large_font.render(f"Projectile Game - Level {self.difficulty}", True, BLACK)
        surface.blit(title, (50, 20))
       
        score_text = font.render(f"Score: {self.score}/{self.total_questions}", True, BLACK)
        surface.blit(score_text, (400, 20))
        
        # Draw wall with better visibility
        wall_rect = pygame.Rect(self.wall_x - self.wall_width//2, SCREEN_HEIGHT - self.wall_height, 
                               self.wall_width, self.wall_height)
        pygame.draw.rect(surface, RED, wall_rect)
        pygame.draw.rect(surface, DARK_GRAY, wall_rect, 3)  # Border for visibility
        
        # Draw wall height indicator
        height_text = small_font.render(f"H:{self.wall_height}", True, BLACK)
        surface.blit(height_text, (self.wall_x - 20, SCREEN_HEIGHT - self.wall_height - 20))
       
        # Draw ground
        ground_y = SCREEN_HEIGHT - 50
        pygame.draw.line(surface, BLACK, (0, ground_y), (SCREEN_WIDTH, ground_y), 3)
        
        # Draw grass texture on ground
        for x in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(surface, GREEN, (x, ground_y), (x, ground_y + 10), 2)
       
        # Draw trajectory
        if len(self.trajectory_points) > 1:
            # Draw trajectory line
            pygame.draw.lines(surface, BLUE, False, self.trajectory_points, 4)
            
            # Draw trajectory end point
            if self.trajectory_points:
                end_point = self.trajectory_points[-1]
                pygame.draw.circle(surface, PURPLE, (int(end_point[0]), int(end_point[1])), 6)
       
        # Draw launcher with better graphics
        launcher_rect = pygame.Rect(self.launch_x - 15, self.launch_y - 10, 30, 20)
        pygame.draw.rect(surface, GREEN, launcher_rect)
        pygame.draw.circle(surface, DARK_GRAY, (self.launch_x, self.launch_y), 8)
       
        if self.input_mode:
            # Input fields for level 2+
            labels = ["a:", "h:", "k:"]
            inputs = [self.input_a, self.input_h, self.input_k]
            active_field = ["a", "h", "k"]
            
            input_title = font.render("Enter Parameters:", True, BLACK)
            surface.blit(input_title, (50, 60))
           
            for i, (label, input_val, field) in enumerate(zip(labels, inputs, active_field)):
                y_pos = 90 + i * 50
                label_surface = font.render(label, True, BLACK)
                surface.blit(label_surface, (50, y_pos))
               
                color = BLUE if self.input_active == field else LIGHT_GRAY
                input_rect = pygame.Rect(90, y_pos - 5, 150, 35)
                pygame.draw.rect(surface, WHITE, input_rect)
                pygame.draw.rect(surface, color, input_rect, 3)
                input_surface = font.render(input_val, True, BLACK)
                surface.blit(input_surface, (95, y_pos))
        else:
            # Sliders for level 1
            slider_title = font.render("Adjust Parameters:", True, BLACK)
            surface.blit(slider_title, (50, 450))
            self.a_slider.draw(surface)
            self.h_slider.draw(surface)
            self.k_slider.draw(surface)
       
        # Instructions box
        instruction_rect = pygame.Rect(680, 60, 300, 200)
        pygame.draw.rect(surface, LIGHT_GRAY, instruction_rect)
        pygame.draw.rect(surface, BLACK, instruction_rect, 2)
        
        instructions = [
            "OBJECTIVE:",
            "Launch projectile over the wall!",
            "",
            "Formula: y = a(x - h)² + k",
            "• a: controls curve shape",
            "• h: horizontal shift", 
            "• k: vertical shift",
            "",
            "Press SPACE to test launch!",
        ]
       
        if self.input_mode:
            instructions.append("TAB: switch parameters")
       
        for i, instruction in enumerate(instructions):
            if instruction == "OBJECTIVE:":
                text = font.render(instruction, True, RED)
            elif instruction.startswith("•"):
                text = small_font.render(instruction, True, DARK_GRAY)
            else:
                text = small_font.render(instruction, True, BLACK)
            surface.blit(text, (690, 70 + i * 18))
            
        # Current parameters display
        a, h, k = self.get_parabola_values()
        params_text = small_font.render(f"Current: a={a:.3f}, h={h:.1f}, k={k:.1f}", True, PURPLE)
        surface.blit(params_text, (690, 270))
       
        # Feedback
        if self.feedback_timer > 0:
            feedback_color = GREEN if "Success" in self.feedback else RED
            feedback_surface = font.render(self.feedback, True, feedback_color)
            feedback_rect = feedback_surface.get_rect(center=(SCREEN_WIDTH//2, 420))
            surface.blit(feedback_surface, feedback_rect)

class GameManager:
    def __init__(self):
        self.current_game = None
        self.game_state = "menu"
       
        # Menu buttons
        self.scatter_button = Button(100, 150, 200, 50, "Scatter Plot")
        self.algebra_button = Button(100, 220, 200, 50, "Algebra")
        self.projectile_button = Button(100, 290, 200, 50, "Projectile")
        self.back_button = Button(50, 50, 100, 40, "Back")
       
        # Difficulty buttons
        self.easy_button = Button(100, 200, 150, 50, "Easy")
        self.medium_button = Button(300, 200, 150, 50, "Medium")
        self.hard_button = Button(500, 200, 150, 50, "Hard")
       
        self.selected_game_type = None
   
    def handle_event(self, event):
        if self.game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.scatter_button.is_clicked(event.pos):
                    self.selected_game_type = "scatter"
                    self.game_state = "difficulty"
                elif self.algebra_button.is_clicked(event.pos):
                    self.selected_game_type = "algebra"
                    self.game_state = "difficulty"
                elif self.projectile_button.is_clicked(event.pos):
                    self.selected_game_type = "projectile"
                    self.game_state = "difficulty"
       
        elif self.game_state == "difficulty":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button.is_clicked(event.pos):
                    self.game_state = "menu"
                elif self.easy_button.is_clicked(event.pos):
                    self.start_game(1)
                elif self.medium_button.is_clicked(event.pos):
                    self.start_game(2)
                elif self.hard_button.is_clicked(event.pos):
                    self.start_game(3)
       
        elif self.game_state == "playing":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = "menu"
            else:
                self.current_game.handle_event(event)
   
    def start_game(self, difficulty):
        if self.selected_game_type == "scatter":
            self.current_game = ScatterPlotGame(difficulty)
        elif self.selected_game_type == "algebra":
            self.current_game = AlgebraGame(difficulty)
        elif self.selected_game_type == "projectile":
            self.current_game = ProjectileGame(difficulty)
       
        self.game_state = "playing"
   
    def update(self):
        if self.game_state == "playing" and self.current_game:
            self.current_game.update()
   
    def draw(self, surface):
        surface.fill(WHITE)
       
        if self.game_state == "menu":
            title = large_font.render("Math Challenge Game Suite", True, BLACK)
            surface.blit(title, (200, 50))
           
            subtitle = font.render("Choose a game:", True, BLACK)
            surface.blit(subtitle, (100, 100))
           
            self.scatter_button.draw(surface)
            self.algebra_button.draw(surface)
            self.projectile_button.draw(surface)
           
            # Game descriptions
            descriptions = [
                "Identify coordinates of points on a graph",
                "Solve algebraic equations for x",
                "Adjust parabolic trajectories to clear obstacles"
            ]
           
            for i, desc in enumerate(descriptions):
                text = small_font.render(desc, True, DARK_GRAY)
                surface.blit(text, (320, 165 + i * 70))
       
        elif self.game_state == "difficulty":
            title = large_font.render(f"Select Difficulty - {self.selected_game_type.title()}", True, BLACK)
            surface.blit(title, (150, 100))
           
            self.back_button.draw(surface)
            self.easy_button.draw(surface)
            self.medium_button.draw(surface)
            self.hard_button.draw(surface)
           
            # Difficulty descriptions
            if self.selected_game_type == "scatter":
                descriptions = ["±10 range", "±20 range", "±50 range"]
            elif self.selected_game_type == "algebra":
                descriptions = ["One-step, small numbers", "Two-step, medium numbers", "Complex, large numbers"]
            else:  # projectile
                descriptions = ["Use sliders", "Enter a, h, k values", "Advanced challenges"]
           
            for i, desc in enumerate(descriptions):
                text = small_font.render(desc, True, DARK_GRAY)
                surface.blit(text, (100 + i * 200, 270))
       
        elif self.game_state == "playing":
            self.current_game.draw(surface)
           
            # ESC instruction
            esc_text = small_font.render("Press ESC to return to menu", True, DARK_GRAY)
            surface.blit(esc_text, (SCREEN_WIDTH - 200, 10))

def main():
    clock = pygame.time.Clock()
    game_manager = GameManager()
   
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)
       
        game_manager.update()
        game_manager.draw(screen)
       
        pygame.display.flip()
        clock.tick(60)
   
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()