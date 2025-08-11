import datetime

appointments = {}

def book_appointment(client_name, datetime_str):
    dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    if dt in appointments:
        return "This slot is already booked."
    appointments[dt] = client_name
    return f"Booked appointment for {client_name} on {dt}"

print(book_appointment("Alice", "2025-08-10 14:30"))
