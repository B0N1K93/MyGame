import cx_Freeze

executables = [cx_Freeze.Executable('main.py', target_name = 'Бандерогусак!.exe', base = 'Win32GUI')]
excludes = ['unicodedata', 'logging', 'unittest', 'email', 'html', 'http', 'urllib', 'xml', 'bz2', 'numpy', 'scipy']
include_files = ['Goose', 'background.png', 'bonus.png', 'coin.png', 'enemy.png', 'lives.png', 'player.png', 'pause.png', 'icon.png', 'rage.png', 'Village of fools soundtrack.wav', 'coin.wav', 'explosion.wav', 'rage.wav']
includes = ['pygame', 'os', 'random', 'time', 'math']
options = {
    'build.exe': {
        'excludes': excludes,
        'build_exe': 'build_windows',
        'include_files': include_files,
        'includes': includes
    }
}

cx_Freeze.setup(
    name = 'Бандерогусак!',
    version = '1.0',
    executables = executables,
    options = options)
