import re


def is_math_expression(text):
    """Detect if code text contains mathematical notation"""
    math_indicators = [
        "≈",
        "×",
        "÷",
        "≤",
        "≥",
        "∈",
        "∉",
        "∑",
        "∏",
        "∫",
        "√",
        "±",
        "≠",
        "∞",
        "∂",
        "α",
        "β",
        "γ",
        "δ",
        "ε",
        "θ",
        "λ",
        "μ",
        "π",
        "σ",
        "φ",
        "ω",
        "^",
    ]
    return any(indicator in text for indicator in math_indicators)


def convert_math_to_latex(text):
    """Convert mathematical notation to LaTeX math"""
    replacements = {
        "≈": r"\approx",
        "×": r"\times",
        "÷": r"\div",
        "≤": r"\leq",
        "≥": r"\geq",
        "≠": r"\neq",
        "∈": r"\in",
        "∉": r"\notin",
        "⊂": r"\subset",
        "⊃": r"\supset",
        "∪": r"\cup",
        "∩": r"\cap",
        "∑": r"\sum",
        "∏": r"\prod",
        "∫": r"\int",
        "√": r"\sqrt",
        "±": r"\pm",
        "∓": r"\mp",
        "∞": r"\infty",
        "∂": r"\partial",
        "∇": r"\nabla",
        # Greek letters
        "α": r"\alpha",
        "β": r"\beta",
        "γ": r"\gamma",
        "δ": r"\delta",
        "ε": r"\epsilon",
        "ζ": r"\zeta",
        "η": r"\eta",
        "θ": r"\theta",
        "λ": r"\lambda",
        "μ": r"\mu",
        "π": r"\pi",
        "ρ": r"\rho",
        "σ": r"\sigma",
        "τ": r"\tau",
        "φ": r"\phi",
        "χ": r"\chi",
        "ψ": r"\psi",
        "ω": r"\omega",
    }

    # Create character class pattern - more efficient for single chars
    pattern = "[" + re.escape("".join(replacements.keys())) + "]"

    # Single regex replacement
    result = re.sub(pattern, lambda m: replacements[m.group(0)], text)

    # Handle subscripts and superscripts # need a better math parser
    # First handle compound patterns like var^sub_script -> var^{sub_{script}}
    result = re.sub(r"([a-zA-Z]+)\^([a-zA-Z]+)_([a-zA-Z0-9]+)", r"\1^{\2_{\3}}", result)
    # Then handle simple subscripts: variable_name -> variable_{name}
    result = re.sub(r"([a-zA-Z]+)_([a-zA-Z0-9]+)", r"\1_{\2}", result)
    # Then handle simple superscripts: variable^power -> variable^{power}
    result = re.sub(r"([a-zA-Z]+)\^([a-zA-Z0-9]+)", r"\1^{\2}", result)

    return result
