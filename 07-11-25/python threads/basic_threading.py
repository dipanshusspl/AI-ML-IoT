import threading
import time

# Define a function to run in each thread
def print_numbers():
    for i in range(1, 6):
        print(f"Numbers Thread: {i}")
        time.sleep(1)  # simulate some delay

def print_letters():
    for ch in ['A', 'B', 'C', 'D', 'E']:
        print(f"Letters Thread: {ch}")
        time.sleep(1)  # simulate some delay

# Create threads
t1 = threading.Thread(target=print_numbers)
t2 = threading.Thread(target=print_letters)

# Start threads
t1.start()
t2.start()

# Wait for both threads to complete
t1.join()
t2.join()

print("✅ Both threads finished execution!")
