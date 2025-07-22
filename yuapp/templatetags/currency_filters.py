from django import template

register = template.Library()

# @register.filter
# def currency(value):
#     return f"GHS {value:,.2f}"

@register.filter
def currency(value):
    try:
        value = float(value)  # Convert to float before formatting
        return f"GHS {value:,.2f}"  # Format with commas and 2 decimal places
    except (ValueError, TypeError):
        return "GHS 0.00"  # Return a default value if conversion fails
    

@register.filter
def image_url(crop):
    return crop.photo.url if crop.photo else ''

@register.filter
def subtract(value, arg):
    #Subtracts arg from value"""
    return value - arg if value and arg else value

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):  # Ensure it's a dict
        return dictionary.get(key, 0)  # Return 0 if key not found
    return 0  # If it's not a dictionary, return 0