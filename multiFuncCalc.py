import math
from fractions import Fraction
import re

class MathCalculator:
    def __init__(self):
        self.menu_options = {
            '1': self.solve_proportions,
            '2': self.solve_for_x,
            '3': self.factor_square_roots,
            '4': self.convert_decimal,
            '5': self.convert_fraction,
            '6': self.convert_percent,
            '7': self.quit_program
        }
   
    def display_menu(self):
        print("\n" + "="*50)
        print("         MATHEMATICAL CALCULATOR")
        print("="*50)
        print("1. Solve Proportions (a/b = c/d)")
        print("2. Solve for x in Linear Equations")
        print("3. Factor Square Roots")
        print("4. Convert Decimals (to fractions & percents)")
        print("5. Convert Fractions (to decimals & percents)")
        print("6. Convert Percents (to decimals & fractions)")
        print("7. Quit")
        print("="*50)
   
    def solve_proportions(self):
        print("\n--- SOLVE PROPORTIONS ---")
        print("Format: a/b = c/d")
        print("Enter 'x' for the unknown value")
       
        try:
            a = input("Enter a: ").strip()
            b = input("Enter b: ").strip()
            c = input("Enter c: ").strip()
            d = input("Enter d: ").strip()
           
            # Convert inputs, handling 'x' as unknown
            values = [a, b, c, d]
            unknown_pos = -1
            nums = []
           
            for i, val in enumerate(values):
                if val.lower() == 'x':
                    if unknown_pos != -1:
                        print("Error: Only one unknown (x) allowed")
                        return
                    unknown_pos = i
                    nums.append(None)
                else:
                    try:
                        nums.append(float(val))
                    except ValueError:
                        print(f"Error: '{val}' is not a valid number")
                        return
           
            if unknown_pos == -1:
                print("Error: No unknown variable (x) found")
                return
           
            # Solve for x based on position
            a_val, b_val, c_val, d_val = nums
           
            if unknown_pos == 0:  # a is unknown
                if b_val == 0:
                    print("Error: Division by zero")
                    return
                x = (c_val * b_val) / d_val
                print(f"Solution: x/{b_val} = {c_val}/{d_val}")
                print(f"x = {x}")
               
            elif unknown_pos == 1:  # b is unknown
                if a_val == 0:
                    print("Error: Cannot solve when a = 0")
                    return
                x = (a_val * d_val) / c_val
                print(f"Solution: {a_val}/x = {c_val}/{d_val}")
                print(f"x = {x}")
               
            elif unknown_pos == 2:  # c is unknown
                if d_val == 0:
                    print("Error: Division by zero")
                    return
                x = (a_val * d_val) / b_val
                print(f"Solution: {a_val}/{b_val} = x/{d_val}")
                print(f"x = {x}")
               
            elif unknown_pos == 3:  # d is unknown
                if c_val == 0:
                    print("Error: Cannot solve when c = 0")
                    return
                x = (b_val * c_val) / a_val
                print(f"Solution: {a_val}/{b_val} = {c_val}/x")
                print(f"x = {x}")
           
            # Verify the solution
            verification = [a_val, b_val, c_val, d_val]
            verification[unknown_pos] = x
            left_side = verification[0] / verification[1]
            right_side = verification[2] / verification[3]
            print(f"Verification: {left_side:.6f} = {right_side:.6f}")
           
        except Exception as e:
            print(f"Error: {e}")
   
    def solve_for_x(self):
        print("\n--- SOLVE FOR X ---")
        print("Supported formats:")
        print("- ax + b = c")
        print("- ax = b")
        print("- x + b = c")
        print("- a(x + b) = c")
       
        equation = input("Enter equation: ").replace(" ", "")
       
        try:
            # Split by equals sign
            if '=' not in equation:
                print("Error: Equation must contain '=' sign")
                return
           
            left, right = equation.split('=')
           
            # Simple linear equation solver
            # Convert to standard form: ax + b = 0
            def parse_expression(expr):
                # Handle coefficient of x
                x_coeff = 0
                constant = 0
               
                # Replace common patterns
                expr = expr.replace('-', '+-')
                terms = [term for term in expr.split('+') if term]
               
                for term in terms:
                    if 'x' in term:
                        coeff_str = term.replace('x', '')
                        if coeff_str == '' or coeff_str == '+':
                            x_coeff += 1
                        elif coeff_str == '-':
                            x_coeff -= 1
                        else:
                            x_coeff += float(coeff_str)
                    else:
                        if term:
                            constant += float(term)
               
                return x_coeff, constant
           
            left_x_coeff, left_const = parse_expression(left)
            right_x_coeff, right_const = parse_expression(right)
           
            # Move everything to left side: (left_x_coeff - right_x_coeff)x + (left_const - right_const) = 0
            final_x_coeff = left_x_coeff - right_x_coeff
            final_const = left_const - right_const
           
            if final_x_coeff == 0:
                if final_const == 0:
                    print("Infinite solutions (identity)")
                else:
                    print("No solution (contradiction)")
            else:
                x = -final_const / final_x_coeff
                print(f"Solution: x = {x}")
               
                # Verify
                original_left = left_x_coeff * x + left_const
                original_right = right_x_coeff * x + right_const
                print(f"Verification: {original_left} = {original_right}")
       
        except Exception as e:
            print(f"Error parsing equation: {e}")
            print("Please use simple linear equations like '2x + 3 = 7'")
   
    def factor_square_roots(self):
        print("\n--- FACTOR SQUARE ROOTS ---")
        try:
            number = float(input("Enter number to factor under square root: "))
           
            if number < 0:
                print("Error: Cannot factor negative numbers under real square roots")
                return
           
            if number == 0:
                print("√0 = 0")
                return
           
            # Find perfect square factors
            original_number = int(number) if number == int(number) else number
           
            if number != int(number):
                print("Note: Working with decimal, converting to fraction first")
                frac = Fraction(number).limit_denominator()
                print(f"√{number} = √({frac}) = √{frac.numerator}/√{frac.denominator}")
                return
           
            number = int(number)
            perfect_square_factor = 1
            remaining_factor = number
           
            # Find largest perfect square factor
            i = 2
            while i * i <= remaining_factor:
                while remaining_factor % (i * i) == 0:
                    perfect_square_factor *= i
                    remaining_factor //= (i * i)
                i += 1
           
            if perfect_square_factor == 1:
                print(f"√{original_number} cannot be simplified further")
                print(f"√{original_number} ≈ {math.sqrt(original_number):.6f}")
            else:
                if remaining_factor == 1:
                    print(f"√{original_number} = {perfect_square_factor}")
                else:
                    print(f"√{original_number} = {perfect_square_factor}√{remaining_factor}")
               
                print(f"Decimal approximation: {math.sqrt(original_number):.6f}")
               
                # Show factorization
                factors = []
                temp = number
                d = 2
                while d * d <= temp:
                    while temp % d == 0:
                        factors.append(d)
                        temp //= d
                    d += 1
                if temp > 1:
                    factors.append(temp)
               
                print(f"Prime factorization of {original_number}: {' × '.join(map(str, factors))}")
       
        except ValueError:
            print("Error: Please enter a valid number")
   
    def convert_decimal(self):
        print("\n--- CONVERT DECIMAL ---")
        try:
            decimal = float(input("Enter decimal number: "))
           
            # Convert to fraction
            fraction = Fraction(decimal).limit_denominator()
            print(f"As fraction: {fraction}")
           
            # Convert to percent
            percent = decimal * 100
            print(f"As percent: {percent}%")
           
            # Additional info
            if fraction.denominator != 1:
                decimal_from_fraction = fraction.numerator / fraction.denominator
                print(f"Verification: {fraction.numerator}/{fraction.denominator} = {decimal_from_fraction}")
       
        except ValueError:
            print("Error: Please enter a valid decimal number")
   
    def convert_fraction(self):
        print("\n--- CONVERT FRACTION ---")
        try:
            fraction_str = input("Enter fraction (format: a/b): ").strip()
           
            if '/' not in fraction_str:
                print("Error: Please use format a/b")
                return
           
            numerator, denominator = fraction_str.split('/')
            numerator = float(numerator)
            denominator = float(denominator)
           
            if denominator == 0:
                print("Error: Denominator cannot be zero")
                return
           
            # Convert to decimal
            decimal = numerator / denominator
            print(f"As decimal: {decimal}")
           
            # Convert to percent
            percent = decimal * 100
            print(f"As percent: {percent}%")
           
            # Simplify fraction if possible
            frac = Fraction(int(numerator), int(denominator)) if numerator == int(numerator) and denominator == int(denominator) else Fraction(numerator, denominator).limit_denominator()
            if str(frac) != fraction_str:
                print(f"Simplified fraction: {frac}")
       
        except (ValueError, ZeroDivisionError):
            print("Error: Please enter a valid fraction")
   
    def convert_percent(self):
        print("\n--- CONVERT PERCENT ---")
        try:
            percent_input = input("Enter percentage (with or without % sign): ").strip()
           
            # Remove % if present
            if percent_input.endswith('%'):
                percent_input = percent_input[:-1]
           
            percent = float(percent_input)
           
            # Convert to decimal
            decimal = percent / 100
            print(f"As decimal: {decimal}")
           
            # Convert to fraction
            fraction = Fraction(decimal).limit_denominator()
            print(f"As fraction: {fraction}")
           
            # Show common fraction if applicable
            common_fractions = {
                25: "1/4", 50: "1/2", 75: "3/4",
                33.333333: "1/3", 66.666667: "2/3",
                20: "1/5", 40: "2/5", 60: "3/5", 80: "4/5",
                12.5: "1/8", 37.5: "3/8", 62.5: "5/8", 87.5: "7/8"
            }
           
            for common_percent, common_frac in common_fractions.items():
                if abs(percent - common_percent) < 0.01:
                    print(f"Common fraction: {common_frac}")
                    break
       
        except ValueError:
            print("Error: Please enter a valid percentage")
   
    def quit_program(self):
        print("\nThank you for using the Mathematical Calculator!")
        return True
   
    def run(self):
        print("Welcome to the Mathematical Calculator!")
       
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
           
            if choice in self.menu_options:
                if self.menu_options[choice]():  # quit_program returns True
                    break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
           
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    calculator = MathCalculator()
    calculator.run()