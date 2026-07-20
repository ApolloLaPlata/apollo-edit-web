if __name__ == "__main__":
    from backend.maestro.lightning_fleet import LightningFleetManager
    
    fleet = LightningFleetManager()
    studio_name = "zygomorphic-green-9lz"
    print("PYTHON:", fleet.run_task(studio_name, "which python"))
    print("PYTHON3:", fleet.run_task(studio_name, "which python3"))
    print("PIP:", fleet.run_task(studio_name, "which pip"))
    print("PIP3:", fleet.run_task(studio_name, "which pip3"))
    print("CONDA:", fleet.run_task(studio_name, "which conda"))
    
