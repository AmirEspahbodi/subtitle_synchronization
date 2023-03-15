from datetime import datetime
import openpyxl


class SynchronizationStatus:
    SameRange = 1
    LagBehind = 2
    AheadOf = 3
    NOTHING = 4


def read_subtitles_from_text(textData:str, called_localy=False, is_secondary=False):
    synchronized_substring:list[str]=[]
    counter = 0

    if not called_localy:
        subtitles = textData.splitlines()
        line = subtitles[counter]
    else:
        subtitles = open(textData)
        line = subtitles.readline()
    
    
    while line.strip()!='1':
        if is_secondary:
            synchronized_substring.append(line)
        if not called_localy:
            counter+=1
            line = subtitles[counter]
        else:
            line = subtitles.readline()
                 
    if not called_localy:
        subtitles = subtitles[counter+1:]
    
    if is_secondary:
        yield synchronized_substring
            
    lines: list[str] = [line.strip()]

    for line in subtitles:
        if line.strip().isdigit():
            yield lines
            lines=[line.strip()]
            continue
        if line.strip():
            lines.append(line.strip())
    yield lines
    if called_localy: subtitles.close()


def get_subtitle_synchronization_status(back_base_sub, base_sub, next_base_sub, rewritting_sub, strict_moed=True):
    # Skip lines like this <c.white><c.mono_sans>[clears throat]</c.mono_sans></c.white>
    
    if (rewritting_sub[2][len('<c.white><c.mono_sans>'):][:-len('</c.mono_sans></c.white>')].endswith(']')):
        return SynchronizationStatus.NOTHING
    
    base_sub_start_time = datetime.strptime(base_sub[1][0:12], '%H:%M:%S.%f')
    base_sub_end_time = datetime.strptime(base_sub[1][17:29], '%H:%M:%S.%f')
    next_base_sub_start_time = datetime.strptime(next_base_sub[1][0:12], '%H:%M:%S.%f')
    
    rewritting_sub_start_time = datetime.strptime(rewritting_sub[1][0:12], '%H:%M:%S.%f')
    rewritting_sub_end_time = datetime.strptime(rewritting_sub[1][17:29], '%H:%M:%S.%f')
        
    if back_base_sub:
        back_base_sub_end_time = datetime.strptime(back_base_sub[1][17:29], '%H:%M:%S.%f')
        if  (back_base_sub_end_time-rewritting_sub_start_time) > (rewritting_sub_end_time - base_sub_start_time) :
            return SynchronizationStatus.LagBehind
    else:
        if (base_sub_start_time - rewritting_sub_start_time) > (rewritting_sub_end_time - base_sub_start_time):
            return SynchronizationStatus.LagBehind
    
    if (base_sub_end_time-rewritting_sub_start_time) < (rewritting_sub_end_time-next_base_sub_start_time):
        return SynchronizationStatus.AheadOf
    
    return SynchronizationStatus.SameRange

def check_starttime_of_rewsub_with_current_list(last_rewritting_subs_for_curretn_base_sub, current_rewitting_sub):
    current_rewitting_sub_start_time = datetime.strptime(current_rewitting_sub[1][0:12], '%H:%M:%S.%f')
    last_rewritting_subs_for_curretn_base_sub_start_time = datetime.strptime(last_rewritting_subs_for_curretn_base_sub[-1][1][0:12], '%H:%M:%S.%f')
    return current_rewitting_sub_start_time==last_rewritting_subs_for_curretn_base_sub_start_time

def set_starttime_of_first_list_eq_with_current_base_sub_start_time(base_sub, rewritting_subs_for_current_base_sub):
    for sub in rewritting_subs_for_current_base_sub[0]:
        sub[1] = base_sub[1][0:12] + sub[1][12:]

def set_enstime_of_last_list_eq_with_current_base_sub_end_time(base_sub, rewritting_subs_for_current_base_sub):
    for sub in rewritting_subs_for_current_base_sub[-1]:
        sub[1] = sub[1][0:17]+base_sub[1][17:29]+sub[1][29:]

def write_rewritting_subs_for_current_base_sub_in_file(rewritting_subs_for_current_base_sub, base_sub, sheet, result_line_counter, synchronized_substring):
    
    result_line_counter[0] = result_line_counter[0] + 1    
    
    start_time = base_sub[1][3:8].lstrip('0').lstrip(':')
    sheet[f'A{result_line_counter[0]}'] = str(start_time)+'s'

    base_sub_text = '\n'.join([sub[len('<c.bg_transparent>'):][:-len('<c.bg_transparent>')-1] for sub in base_sub[2:]])
    sheet[f'C{result_line_counter[0]}'] = base_sub_text
    
    total_sub_text = ''
    for subs in rewritting_subs_for_current_base_sub:
        for sub in subs:
            synchronized_substring.append('\n'.join(sub)+'\n\n')
            total_sub_text += ' '.join([sub[len('<c.white><c.mono_sans>'):][:-len('</c.mono_sans></c.white>')-1] for sub in sub[2:]])+' '
    sheet[f'B{result_line_counter[0]}'] = total_sub_text


def write_current_sub_in_file(current_rewritting_sub, result_line_counter, sheet, synchronized_substring):
    result_line_counter[0] = result_line_counter[0] + 1    
    
    start_time = current_rewritting_sub[1][3:8].lstrip('0').lstrip(':')
    sheet[f'A{result_line_counter[0]}'] = str(start_time)+'s'
    total_sub_text = ' '.join([sub[len('<c.white><c.mono_sans>'):][:-len('</c.mono_sans></c.white>')] for sub in current_rewritting_sub[2:]])
    sheet[f'B{result_line_counter[0]}'] = total_sub_text
    synchronized_substring.append('\n'.join(current_rewritting_sub)+'\n\n')


def main(primary_file, secondary_file, called_localy=False):
    # if called_localy=True primary_file and secondary_file contain a file path
    # if not, primary_file and secondary_file contain a large string of subtitles
    import os
    import random, string
    rendom_string = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    while os.path.exists(rendom_string):
        rendom_string = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    
    base_subtitles = read_subtitles_from_text(primary_file, called_localy=called_localy)
    rewritting_subtitles = read_subtitles_from_text(secondary_file, called_localy=called_localy, is_secondary=True)
    result_line_counter = [1]
    rewritting_subtitles
    synchronized_substring = rewritting_subtitles.__next__()
    book = openpyxl.Workbook()
    sheet = book.active
    
    sheet[f'A{result_line_counter[0]}'] = "Time"
    sheet[f'B{result_line_counter[0]}'] = "Subtitle"
    sheet[f'C{result_line_counter[0]}'] = "Translation"
    
    current_rewritting_sub = None
    rewritting_subs_for_current_base_sub = None
    back_base_sub, base_sub, next_base_sub= None, None, base_subtitles.__next__()
    try:
        for base_sub in base_subtitles:
            base_sub, next_base_sub = next_base_sub, base_sub
            rewritting_subs_for_current_base_sub = []
            while True:
                if current_rewritting_sub is None:
                    current_rewritting_sub = rewritting_subtitles.__next__()
                status = get_subtitle_synchronization_status(back_base_sub, base_sub, next_base_sub, current_rewritting_sub)
                if status == SynchronizationStatus.LagBehind or status == SynchronizationStatus.NOTHING:
                    write_current_sub_in_file(current_rewritting_sub, result_line_counter, sheet, synchronized_substring)
                    current_rewritting_sub = None
                    continue
                elif status == SynchronizationStatus.AheadOf:
                    break
                else:
                    while True:
                        rewritting_subs_for_current_base_sub.append([current_rewritting_sub])
                        current_rewritting_sub = rewritting_subtitles.__next__()
                        while check_starttime_of_rewsub_with_current_list(rewritting_subs_for_current_base_sub[-1], current_rewritting_sub):
                            rewritting_subs_for_current_base_sub[-1].append(current_rewritting_sub)
                            current_rewritting_sub = rewritting_subtitles.__next__()
                        else:
                            if get_subtitle_synchronization_status(back_base_sub, base_sub, next_base_sub, current_rewritting_sub) == SynchronizationStatus.SameRange:
                                continue
                            else:
                                set_starttime_of_first_list_eq_with_current_base_sub_start_time(base_sub, rewritting_subs_for_current_base_sub)
                                set_enstime_of_last_list_eq_with_current_base_sub_end_time(base_sub, rewritting_subs_for_current_base_sub)
                                write_rewritting_subs_for_current_base_sub_in_file(rewritting_subs_for_current_base_sub, base_sub, sheet, result_line_counter, synchronized_substring)
                                break
                    break
            back_base_sub = base_sub
    except StopIteration:
        set_starttime_of_first_list_eq_with_current_base_sub_start_time(base_sub, rewritting_subs_for_current_base_sub)
        set_enstime_of_last_list_eq_with_current_base_sub_end_time(base_sub, rewritting_subs_for_current_base_sub)
        write_rewritting_subs_for_current_base_sub_in_file(rewritting_subs_for_current_base_sub, base_sub, sheet, result_line_counter, synchronized_substring)
    
    book.save(rendom_string+f"{rendom_string}.xlsx")
    
    return f"{rendom_string}.xlsx", synchronized_substring

if __name__=="__main__":
    main('de_70105212.vtt', 'en_70105212.vtt', called_localy=True)