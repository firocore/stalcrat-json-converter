import urllib.request
import zipfile
import json
import os
import asyncio
import shutil

class Converter():
    def __init__(self) -> None:
        self.read_config()
        self.download_base()
        self.create_folders()
        asyncio.run(self.lister_convert())

    def read_config(self):
        with open('config.json', 'r') as config:
            config = json.load(config)

        self.output_path_name = config['output_path_name']
        
        self.lang_file_names = config['lang']['file_names']
        self.lang_items_names = config['lang']['items']

    def download_base(self):
        # Параметры архива
        des = 'items.zip'
        url = 'https://github.com/EXBO-Studio/stalcraft-database/archive/refs/heads/main.zip'
        
        # Загрузка архива
        if urllib.request.urlretrieve(url, des):
            print("Архив с данным скачан.\nНачанаю распаковку.")
            
            # Распаковка архива
            zipfile.ZipFile(des).extractall()
            print('Архив распакован.')
            os.remove(des)

    def create_folders(self):
        

        # Получение основной дериктории
        self.dir = os.getcwd() + '/'
        # Каталог базы
        self.main_path = 'stalcraft-database-main/ru'

        if os.path.exists(self.output_path_name):
            shutil.rmtree(self.output_path_name)
        
        # Создание выходного каталога
        if not os.path.exists(self.output_path_name): os.mkdir(self.output_path_name)
        
        # Создание аналагичных каталогов с исходной базой
        for path_name in [e for e in os.listdir(self.dir + self.main_path) if not os.path.isfile(os.path.join(self.dir + self.main_path, e))]:
            os.chdir(self.dir + self.output_path_name)
            if not os.path.exists(path_name): os.mkdir(path_name)
            
            for path_name_two in [e for e in os.listdir(self.dir + self.main_path + '/' + path_name) if not os.path.isfile(os.path.join(self.dir + self.main_path + '/' + path_name, e))]:
                os.chdir(self.dir + self.output_path_name + '/' + path_name)
                if not os.path.exists(path_name_two): os.mkdir(path_name_two)
                
                for path_name_tre in [e for e in os.listdir(self.dir + self.main_path + '/' + path_name + '/' + path_name_two) if not os.path.isfile(os.path.join(self.dir + self.main_path + '/' + path_name + '/' + path_name_two, e))]:
                    os.chdir(self.dir + self.output_path_name + '/' + path_name + '/' + path_name_two)
                    if not os.path.exists(path_name_tre): os.mkdir(path_name_tre)
        
        # Возвращение в домашний каталог
        os.chdir(self.dir)
        print('Дерриктории созданны.')

    async def lister_convert(self):
        # Чтение исходного листа
        with open(self.main_path + '/listing.json') as file:
            file = json.load(file)

        # Лист для записи приобразованных строк
        new_rows = []

        # Чтение строк
        for row in range(0, len(file)):
            
            name = file[row]['name']['lines'][self.lang_items_names]
            file_name = file[row]['name']['lines'][self.lang_file_names]
            file_name = await self.convert_name(file_name)
            key = file[row]['name']['key']
            data = file[row]['data']
            data = await self.convert_data_path(data, file_name)
            icon = file[row]['icon']
            icon = await self.convert_data_path(icon, file_name)
            icon = icon[:-5] + '.png'
            
            # Конвертация data
            await self.file_convert(file_name, file[row]['data'])
            # Копирование изображения
            asyncio.sleep(0.1)
            shutil.copyfile(self.dir + self.main_path + file[row]['icon'], self.dir + self.output_path_name + icon)
            
            
            # Новые строки
            new_row = {
                "name": name,
                "key": key,
                "data": data,
                "icon": icon
            }

            # Добавление новых строк в лист
            new_rows.append(new_row)
        
        # Запись выходного листа
        with open(self.output_path_name + '/listing.json', 'a') as out:
            json.dump(new_rows, out, indent=2, ensure_ascii=False)

        if os.path.exists(self.main_path[:-3]):
            shutil.rmtree(self.main_path[:-3])

    async def convert_name(self, name: str) -> str:
        return name.replace(' ', '_').replace('»', '').replace('«', '').replace('/', '-') + '.json'

    async def convert_data_path(str, path: str, name: str) -> str:
        return path[:-8] + name.replace(' ', '_').replace('»', '').replace('«', '').replace('/', '-')

    async def file_convert(self, file_name: str, path: str):
        # Открытие исходного файла data
        with open(self.dir + self.main_path + path) as file:
            file = json.load(file)
        
        # Информационный блок
        infoBlocks = file['infoBlocks']

        # Строки
        name = file['name']['lines'][self.lang_items_names]
        key = file['name']['key']
        category = file['category']
        stats = {}
        other = []

        # Тут даже бог не поможет понять как я написал эту дичь надо бы по человечики переписать
        for i in range(0, len(infoBlocks)):
            type = infoBlocks[i]['type']

            if type == 'list':
                for x in range(0, len(infoBlocks[i]['elements'])):
                    element = infoBlocks[i]['elements'][x]
                    type_two = element['type']
                    
                    if type_two == 'key-value':
                        if element['key']['lines']['ru'] == "Класс":
                            item_class = element['value']['lines'][self.lang_items_names]

                        elif element['key']['lines']['ru'] == 'Ранг':
                            stats["rank"] =  element['value']['lines'][self.lang_items_names]

                        else:
                            tname = element['key']['lines'][self.lang_items_names]
                            value_type = element['value']['type']

                            if value_type == 'text':
                                value = element['value']['text']
                            else:
                                value = element['value']['lines'][self.lang_items_names]

                            other.append({"name": tname, "value": value}) 

                    elif type_two == 'numeric':
                        if element['name']['lines']['ru'] == 'Вес':
                            stats["weight"] =  element['value']

                        else:
                            tname = element['name']['lines'][self.lang_items_names]
                            value = element['value']
                            other.append({"name": tname, "value": value})
                        
                    elif type_two == 'text':
                        other.append({"text": element['text']['lines'][self.lang_items_names]})
                        
            if type == 'text':
                disc = infoBlocks[i]['text']['lines'][self.lang_items_names]
        
        stats['other'] = other
        try:
            new_rows = {
                "item_name": name,
                "key": key,
                "category": category,
                "class": item_class,
                "stats": stats,
                "discription": disc,
                }
        except Exception:
            new_rows = {
                "item_name": name,
                "key": key,
                "category": category,
                "class": item_class,
                "stats": stats,
                "discription": "Отсутвует",
                }
        # Запись выходного файла data
        with open(self.dir + self.output_path_name + path[:-8] + file_name, 'a') as out:
            json.dump(new_rows, out, indent=2, ensure_ascii=False)
            print('Файл', path, 'конвертирован в', path[:-8] + file_name)


if __name__ == "__main__":
    Converter()
