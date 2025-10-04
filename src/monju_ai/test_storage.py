from monju_ai.storage import save_entry, load_entries

def test_basic():
    entry = {"msg": "Hello Monju!"}
    save_entry(entry)

    entries = load_entries()
    print("Loaded entries:", entries)

if __name__ == "__main__":
    test_basic()
