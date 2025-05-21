import subprocess

def main():
    print("Choose which app to launch:")
    print("1. python.py")
    print("2 uno.py")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        subprocess.run(["python3", "python.py"])
    elif choice == "2": 
        subprocess.run(["python3", "app.py"])
    else:
        print("Invalid choice.")
1
if __name__ == "__main__":
    main()