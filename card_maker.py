'''Create cards for larp camp.'''
from PIL import Image, ImageDraw, ImageFont
import argparse
import csv
import textwrap
import os
from typing import Dict, Tuple

class Card:
    def __init__(self, frame_path: str, space: int) -> None:
        """set initial properties

        Args:
            frame_path (str): path to frame for the card
            space (int): free space in pixels after the last line
        """
        self.space = space
        self.img = Image.open(frame_path)
        self.image_width, self.image_height = self.img.size
        self.ratio = self.image_width/self.image_height
        self.draw = ImageDraw.Draw(self.img)
        self.set_fonts()
        self.y_position = 20
        self.line_height = 30
        self.blank_line_height = 40
        self.title = ''

    def set_fonts(self) -> None:
        """create various font objects
        """
        montserrat_path = os.path.join('fonts', 'montserrat.ttf')
        montserrat_italic_path = os.path.join('fonts', 'montserrat_italic.ttf')

        text_sizes = {'title': 40, 'large': 30, 'normal': 25, 'small': 20}
        self.fonts_bold = {}
        self.fonts_italic = {}

        for key, value in text_sizes.items():
            self.fonts_bold[key] = ImageFont.truetype(montserrat_path, value, encoding="unic")
            self.fonts_bold[key].get_variation_names()
            self.fonts_bold[key].set_variation_by_name('Bold')

            self.fonts_italic[key] = ImageFont.truetype(montserrat_italic_path, value, encoding="unic")
            self.fonts_italic[key].get_variation_names()
            self.fonts_italic[key].set_variation_by_name('Italic')


    def add_title(self, title: str) -> None:
        """write title into card object

        Args:
            title (str): text to be writen

        Raises:
            TitleAlreadySetExeption: raised if title is already writen
        """
        if self.title:
            raise TitleAlreadySetExeption()
        
        text_width, _ = self.draw.textsize(title, font=self.fonts_bold['title'])
        x_position = int(self.image_width-text_width)/2
        self.draw.text((x_position, self.y_position),
                        title, fill =(0, 0, 0),
                        font=self.fonts_bold['title'])
        
        self.y_position += self.blank_line_height
        
        self.title = title.replace(' ', '_')

    def choose_font(self, text: str, style: str, size: str) -> ImageFont:
        """_summary_

        Args:
            text (str): block of text
            style (str): style of text - bold or italic
            size (str): size of text - small, normal or large

        Raises:
            UnknownFontStyleExeption: raised if given non-existing name of style

        Returns:
            ImageFont: chosen font
        """
        if style == 'bold':
            font_dict = self.fonts_bold
        elif style == 'italic':
            font_dict = self.fonts_italic
        else:
            raise UnknownFontStyleExeption()
        
        if len(text) > int(150*self.ratio) or size == 'small':
            characters = int(50*self.ratio)
            font = font_dict['small']
        elif len(text) > int(100*self.ratio) or size == 'normal':
            characters = int(40*self.ratio)
            font = font_dict['normal']
        else:
            characters = int(30*self.ratio)
            font = font_dict['normal']

            
        return font, characters

    def add_text(self, text: str, style: str ='bold', size: str ='large') -> None:
        """write text block into the image

        Args:
            text (str): block of text to be writen
            style (str, optional): style of text - bold or italic. Defaults to 'bold'.
            size (str, optional): size of font - small, normal or large. Defaults to 'large'.

        Raises:
            CharacterLimitExceededError: raised when text is too long
        """
        font, characters = self.choose_font(text, style, size)

        lines = textwrap.wrap(text, characters)
        for line in lines:
            text_width, _ = self.draw.textsize(line, font=font)
            x_position = int((self.image_width-text_width)/2)
            self.y_position += self.line_height

            if self.y_position > self.image_height - self.space:
                raise CharacterLimitExceededError()
            
            self.draw.text((x_position, self.y_position),
                           line, fill =(0, 0, 0),
                           font=font)
            
        self.y_position += self.blank_line_height
            
    def save_into_file(self, folder_path: str ='cards') -> None:
        """creates .png file

        Args:
            folder_path (str, optional): path to folder for saving the image. Defaults to 'cards'.
        """
        img_name = f'card_{self.title}.png'
        img_path = os.path.join(folder_path, img_name)
        print(img_path)

        try:
            self.img.save(img_path)
            print(f'saving into: {img_path}')
        except OSError:
            print(f'folder {folder_path} does not exist')
    
class CharacterLimitExceededError(Exception):
    "Raised when the input does not fit into the image."
    pass

class TitleAlreadySetExeption(Exception):
    "Raised when trying to set title and title is already set."
    pass

class UnknownFontStyleExeption(Exception):
    "Raised when used other keyword then 'bold' or 'italic'."
    pass

class UnknownCardTypeException(Exception):
    "Raised when used other keyword then 'maze-cards' or 'magical-items'."
    pass

def parse_path() -> Tuple[str]:
    """read path to file argument

    Returns:
        str: path to the file with magical items
        str: magical-items or maze-cards
    """
    parser = argparse.ArgumentParser(
        description="path to csv file with magical items description",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    default_path = os.path.join('data', 'artefakty.csv')

    parser.add_argument(
        "--csv_path", type=str,
        default=default_path,
        help="path to magical items .csv file (default: data/artefakty.csv)"
    )

    parser.add_argument(
        "--card_type", type=str,
        default="magical-items",
        help="magical-items or maze-cards (default: magical-items)"
    )

    return vars(parser.parse_args())["csv_path"], vars(parser.parse_args())["card_type"]

def process_csv(csv_path: str, card_type: str) -> None:
    """read .csv file content to memory

    Args:
        csv_path (str): path to the file with magical items
        card_type (str): magical-items or maze-cards
    """
    print(f'trying to open file: {csv_path}')
    
    if card_type == 'magical-items':
        create_card = create_magical_item
    elif card_type == 'maze-cards':
        create_card = create_maze_card
    else:
        raise UnknownCardTypeException()

    try:
        csv_file = open(csv_path)
        print('success')
    except OSError:
        print(f'cannot open file: {csv_path}')
    
    csv_reader = csv.DictReader(csv_file)
    items = list(csv_reader)

    for item in items:
        create_card(item)

    csv_file.close()
        
def create_magical_item(item: Dict[str, str]) -> None:
    """format magical item card

    Args:
        row (str): description of one magical item
    """
    frame_path = os.path.join('frames', 'frame_magical_item.png')
    space = 100
    card = Card(frame_path, space)
    card.add_text('Magický předmět', 'italic', 'normal')
    card.add_title(item["Jméno"])
    if item["InSet"] == "1":
        card.add_text(f'Patří do setu: {item["Set"]}  [{item["SetPocet"]}]', 'italic', 'small')
    card.add_text(item["Mechanika"])
    card.add_text(item["Legenda"], 'italic')
    card.save_into_file()

def create_maze_card(item: Dict[str, str]) -> None:
    ...

def create_aspekt_card(aspekt: Dict[str, str|int]) -> None:
    ...

if __name__ == '__main__':
    csv_path, card_type = parse_path()
    process_csv(csv_path, card_type)