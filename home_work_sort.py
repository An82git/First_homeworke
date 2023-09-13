import shutil
from pathlib import Path
import sys
import re


images = []
documents = []
audio = []
video = []
archives = [] 
unknown = []
directory = []
sort_directory_list = {}
known_expansion = []
not_known_expansion = []


CREATE_NEW_DIR = ['images', 'video', 'documents', 'audio', 'archives']
MAIN_DIR = Path(' '.join(sys.argv).replace(sys.argv[0], '').strip())
CYRILLIC_SYMBOLS = "абвгдежзийклмнопрстуфхцчшщьюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "yu", "ya", "je", "i", "ji", "g")
TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
   TRANS[ord(c)] = l
   TRANS[ord(c.upper())] = l.upper()


def sort_directory(path:Path) -> None:
    for file in path.iterdir():
        if file.is_dir():
            directory.append([file.as_posix(), file.name])
            sort_directory(file)
        else:
            if file.suffix.upper() in ['.JPEG', '.PNG', '.JPG', '.SVG']:
                known_expansion.append(file.suffix.upper())
                images.append([file.as_posix(), file.name])

            elif file.suffix.upper() in ['.AVI', '.MP4', '.MOV', '.MKV']:
                known_expansion.append(file.suffix.upper())
                video.append([file.as_posix(), file.name])

            elif file.suffix.upper() in ['.DOC', '.DOCX', '.TXT', '.PDF', '.XLSX', '.PPTX']:
                known_expansion.append(file.suffix.upper())
                documents.append([file.as_posix(), file.name])

            elif file.suffix.upper() in ['.MP3', '.OGG', '.WAV', '.AMR']:
                known_expansion.append(file.suffix.upper())
                audio.append([file.as_posix(), file.name])

            elif file.suffix.upper() in ['.ZIP', '.GZ', '.TAR']:
                known_expansion.append(file.suffix.upper())
                archives.append([file.as_posix(), file.name])

            else:
                not_known_expansion.append(file.suffix.upper())
                unknown.append([file.as_posix(), file.name])
        sort_directory_list.update({'directory':directory,'images':images,'video':video,'documents':documents,
                                    'audio':audio,'archives':archives,'unknown':unknown})


def normalize(string:str) -> str:
    return re.sub(r'[^A-Za-z0-9./]' , '_', 
                  string.removeprefix(str(MAIN_DIR.joinpath()).replace(chr(92), '/')).translate(TRANS)).removeprefix('/')


def type_images() -> None:
    for key, value in sort_directory_list.items():
        for item in value:
            if key == 'images':
                shutil.move(item[0], MAIN_DIR.joinpath(f'images/{normalize(Path(item[0]).name)}'))


def type_documents() -> None:
    for key, value in sort_directory_list.items():
        for item in value:
            if key == 'documents':
                shutil.move(item[0], MAIN_DIR.joinpath(f'documents/{normalize(Path(item[0]).name)}'))


def type_audio() -> None:
    for key, value in sort_directory_list.items():
        for item in value:
            if key == 'audio':
                shutil.move(item[0], MAIN_DIR.joinpath(f'audio/{normalize(Path(item[0]).name)}'))


def type_video() -> None:
    for key, value in sort_directory_list.items():
        for item in value:
            if key == 'video':
                shutil.move(item[0], MAIN_DIR.joinpath(f'video/{normalize(Path(item[0]).name)}'))


def type_archives() -> None:
    for key, value in sort_directory_list.items():
        for item in value:
            if key == 'archives':
                shutil.unpack_archive(item[0], MAIN_DIR.joinpath(f'archives/{normalize(Path(item[0]).name.removesuffix(Path(item[0]).suffix))}'))                
                Path(item[0]).unlink()


def remove_folder(path:Path) -> None:
    for file in path.glob('**/*'):
        try:
            file.rmdir()
        except OSError:
            remove_folder(file)


def create_folder(name_folder:list) -> None:
    file_and_dir = []
    for item in Path(MAIN_DIR).iterdir():
        file_and_dir.append(item.name)
    for dir in name_folder:
        if not dir in file_and_dir:
            Path.mkdir(MAIN_DIR.joinpath(dir))


def normalize_folder_and_file(path:Path) -> None:
    for file in path.glob('**/*'):
        shutil.move(file, MAIN_DIR.joinpath(normalize(file.as_posix().removeprefix(MAIN_DIR.as_posix()))))
        

def main() -> None:
    sort_directory(MAIN_DIR)
    for key, value in sort_directory_list.items():
        directory_list = []
        if not key == 'directory':
            for item in value:
                directory_list.append(item[1])
            print('{:-<10}\n{} - {}'.format('', key, directory_list))
    print('{:-<10}\nknown expansion - {}\n{:-<10}\nnot known expansion - {}\n{:-<10}'.format('', list(set(known_expansion)), 
                                                                           '', list(set(not_known_expansion)), ''))

    create_folder(CREATE_NEW_DIR)

    type_images()
    type_video()
    type_documents()
    type_audio()
    type_archives()

    normalize_folder_and_file(MAIN_DIR)

    remove_folder(MAIN_DIR)


main()
