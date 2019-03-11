import base64
import os
import re
from xml.etree import ElementTree

import requests
from PIL import Image

BOOKID = 'your book id'
NO_OF_PAGES = '(int) pages in a book'
SESSION_ID = 'your_id'


def get_page_xml(page_no):
    book_id = BOOKID
    url = f"http://znanium.com/module.php?target=bookread2&book={book_id}&pageno={page_no}&currpageno={page_no}"
    cookie = {'PHPSESSID': SESSION_ID}
    r = requests.get(url, cookies=cookie)
    content = r.content
    root = ElementTree.fromstring(content)
    return root


def get_images64_from_xml(xml_file):
    images_list = []
    match = "data:image/png;base64,((.+\n?)+)"
    for child in xml_file[3]:
        m = re.search(match, child.text)
        image = base64.b64decode(m.group(1))
        images_list.append(image)
    return images_list


def save_temp_images(images):
    count = 0
    for image in get_images64_from_xml(images):
        filename = f'./temp_images/image{count}.png'
        with open(filename, 'wb') as f:
            f.write(image)
        count += 1


def combine_images(img_id):
    image_paths = []
    path = './temp_images/'
    for image_name in os.listdir(path):
        image_paths.append(path + image_name)
    images = list(map(Image.open, image_paths))
    widths, heights = zip(*(i.size for i in images))

    total_height = sum(heights)
    max_width = max(widths)

    new_im = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    new_im.save(f'./final_images/page{img_id}.png')


def delete_temp_images():
    folder = './temp_images'
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def main():
    no_of_pages = NO_OF_PAGES

    for page in range(no_of_pages):
        page_images = get_page_xml(page + 1)
        save_temp_images(page_images)
        combine_images(page + 1)
        delete_temp_images()



if __name__ == '__main__':
    main()
