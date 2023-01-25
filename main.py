import urllib.request
import zipfile
import json
import os
import asyncio
import shutil

output_path_name = 'json-database'

class Converter():
    def __init__(self) -> None:
        self.download_base()
        self.create_folders()
        asyncio.run(self.lister_convert())

    def download_base(self):
        # Параметры
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
        self.dir = os.getcwd() + '/'
        self.main_path = 'stalcraft-database-main/ru'
        
        if not os.path.exists(output_path_name): os.mkdir(output_path_name)
        
        for path_name in [e for e in os.listdir(self.dir + self.main_path) if not os.path.isfile(os.path.join(self.dir + self.main_path, e))]:
            os.chdir(self.dir + output_path_name)
            if not os.path.exists(path_name): os.mkdir(path_name)
            
            for path_name_two in [e for e in os.listdir(self.dir + self.main_path + '/' + path_name) if not os.path.isfile(os.path.join(self.dir + self.main_path + '/' + path_name, e))]:
                os.chdir(self.dir + output_path_name + '/' + path_name)
                if not os.path.exists(path_name_two): os.mkdir(path_name_two)
                
                for path_name_tre in [e for e in os.listdir(self.dir + self.main_path + '/' + path_name + '/' + path_name_two) if not os.path.isfile(os.path.join(self.dir + self.main_path + '/' + path_name + '/' + path_name_two, e))]:
                    os.chdir(self.dir + output_path_name + '/' + path_name + '/' + path_name_two)
                    if not os.path.exists(path_name_tre): os.mkdir(path_name_tre)

        os.chdir(self.dir)
        print('Дерриктории созданны.')

    async def lister_convert(self):
        with open(self.main_path + '/listing.json') as file:
            file = json.load(file)

        new_rows = []
        for row in range(0, len(file)):
            await self.file_convert(file[row]['data'])
            await self.copy_image(file[row]['icon'])
            new_row = {
                "name": file[row]['name']['lines']['en'],
                "key": file[row]['name']['key'],
                "data": file[row]['data'],
                "icon": file[row]['icon']
            }
            new_rows.append(new_row)
        
        with open(output_path_name + '/listing.json', 'a') as out:
            json.dump(new_rows, out, indent=2, ensure_ascii=False)

    async def file_convert(self, path):
        with open(self.dir + self.main_path + path) as file:
            file = json.load(file)
        
        infoBlocks = file['infoBlocks']

        name = file['name']['lines']['ru']
        key = file['name']['key']
        category = file['category']
        stats = {}
        other = []

        for i in range(0, len(infoBlocks)):
            type = infoBlocks[i]['type']

            if type == 'list':
                for x in range(0, len(infoBlocks[i]['elements'])):
                    element = infoBlocks[i]['elements'][x]
                    type_two = element['type']
                    
                    if type_two == 'key-value':
                        if element['key']['lines']['ru'] == "Класс":
                            item_class = element['value']['lines']['ru']

                        elif element['key']['lines']['ru'] == 'Ранг':
                            stats["rank"] =  element['value']['lines']['ru']

                        else:
                            tname = element['key']['lines']['ru']
                            value_type = element['value']['type']

                            if value_type == 'text':
                                value = element['value']['text']
                            else:
                                value = element['value']['lines']['ru']

                            other.append({"name": tname, "value": value}) 

                    elif type_two == 'numeric':
                        if element['name']['lines']['ru'] == 'Вес':
                            stats["weight"] =  element['value']

                        else:
                            tname = element['name']['lines']['ru']
                            value = element['value']
                            other.append({"name": tname, "value": value})
                        
                    elif type_two == 'text':
                        other.append({"text": element['text']['lines']['ru']})
                        
            if type == 'text':
                self.discc = infoBlocks[i]['text']['lines']['ru']
        
        stats['other'] = other
        try:
            new_rows = {
                "item_name": name,
                "key": key,
                "category": category,
                "class": item_class,
                "stats": stats,
                "discription": self.discc,
                }
        except:
            new_rows = {
                "item_name": name,
                "key": key,
                "category": category,
                "class": item_class,
                "stats": stats,
                "discription": "Отсутвует",
                }

        with open(self.dir + output_path_name + path, 'a') as out:
            json.dump(new_rows, out, indent=2, ensure_ascii=False)
            print('Файл', path, 'конвертирован.')

    async def copy_image(self, path):
        shutil.copyfile(self.dir + self.main_path + path, output_path_name + path)
            


if __name__ == "__main__":
    Converter()
