import sys
import requests

API = "http://127.0.0.1:8000"

def print_response(r):
    print("Status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

# --- операции ---
def create(role, room_id, user_name, start, end):
    headers = {"X-User-Role": role}
    params = {
        "room_id": int(room_id),
        "user_name": user_name,
        "start_date": start,
        "end_date": end
    }
    r = requests.post(f"{API}/bookings", params=params, headers=headers)
    print_response(r)

def list_bookings(role):
    headers = {"X-User-Role": role}
    r = requests.get(f"{API}/bookings", headers=headers)
    print_response(r)

def update_booking(role, booking_id, start, end):
    headers = {"X-User-Role": role}
    params = {"start_date": start, "end_date": end}
    r = requests.put(f"{API}/bookings/{booking_id}", params=params, headers=headers)
    print_response(r)

def delete_booking(role, booking_id):
    headers = {"X-User-Role": role}
    r = requests.delete(f"{API}/bookings/{booking_id}", headers=headers)
    print_response(r)

def usage():
    print(__doc__)

# --- основной запуск ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "create" and len(sys.argv) == 7:
            _, _, role, room_id, user_name, start, end = sys.argv
            create(role, room_id, user_name, start, end)

        elif cmd == "list_bookings" and len(sys.argv) == 3:
            _, _, role = sys.argv
            list_bookings(role)

        elif cmd == "update" and len(sys.argv) == 6:
            _, _, role, booking_id, start, end = sys.argv
            update_booking(role, booking_id, start, end)

        elif cmd == "delete" and len(sys.argv) == 4:
            _, _, role, booking_id = sys.argv
            delete_booking(role, booking_id)

        else:
            usage()
    except Exception as e:
        print("Ошибка:", e)
