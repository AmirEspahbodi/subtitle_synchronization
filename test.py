from subtitle_synchronization import  read_subtitles_from_text, main
import time

filee = open('en_70105212.vtt', 'r')
en_70105212_text = ''.join(filee.readlines())

filee = open('de_70105212.vtt', 'r')
de_70105212_text = ''.join(filee.readlines())

# for i in read_subtitles_from_text(text):
#     print(i)
# generator = read_subtitles_from_text('en_70105212.vtt', called_localy=True, is_secondary=True)
# first_lines = generator.__next__()
# next_line_of_first_lines = generator.__next__()
# first_lines.extend(next_line_of_first_lines)
# print(''.join(first_lines))
# for i in generator:
#     time.sleep(0.3)
#     print(str(i))

# for i in read_subtitles_from_text(de_70105212_text, called_localy=False):
#     time.sleep(0.3)
#     print(i)

xlsx_file, synchronized_substring = main(de_70105212_text, en_70105212_text, called_localy=False)
print(synchronized_substring)