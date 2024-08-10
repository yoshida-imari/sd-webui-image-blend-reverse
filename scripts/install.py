import launch

if not launch.is_installed("Cython"):
    launch.run_pip("install Cython", "Cython")

if not launch.is_installed("pytoshop"):
    launch.run_pip("install pytoshop-fix-packbits", "pytoshop")


