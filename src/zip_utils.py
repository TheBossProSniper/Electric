from subprocess import PIPE, Popen
from colorama import Fore
import os
import winreg
import click
from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from extension import write


home = os.path.expanduser('~')


def delete_start_menu_shortcut(shortcut_name):
    start_menu = os.environ['APPDATA'] + \
        R'\Microsoft\Windows\Start Menu\Programs\Electric'
    path = os.path.join(start_menu, f'{shortcut_name}.lnk')
    os.remove(path)


def verify_checksum(path: str, checksum: str):
    from hashlib import sha256
    
    if sha256(open(path, 'rb').read()).hexdigest() == checksum:
        print('Hashes Match!')
    else:
        print('Hashes Don\'t Match!')


def unzip_file(download_dir: str, unzip_dir_name: str, file_type: str, metadata: Metadata):
    import zipfile
    import tarfile

    if not unzip_dir_name:
        unzip_dir_name = download_dir.replace('.zip', '')

    if not os.path.isdir(rf'{home}\electric'):
        os.mkdir(rf'{home}\electric')

    os.chdir(rf'{home}\electric')

    if metadata.silent and file_type == '.zip':
        with zipfile.ZipFile(download_dir, 'r') as zf:
            try:
                zf.extractall(download_dir.replace('.zip', ''))
            except:
                pass

    if not metadata.silent and file_type == '.zip':
        from tqdm import tqdm
        with zipfile.ZipFile(download_dir, 'r') as zf:
            for member in tqdm(zf.infolist(), desc='Extracting ', bar_format='{l_bar}{bar:13}{r_bar}{bar:-13b}', smoothing=0.0, unit='files'):
                try:
                    zf.extract(member, download_dir.replace('.zip', ''))
                except zipfile.error:
                    pass


    if file_type == '.tar':
        tar = tarfile.open(download_dir, 'r:')
        tar.extractall(unzip_dir_name)
        tar.close()

    if file_type == '.tar.gz':
        tar = tarfile.open(download_dir, 'r:gz')
    
    import py7zr
    if file_type == '.7z':
        with py7zr.SevenZipFile(download_dir) as z:
            z.extractall(unzip_dir_name)

    import patoolib

    if file_type == '.rar':
        patoolib.extract_archive(download_dir, outdir=unzip_dir_name)

    os.remove(download_dir)
    return rf'{home}\electric\\' + download_dir.replace(file_type, '')


def install_font(src_path: str):
    from ctypes import wintypes
    import ctypes
    import os
    import shutil

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

    FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'

    HWND_BROADCAST = 0xFFFF
    SMTO_ABORTIFHUNG = 0x0002
    WM_FONTCHANGE = 0x001D
    GFRI_DESCRIPTION = 1
    GFRI_ISTRUETYPE = 3

    if not hasattr(wintypes, 'LPDWORD'):
        wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

    user32.SendMessageTimeoutW.restype = wintypes.LPVOID
    user32.SendMessageTimeoutW.argtypes = (
        wintypes.HWND,   # hWnd
        wintypes.UINT,   # Msg
        wintypes.LPVOID,  # wParam
        wintypes.LPVOID,  # lParam
        wintypes.UINT,   # fuFlags
        wintypes.UINT,   # uTimeout
        wintypes.LPVOID  # lpdwResult
    )

    gdi32.AddFontResourceW.argtypes = (
        wintypes.LPCWSTR,)  # lpszFilename

    # http://www.undocprint.org/winspool/getfontresourceinfo
    gdi32.GetFontResourceInfoW.argtypes = (
        wintypes.LPCWSTR,  # lpszFilename
        wintypes.LPDWORD,  # cbBuffer
        wintypes.LPVOID,  # lpBuffer
        wintypes.DWORD)   # dwQueryType

    # copy the font to the Windows Fonts folder
    dst_path = os.path.join(
        os.environ['SystemRoot'], 'Fonts', os.path.basename(src_path)
    )
    shutil.copy(src_path, dst_path)

    # load the font in the current session
    if not gdi32.AddFontResourceW(dst_path):
        os.remove(dst_path)
        raise WindowsError('AddFontResource failed to load "%s"' % src_path)

    # notify running programs
    user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None
    )

    # store the fontname/filename in the registry
    filename = os.path.basename(dst_path)
    fontname = os.path.splitext(filename)[0]

    # try to get the font's real name
    cb = wintypes.DWORD()
    if gdi32.GetFontResourceInfoW(
            filename, ctypes.byref(cb), None, GFRI_DESCRIPTION
    ):
        buf = (ctypes.c_wchar * cb.value)()
        if gdi32.GetFontResourceInfoW(
                filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION
        ):
            fontname = buf.value

    is_truetype = wintypes.BOOL()
    cb.value = ctypes.sizeof(is_truetype)
    gdi32.GetFontResourceInfoW(
        filename, ctypes.byref(cb), ctypes.byref(is_truetype), GFRI_ISTRUETYPE
    )

    if is_truetype:
        fontname += ' (TrueType)'

    with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)


def download(packet, url: str, download_extension: str, file_path: str, metadata: Metadata, show_progress_bar=True, is_zip=False):
    '''
    Downloads A File from a URL And Saves It To A location
    url `(str)`:  Link or URL to download the file from.
    download_extension`(string)`: Extension for the file downloaded like `.exe` or `.txt`. 

    file_path`(string)`: Path to save the file to. 
    Examples(`'C:\\Users\\name\\Downloads'`, `'~/Desktop'`)
    show_progress_bar `[Optional]` `(bool)`: Whether or not to show the progress bar while downloading.
    >>> download('https://atom.io/download/windows_x64', '.exe', 'C:\MyDir\Installer')
    '''
    import requests
    import sys
    import cursor

    cursor.hide()  # Use This If You Want to Hide The Cursor While Downloading The File In The Terminal
    if not os.path.isdir(rf'{home}\electric'):
        os.mkdir(rf'{home}\electric')

    if not is_zip:
        if not os.path.isdir(rf'{home}\electric\extras'):
            os.mkdir(rf'{home}\electric\extras')

        if not os.path.isdir(rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}'):
            os.mkdir(
                rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}')

        # if not os.path.isdir(file_path.replace('\\\\', '\\')):
        #     os.mkdir(file_path.replace('\\\\', '\\'))

    try:
        file_path = file_path.replace('\\\\', '\\')
        with open(f'{file_path}{download_extension}', 'wb') as f:
            # Get Response From URL
            response = requests.get(url, stream=True)
            # Find Total Download Size
            total_length = response.headers.get('content-length')
            # Number Of Iterations To Write To The File
            chunk_size = 4096

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                full_length = int(total_length)

                # Write Data To File
                for data in response.iter_content(chunk_size=chunk_size):
                    dl += len(data)
                    f.write(data)

                    if show_progress_bar:
                        complete = int(25 * dl / full_length)
                        # Replace '=' with the character you want like '#' or '$'
                        fill_c = Fore.LIGHTGREEN_EX + '=' * complete
                        # Replace '-' with the character you want like ' ' (whitespace)
                        unfill_c = Fore.LIGHTBLACK_EX + '-' * (25 - complete)
                        sys.stdout.write(
                            f'\r{fill_c}{unfill_c} {Fore.RESET} {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB {Fore.RESET}')
                        sys.stdout.flush()
        if is_zip:
            write(f'\n{Fore.LIGHTGREEN_EX}Initializing Unzipper{Fore.RESET}',
                  'white', metadata)

    except KeyboardInterrupt:
        write(f'\nDownload Was Interrupted!',
              'red', metadata)
        sys.exit()


def create_start_menu_shortcut(unzip_dir, file_name, shortcut_name):
    import win32com.client

    start_menu = os.environ['APPDATA'] + \
        R'\Microsoft\Windows\Start Menu\Programs\Electric'
    if not os.path.isdir(start_menu):
        os.mkdir(start_menu)
    path = os.path.join(start_menu, f'{shortcut_name}.lnk')
    os.chdir(unzip_dir)
    icon = unzip_dir + '\\' + file_name
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = icon
    shortcut.IconLocation = icon
    shortcut.WindowStyle = 7  # 7 - Minimized, 3 - Maximized, 1 - Normal
    shortcut.save()


def generate_shim(shim_command: str, shim_name: str, shim_extension: str, overridefilename: str = ''):
    shim_command += f'\\{shim_name}'
    shim_command = shim_command.replace('\\\\', '\\')
    if not os.path.isdir(rf'{home}\electric\shims'):
        os.mkdir(rf'{home}\electric\shims')

    with open(rf'{home}\electric\shims\{shim_name if not overridefilename else overridefilename}.bat', 'w+') as f:
        f.write(f'@echo off\n"{shim_command}.{shim_extension}"')


def find_existing_installation(dir_name: str) -> bool:
    loc = f'{home}\electric'
    files = os.listdir(loc)
    if dir_name in files:
        return True
    return False


def display_notes(packet: PortablePacket, unzip_dir: str, metadata: Metadata, uninstall=False):
    write('\n----Notes----', 'white', metadata)
    if not uninstall:
        if isinstance(packet.install_notes, list):
            for line in packet.notes:
                write(line.replace('$dir', unzip_dir).replace('<extras>', rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}').replace(
                    '\\\\', '\\'), 'white', metadata)
        else:
            write(packet.install_notes.replace('$dir', unzip_dir).replace('<extras>', rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}').replace(
                '\\\\', '\\'), 'white', metadata)
    else:
        if isinstance(packet.uninstall_notes, list):
            for line in packet.notes:
                write(line.replace('$dir', unzip_dir).replace('<extras>', rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}').replace(
                    '\\\\', '\\'), 'white', metadata)
        else:
            write(packet.uninstall_notes.replace(
                '$dir', unzip_dir).replace('<extras>', rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}').replace('\\\\', '\\'), 'white', metadata)
    write('\n', 'white', metadata)


def make_archive(source, destination):
    from shutil import copytree, move
    
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    make_archive(name, format, archive_from, archive_to)
    move('%s.%s' % (name, format), destination)


def create_folder_backup(packet: PortablePacket, folder: str):
    if not os.path.isdir(rf'{home}\electric\Backup'):
        os.mkdir(rf'{home}\electric\Backup')
        os.mkdir(
            rf'{home}\electric\Backup\{packet.extract_dir}@{packet.latest_version}')
        make_archive(rf'{home}\electric\{packet.extract_dir}@{packet.latest_version}\{folder}',
                     rf'{home}\electric\{packet.extract_dir}@{packet.latest_version}')
        copytree(rf'{home}\electric\{packet.extract_dir}@{packet.latest_version}\{folder}',
                 rf'{home}\electric\Backup\{packet.extract_dir}@{packet.latest_version}\{folder}.zip')


def set_environment_variable(name: str, value: str):
    Popen(rf'setx {name} "{value}"', stdin=PIPE,
          stdout=PIPE, stderr=PIPE, shell=True)



def confirm(prompt: str):
    value = input(f'{prompt} (Y/n): ')
    if value in ['y', 'yes', 'Y', 'YES', 'Yes']:
        return True
    else:
        return False


def install_dependencies(packet: PortablePacket, metadata: Metadata):
    
    disp = str(packet.dependencies).replace(
            "[", "").replace("]", "").replace("\'", "")
    write(f'{packet.display_name} has the following dependencies: {disp}',
            'bright_yellow', metadata)
    continue_install = confirm(
        'Would you like to install the above dependencies ?')
    if continue_install:
        write(
        f'Installing Dependencies For => {packet.display_name}', 'cyan', metadata)
        for package_name in packet.dependencies:
            os.system(f'electric install {package_name}')


def uninstall_dependencies(packet: PortablePacket, metadata: Metadata):
    disp = str(packet.dependencies).replace(
            "[", "").replace("]", "").replace("\'", "")
    write(f'{packet.display_name} has the following dependencies: {disp}',
            'bright_yellow', metadata)
    continue_install = confirm(
        'Would you like to uninstall the above dependencies ?')
    if continue_install:
        write(
        f'Uninstalling Dependencies For => {packet.display_name}', 'cyan', metadata)
        for package_name in packet.dependencies:
            os.system(f'electric uninstall {package_name}')

def delete_environment_variable(name: str):
    Popen(rf'reg delete "HKCU\Environment" /F /V "{name}"', stdin=PIPE,
          stdout=PIPE, stderr=PIPE, shell=True)


def append_to_path(input_dir: str):
    proc = Popen(f'setx /M path "%PATH%;{input_dir}"', stdin=PIPE,
          stdout=PIPE, stderr=PIPE, shell=True)
    _, _ = proc.communicate()


def refresh_environment_variables():
    """
    Refreshes the environment variables on the current Powershell session.
    """
    proc = Popen('powershell -c "$env:Path = [System.Environment]::GetEnvironmentVariable(\'Path\',\'Machine\') + \';\' + [System.Environment]::GetEnvironmentVariable(\'Path\',\'User\')"'.split(
    ), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    proc.communicate()