import sys
from gui.gui import Program
from database.db import setup_database, clear_license_keys

def main():
    if "--no-key" in sys.argv:
        clear_license_keys()
    
    setup_database()
    program = Program()
    program.run()

if __name__ == "__main__":
    main()