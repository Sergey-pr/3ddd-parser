import os
import requests

from pathlib import Path
from selenium import webdriver
from bs4 import BeautifulSoup

import tkinter as tk
from tkinter import *
from tkinter import filedialog


class DddParser:
    def __init__(self, driver_dir, old_dir, new_dir):
        self.driver = webdriver.Chrome(driver_dir)
        self.old_dir = old_dir
        self.new_dir = new_dir

    def process_directory(self):
        for old_path, sub_dirs, files in os.walk(self.old_dir):
            for filename in files:
                old_path_with_filename = os.path.join(old_path, filename)
                filename_without_ext, _ = os.path.splitext(filename)
                if '_' in filename:
                    code = filename_without_ext.split('_')[1]
                else:
                    code = filename_without_ext.split('.')[1]

                file_dict = self.process_file(code)

                if not file_dict:
                    continue

                path = f'{self.new_dir}/{file_dict.get("cat")}/{file_dict.get("sub_cat")}/{file_dict.get("name")}'
                Path(path).mkdir(parents=True, exist_ok=True)


                self.download_image(path, file_dict)
                if not os.path.isfile(f"{path}/{filename}"):
                    os.rename(old_path_with_filename, f"{path}/{filename}")

        self.driver.close()


    def process_file(self, code):

        self.driver.get(f"https://3ddd.ru/search?query={code}")


        search_content = self.driver.page_source
        search_soup = BeautifulSoup(search_content, features="lxml")

        item_div = search_soup.find('div', {'class': 'item'})
        if not item_div:
            return None
        children = item_div.findChildren("a", recursive=False)
        if not children:
            return None

        link_suffix = children[0].attrs.get('href')
        link = 'https://3ddd.ru' + link_suffix
        self.driver.get(link)

        page_content = self.driver.page_source
        page_soup = BeautifulSoup(page_content, features="lxml")

        categories = page_soup.find('ul', {'class': 'list-unstyled'})
        categories = categories.findChildren("li", recursive=False)
        cat = categories[0]
        cat = str(self.get_category(cat)).strip()

        sub_cat = categories[1]
        sub_cat = str(self.get_category(sub_cat)).strip()

        title_h1 = page_soup.find('h1', {'class': 'model-header'})
        name = str(title_h1.contents[0]).strip()

        image_div = page_soup.find('div', {'class': 'image-slider-item'})
        image = image_div.findChildren("img", recursive=False)
        image_url = image[0].attrs.get('src')

        illegal = ['*', '.', '"', '/', '\\', '[', ']', ':', ';', '|', ',']
        for symbol in illegal:
            name = name.replace(symbol, ' ')

        name = name.strip()

        file_dict = {
            'cat': cat,
            'sub_cat': sub_cat,
            'name': name,
            'image_url': image_url
        }

        return file_dict

    @staticmethod
    def download_image(path, file_dict):
        asset_url = file_dict.get('image_url')
        response = requests.get(asset_url, stream=True, allow_redirects=False)
        response.raw.decode_content = True
        new_file_content = response.content

        filename = asset_url.split('/')[-1]
        _, ext = os.path.splitext(filename)

        with open(f'{path}/{file_dict.get("name")}{ext}',"wb") as new_file:
            new_file.write(new_file_content)

    @staticmethod
    def get_category(element):
        element = element.findChildren("a", recursive=False)
        element = element[0].contents[0]
        return element



root = tk.Tk()
root.withdraw()

window = Tk()
window.title("Распределитель 4000")
window.geometry('540x120')

choose_folder_1_label = Label(window, text="Выберите изначальную папку:")
choose_folder_1_label.grid(column=0, row=0)

choose_folder_1_textbox = Entry(window, width=30)
choose_folder_1_textbox.grid(column=1, row=0)

def choose_folder_1_button_func():
    folder = filedialog.askdirectory()
    choose_folder_1_textbox.delete(0, END)
    choose_folder_1_textbox.insert(0, folder)

choose_folder_1_button = Button(window, text="Обзор", command=choose_folder_1_button_func)
choose_folder_1_button.grid(column=2, row=0)


choose_folder_2_label = Label(window, text="Выберите конченую папку:")
choose_folder_2_label.grid(column=0, row=1)

choose_folder_2_textbox = Entry(window, width=30)
choose_folder_2_textbox.grid(column=1, row=1)

def choose_folder_2_button_func():
    folder = filedialog.askdirectory()
    choose_folder_2_textbox.delete(0, END)
    choose_folder_2_textbox.insert(0, folder)

choose_folder_2_button = Button(window, text="Обзор", command=choose_folder_2_button_func)
choose_folder_2_button.grid(column=2, row=1)


choose_file_label = Label(window, text="Выберите драйвер хрома:")
choose_file_label.grid(column=0, row=2)

choose_file_textbox = Entry(window, width=30)
choose_file_textbox.grid(column=1, row=2)

def choose_file_button_func():
    file = filedialog.askopenfilename()
    choose_file_textbox.delete(0, END)
    choose_file_textbox.insert(0, file)

choose_file_button = Button(window, text="Обзор", command=choose_file_button_func)
choose_file_button.grid(column=2, row=2)


def start_button_func():
    parser = DddParser(
        choose_file_textbox.get(),
        choose_folder_1_textbox.get(),
        choose_folder_2_textbox.get()
    )
    parser.process_directory()


start_button = Button(window, text="Поехали", command=start_button_func)
start_button.grid(column=1, row=3)


def on_closing():
    window.destroy()
    sys.exit(0)


window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()