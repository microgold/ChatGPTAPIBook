# topics = "Advent Calendar, Angel, Artificial Tree, Baby Jesus, Baking, Bells, Bethlehem, Blizzard, Candles, Candy Cane, Carolers, Celebration, Chimney, Chocolate, Church, Claus, Cookies, Cranberry Sauce, Decorations, December, Eggnog, Elf, Evergreen, Exchange, Family, Feast, Festivity, Fireplace, Fruitcake, Garland, Gingerbread House, Glitter, Gold, Greetings, Grinch, Ham, Holly, Hot Chocolate, Icicles, Jingle Bells, Joy, Lights, Manger, Market, Merry, Mistletoe, Mittens, Mulled Wine, Music, Nativity, Nutcracker, Ornament, Parade, Party, Peppermint, Pine Cone, Pine Tree, Plum Pudding, Poinsettia, Presents, Red, Reindeer, Ribbon, Rudolph, Santa, Sleigh, Sleigh Bells, Snow, Snow Globe, Snowflakes, Snowman, Star, Stocking, Tinsel, Toboggan, Toy Soldier, Tree, Turkey, Twinkling Lights, Ugly Sweater, Wassail, White Christmas, Winter, Wreath, Wrapping Paper, Yule, Yule Log, Tradition, Socks, Spirit, St. Nicholas, Wise Men, Shepherd, Innkeeper, Drummer Boy, Little Match Girl, Sugar Plum Fairy, Ghost of Christmas Past, Ghost of Christmas Present, Ghost of Christmas Yet to Come, Bob Cratchit, Tiny Tim, Jacob Marley, Mr. Fezziwig, The Nutcracker, Clara, Drosselmeyer, King of the Mice, Snow Queen, Jack Frost, Father Christmas, Befana, Snow Maiden, Ded Moroz, Yule Goat, Yule Lads, Krampus, St. Lucy, Holly King, Wassailer, Parson Brown, Good King Wenceslas, Belsnickel, La Befana, Pere Noel, The Little Drummer Boy, Christkind, Baboushka, Caga Tió"
# topics = topics.split(", ")
# print('Number of topics: ', len(topics))

# read the puzzle_words.txt file and find out which comma delimited list is greater than 11
# if the list is greater than 11, then print out the list of words that breaks the rule

# open the file
puzzle_words = open('c:\\temp\\final-christmas-book\\puzzle_words.txt', 'r')
# read the file
puzzle_words = puzzle_words.read()
# split the file into a list of lists
puzzle_word_segments = puzzle_words.split('|')
for segment in puzzle_word_segments:
    if len(segment.split(',')) > 11:
        print(segment)
