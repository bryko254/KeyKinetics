from django.utils.timezone import localtime, timedelta

def get_date_range(days=30):
    """Get start and end dates for filtering"""
    end_date = localtime()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def format_timedelta(td):
    """Format timedelta object to human readable string"""
    if td is None:
        return None
    
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "0m" 