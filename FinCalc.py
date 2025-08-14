#!/usr/bin/env python3
import math
from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Optional

getcontext().prec = 28

def prompt_float(label: str, min_val: Optional[float] = None) -> float:
    while True:
        try:
            s = input(label).strip().replace('%', '')
            val = float(s)
            if min_val is not None and val < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print("Please enter a valid number.")

def prompt_int(label: str, min_val: Optional[int] = None) -> int:
    while True:
        try:
            s = input(label).strip()
            val = int(s)
            if min_val is not None and val < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")

def prompt_yes_no(label: str) -> bool:
    while True:
        s = input(label + " [y/n]: ").strip().lower()
        if s in ('y', 'yes'):
            return True
        if s in ('n', 'no'):
            return False
        print("Please enter y or n.")

def prompt_choice(label: str, choices: list[str]) -> int:
    for i, c in enumerate(choices, 1):
        print(f"{i}. {c}")
    while True:
        sel = prompt_int(label, 1)
        if 1 <= sel <= len(choices):
            return sel
        print("Invalid selection.")

# ------------------------------
# Annuities
# ------------------------------

def fv_annuity_monthly(pmt: float, annual_rate_pct: float, years: float, due: bool = False) -> float:
    r = annual_rate_pct / 100.0
    m = 12
    i = r / m
    n = int(round(years * m))
    if i == 0:
        fv = pmt * n
    else:
        fv = pmt * (((1 + i) ** n - 1) / i)
    if due:
        fv *= (1 + i)
    return fv

def pv_annuity_monthly(pmt: float, annual_rate_pct: float, years: float, due: bool = False) -> float:
    r = annual_rate_pct / 100.0
    m = 12
    i = r / m
    n = int(round(years * m))
    if i == 0:
        pv = pmt * n
    else:
        pv = pmt * (1 - (1 + i) ** (-n)) / i
    if due:
        pv *= (1 + i)
    return pv

def fv_annuity_monthly_with_continuous_growth(pmt: float, annual_rate_pct: float, years: float, due: bool = False) -> float:
    # Monthly contributions; continuous compounding on balances
    r = annual_rate_pct / 100.0
    m = 12
    n = int(round(years * m))
    fv = 0.0
    for k in range(1, n + 1):
        # Ordinary annuity: deposit at end of month k at time t_k = k/m years
        # Annuity due: deposit at beginning of month k at time t_k = (k-1)/m
        t_k = (k / m) if not due else ((k - 1) / m)
        growth_years = max(years - t_k, 0.0)
        fv += pmt * math.exp(r * growth_years)
    return fv

def fv_continuous_payment_stream(c_per_year: float, annual_rate_pct: float, years: float) -> float:
    # Continuous payment rate c (currency per year), continuous compounding rate r
    r = annual_rate_pct / 100.0
    if r == 0:
        return c_per_year * years
    return c_per_year * (math.exp(r * years) - 1.0) / r

# ------------------------------
# Mortgage
# ------------------------------

def mortgage_monthly_payment(principal: float, annual_rate_pct: float, years: float) -> float:
    r = annual_rate_pct / 100.0
    m = 12
    i = r / m
    n = int(round(years * m))
    if i == 0:
        return principal / n
    return principal * i / (1 - (1 + i) ** (-n))

# ------------------------------
# Retirement estimate
# ------------------------------

def future_value_balance(current_balance: float, annual_rate_pct: float, years: float, continuous: bool = False) -> float:
    r = annual_rate_pct / 100.0
    if continuous:
        return current_balance * math.exp(r * years)
    else:
        m = 12
        i = r / m
        n = int(round(years * m))
        return current_balance * (1 + i) ** n

def future_value_growing_annuity_monthly(pmt_monthly: float, annual_rate_pct: float, years: float, contrib_growth_annual_pct: float = 0.0, due: bool = False, continuous_growth_on_balances: bool = False) -> float:
    r = annual_rate_pct / 100.0
    g_annual = contrib_growth_annual_pct / 100.0
    m = 12
    n = int(round(years * m))

    # Per-month equivalents
    if continuous_growth_on_balances:
        # Compute by summation with continuous compounding and monthly payment growth
        # Payment in month k: P0 * (1 + g_m)^(k-1)
        g_m = (1 + g_annual) ** (1.0 / m) - 1.0
        fv = 0.0
        for k in range(1, n + 1):
            t_k = (k / m) if not due else ((k - 1) / m)
            growth_years = max(years - t_k, 0.0)
            p_k = pmt_monthly * ((1 + g_m) ** (k - 1))
            fv += p_k * math.exp(r * growth_years)
        return fv
    else:
        i = r / m
        g_m = (1 + g_annual) ** (1.0 / m) - 1.0
        if abs(i - g_m) < 1e-12:
            # Degenerate case r ≈ g
            fv = pmt_monthly * n * ((1 + i) ** (n - (0 if due else 1)))
        else:
            fv = pmt_monthly * (((1 + i) ** n - (1 + g_m) ** n) / (i - g_m))
        if due:
            fv *= (1 + i)
        return fv

# ------------------------------
# Doubling time
# ------------------------------

def doubling_time(annual_rate_pct: float, compounding: str = "annual", periods_per_year: int = 1) -> float:
    r = annual_rate_pct / 100.0
    comp = compounding.lower()
    if comp == "continuous":
        if r <= 0:
            return math.inf
        return math.log(2.0) / r
    else:
        m = periods_per_year
        i = r / m
        if i <= -1:
            return math.inf
        return math.log(2.0) / (m * math.log(1 + i))

# ------------------------------
# Logarithmic equations
# ------------------------------

def solve_log_equation():
    print("\nChoose a form to solve for x:")
    sel = prompt_choice("Select:", [
        "log_b(a*x + c) = d",
        "a*log_b(x) + c = d",
        "ln(a*x + c) = d",
        "ln(x) = d",
        "log10(a*x + c) = d",
    ])
    if sel == 1:
        a = prompt_float("Enter a: ")
        b = prompt_float("Enter base b (>0, !=1): ")
        c = prompt_float("Enter c: ")
        d = prompt_float("Enter d: ")
        if b <= 0 or abs(b - 1.0) < 1e-15:
            print("Invalid base.")
            return
        try:
            x = (b ** d - c) / a
            if a == 0:
                print("a cannot be zero.")
                return
            if a * x + c <= 0:
                print("No real solution (log argument <= 0).")
                return
            print(f"Solution: x = {x}")
        except Exception as e:
            print(f"Could not solve: {e}")
    elif sel == 2:
        a = prompt_float("Enter a (coefficient of log): ")
        b = prompt_float("Enter base b (>0, !=1): ")
        c = prompt_float("Enter c (added outside log): ")
        d = prompt_float("Enter d (right side): ")
        if b <= 0 or abs(b - 1.0) < 1e-15:
            print("Invalid base.")
            return
        if a == 0:
            print("a cannot be zero.")
            return
        logx = (d - c) / a
        x = b ** logx
        if x <= 0:
            print("No real solution (x must be > 0).")
            return
        print(f"Solution: x = {x}")
    elif sel == 3:
        a = prompt_float("Enter a: ")
        c = prompt_float("Enter c: ")
        d = prompt_float("Enter d: ")
        if a == 0:
            print("a cannot be zero.")
            return
        x = math.exp(d) - c
        x /= a
        if a * x + c <= 0:
            print("No real solution (ln argument <= 0).")
            return
        print(f"Solution: x = {x}")
    elif sel == 4:
        d = prompt_float("Enter d: ")
        x = math.exp(d)
        if x <= 0:
            print("No real solution (x must be > 0).")
            return
        print(f"Solution: x = {x}")
    elif sel == 5:
        a = prompt_float("Enter a: ")
        c = prompt_float("Enter c: ")
        d = prompt_float("Enter d: ")
        x = 10 ** d - c
        if a == 0:
            print("a cannot be zero.")
            return
        x /= a
        if a * x + c <= 0:
            print("No real solution (log argument <= 0).")
            return
        print(f"Solution: x = {x}")

# ------------------------------
# Scientific notation
# ------------------------------

def to_scientific_notation(number_str: str) -> tuple[str, int]:
    # Use Decimal for stable representation
    d = Decimal(number_str)
    if d.is_zero():
        return ("0", 0)
    sign = "-" if d < 0 else ""
    d = abs(d)
    exp = 0
    # Normalize to 1 <= mantissa < 10
    while d >= 10:
        d /= 10
        exp += 1
    while d < 1:
        d *= 10
        exp -= 1
    mantissa = d.quantize(Decimal("1.000000000000000000"), rounding=ROUND_HALF_UP).normalize()
    return (sign + format(mantissa, 'f'), exp)

def from_scientific_notation(mantissa_str: str, exponent: int) -> str:
    d = Decimal(mantissa_str) * (Decimal(10) ** int(exponent))
    return format(d.normalize(), 'f')

# ------------------------------
# Menus
# ------------------------------

def annuity_menu():
    print("\nAnnuity calculator")
    sel = prompt_choice("Select:", [
        "Future value (monthly compounding, monthly payments)",
        "Present value (monthly compounding, monthly payments)",
        "Future value (continuous compounding on monthly payments)",
        "Future value (continuous payment stream)",
    ])
    if sel in (1, 2, 3):
        pmt = prompt_float("Monthly payment amount: ", 0.0)
        rate = prompt_float("Annual nominal rate (%): ", 0.0)
        years = prompt_float("Years: ", 0.0)
        due = prompt_yes_no("Annuity due (payments at beginning)?")
        if sel == 1:
            fv = fv_annuity_monthly(pmt, rate, years, due=due)
            print(f"Future value = {fv:.2f}")
        elif sel == 2:
            pv = pv_annuity_monthly(pmt, rate, years, due=due)
            print(f"Present value = {pv:.2f}")
        else:
            fv = fv_annuity_monthly_with_continuous_growth(pmt, rate, years, due=due)
            print(f"Future value (continuous growth on balances) = {fv:.2f}")
    else:
        c = prompt_float("Continuous payment rate (per year): ", 0.0)
        rate = prompt_float("Annual continuous rate (%): ", 0.0)
        years = prompt_float("Years: ", 0.0)
        fv = fv_continuous_payment_stream(c, rate, years)
        print(f"Future value (continuous payments & compounding) = {fv:.2f}")

def mortgage_menu():
    print("\nMonthly mortgage payment")
    principal = prompt_float("Loan principal: ", 0.0)
    rate = prompt_float("Annual interest rate (%): ", 0.0)
    years = prompt_float("Term (years): ", 0.0)
    pmt = mortgage_monthly_payment(principal, rate, years)
    print(f"Monthly payment = {pmt:.2f}")

def retirement_menu():
    print("\nRetirement balance estimate")
    bal0 = prompt_float("Current balance: ", 0.0)
    pmt = prompt_float("Monthly contribution: ", 0.0)
    rate = prompt_float("Expected annual return (%): ")
    years = prompt_float("Years until retirement: ", 0.0)
    g = prompt_float("Annual contribution growth (%; 0 if none): ", 0.0)
    due = prompt_yes_no("Contribute at beginning of month (annuity due)?")
    continuous = prompt_yes_no("Apply continuous compounding to balances?")
    fv_bal = future_value_balance(bal0, rate, years, continuous=continuous)
    fv_contrib = future_value_growing_annuity_monthly(
        pmt, rate, years, contrib_growth_annual_pct=g, due=due, continuous_growth_on_balances=continuous
    )
    total = fv_bal + fv_contrib
    print(f"Future value of current balance = {fv_bal:.2f}")
    print(f"Future value of contributions = {fv_contrib:.2f}")
    print(f"Estimated retirement balance = {total:.2f}")

def doubling_menu():
    print("\nTime to double")
    rate = prompt_float("Annual rate (%): ")
    sel = prompt_choice("Compounding:", ["Annual", "Monthly", "Quarterly", "Continuous"])
    if sel == 1:
        t = doubling_time(rate, "periodic", 1)
    elif sel == 2:
        t = doubling_time(rate, "periodic", 12)
    elif sel == 3:
        t = doubling_time(rate, "periodic", 4)
    else:
        t = doubling_time(rate, "continuous")
    if math.isinf(t):
        print("No doubling in finite time with given rate.")
    else:
        print(f"Time to double ≈ {t:.4f} years")

def log_menu():
    print("\nLogarithmic equation solver")
    solve_log_equation()

def sci_notation_menu():
    print("\nScientific notation converter")
    sel = prompt_choice("Select:", ["To scientific notation", "From scientific notation"])
    if sel == 1:
        s = input("Enter a number: ").strip()
        try:
            mant, exp = to_scientific_notation(s)
            print(f"{s} = {mant} × 10^{exp}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        mant = input("Mantissa: ").strip()
        exp = prompt_int("Exponent (integer): ")
        try:
            val = from_scientific_notation(mant, exp)
            print(f"{mant} × 10^{exp} = {val}")
        except Exception as e:
            print(f"Error: {e}")

def main_menu():
    while True:
        print("\nFinancial Calculator")
        sel = prompt_choice("Choose an option:", [
            "Annuity (monthly or continuous growth)",
            "Monthly mortgage payment",
            "Retirement investment balance",
            "Time to double at given rate",
            "Solve logarithmic equations",
            "Convert scientific notation",
            "Exit",
        ])
        if sel == 1:
            annuity_menu()
        elif sel == 2:
            mortgage_menu()
        elif sel == 3:
            retirement_menu()
        elif sel == 4:
            doubling_menu()
        elif sel == 5:
            log_menu()
        elif sel == 6:
            sci_notation_menu()
        else:
            print("Goodbye.")
            break

if __name__ == "__main__":
    main_menu()