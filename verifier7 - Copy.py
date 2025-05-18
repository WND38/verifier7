import subprocess
import json
import os
from datetime import datetime

# Base de dados dos arquivos de drivers. 
BASELINE_FILE = "driver_baseline.json"

def get_driver_info():
    """Query driver information using wmic."""
    try:
        # Python do windows 7 é antigo, utilize subprocess.run 
        result = subprocess.run(
            ['wmic', 'sysdriver', 'get', 'Name,PathName,ServiceType,State'],
            capture_output=True,
            text=True,
            check=True
        )
        # output
        lines = result.stdout.strip().splitlines()
        drivers = []
        # Pular o header
        for line in lines[1:]:
            if line.strip():
                parts = line.split(maxsplit=3)
                if len(parts) >= 4:
                    drivers.append({
                        "Name": parts[0],
                        "PathName": parts[1],
                        "ServiceType": parts[2],
                        "State": parts[3]
                    })
        return drivers
    except AttributeError:
        # subprocess.popen fazendo seu trabalho :D
        try:
            process = subprocess.Popen(
                ['wmic', 'sysdriver', 'get', 'Name,PathName,ServiceType,State'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True  # Python 2.7 // 3.x
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print("Error querying drivers: {}".format(stderr))
                return []
            lines = stdout.strip().splitlines()
            drivers = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split(maxsplit=3)
                    if len(parts) >= 4:
                        drivers.append({
                            "Name": parts[0],
                            "PathName": parts[1],
                            "ServiceType": parts[2],
                            "State": parts[3]
                        })
            return drivers
        except Exception as e:
            print("Error querying drivers: {}".format(e))
            return []
    except subprocess.CalledProcessError as e:
        print("Error querying drivers: {}".format(e))
        return []

def save_baseline(drivers):
    """Save driver information to a baseline file."""
    with open(BASELINE_FILE, 'w') as f:
        json.dump(drivers, f, indent=4)
    print("Baseline saved to {}".format(BASELINE_FILE))

def load_baseline():
    """Load driver information from the baseline file."""
    if not os.path.exists(BASELINE_FILE):
        print("No baseline file found. Please create a baseline first.")
        return []
    with open(BASELINE_FILE, 'r') as f:
        return json.load(f)

def compare_drivers(baseline, current):
    """Compare current drivers with baseline and report changes."""
    baseline_dict = {d["Name"]: d for d in baseline}
    current_dict = {d["Name"]: d for d in current}
    
    changes = []
    # Verificação de novos ou drivers velhos.
    for name, current_driver in current_dict.items():
        if name not in baseline_dict:
            changes.append("Novo driver encontrado: {} ({})".format(name, current_driver['PathName']))
        elif baseline_dict[name] != current_driver:
            changes.append("Driver modificado: {} (Path: {}, State: {})".format(
                name, current_driver['PathName'], current_driver['State']))
    
    # Checar para drivers mod.
    for name in baseline_dict:
        if name not in current_dict:
            changes.append("Driver removed: {}".format(name))
    
    return changes

def main():
    print("Ferramenta de verificação de drivers (bem simples)")
    print("1. Criar base de dados")
    print("2. Verificar mudanças")
    try:
        choice = input("Aperte 1 para salvar seus drivers, 2 para verificação dos mesmos (1 ou 2): ")
    except EOFError:
        print("Erro de input: aperte somente 1 ou 2.")
        return

    if choice == "1":
        drivers = get_driver_info()
        if drivers:
            save_baseline(drivers)
    elif choice == "2":
        baseline = load_baseline()
        if baseline:
            current = get_driver_info()
            if current:
                changes = compare_drivers(baseline, current)
                if changes:
                    print("\nChanges detected:")
                    for change in changes:
                        print(change)
                    # Arquivo salvo:
                    with open("driver_changes.log", "a") as f:
                        f.write("\nCheck at {}:\n".format(datetime.now()))
                        for change in changes:
                            f.write("{}\n".format(change))
                else:
                    print("Nenhuma mudança foi detectada.")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()