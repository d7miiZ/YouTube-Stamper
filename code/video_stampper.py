from youtube_transcript_api import *
from iso639 import languages
import math

def get_transcript_list(youtube_id):
    try:
        return YouTubeTranscriptApi.list_transcripts(youtube_id)
    except Exception:
        raise Exception("Check The Link")

def get_langs(transcript_list,manual=True):
    langs = {}
    if manual:
        langs = transcript_list._manually_created_transcripts.copy()
    else:
        langs = transcript_list._generated_transcripts.copy()
        
    for lang_code in list(langs.keys()):
        try:
            langs[lang_code] = languages.get(alpha2=lang_code).name 
        except:
            pass
    return {value:key for key, value in langs.items()}

def get_transcript(transcript_list,lang='en'):
    return transcript_list.find_transcript([lang]).fetch()

def translate_transcript(transcript_list,to_lang):
    transcript = transcript_list.find_transcript(['en'])
    return transcript.translate(to_lang).fetch()
    

def get_time_stamps(transcript,word):
    time_stamps = []
    for sentence in transcript:
        if word in sentence["text"].lower().split():
            time = sentence["start"]
            duration = int(sentence["duration"])
            time_formated = ''
            if time < 60:
                secs = int(time)
                time_formated = f'00:00:{secs} - 00:00:{secs+duration}'
            elif 60 <= time < 3600:
                mins = int(time/60)

                secs = int((time % 60) * 60)
                secs_lenght = len(str(secs))
                secs = secs if secs_lenght < 2 else int(secs / pow(10,secs_lenght-2))
                time_formated = f'00:{mins}:{secs} - 00:{mins}:{secs+duration}'
            else:
                hours = int(time/3600)

                mins = int( (time % 3600) * 3600) / 60
                print(time)
                mins_lenght = len(str(mins))
                mins = mins if mins_lenght < 2 else int(mins / pow(10,mins_lenght-2))

                secs = int((time % 3600) * 3600)
                secs_lenght = len(str(secs))
                secs = secs if secs_lenght < 2 else int(secs / pow(10,secs_lenght-2))
                time_formated = f'{hours}:{mins}:{secs} - {hours}:{mins}:{secs+duration}'
            time_stamps.append(time_formated)

    return  None if len(time_stamps) == 0 else time_stamps

def get_translation_langs(transcript_list):
    translation_langs = {}
    for lang in transcript_list._translation_languages:
        try:
            translation_langs[languages.get(alpha2=lang["language_code"]).name] = lang["language_code"]
        except:
            pass
    return translation_langs

def get_youtubeId(link):
    '''
    Examples of Youtube links:
    1- https://youtu.be/zPF4coJ7pvU
    2- https://www.youtube.com/watch?v=zPF4coJ7pvU
    3- https://youtu.be/zPF4coJ7pvU?t=40
    4- https://www.youtube.com/embed/zPF4coJ7pvU
    5- https://www.youtube-nocookie.com/embed/zPF4coJ7pvU
    6- https://www.youtube-nocookie.com/embed/zPF4coJ7pvU?start=40
    7- https://www.youtube.com/embed/zPF4coJ7pvU?controls=0&amp;start=40
    '''
    id_part = link.split("/")[-1]
    id = id_part

    if 'watch' in id_part:
        id = id_part.split("v=")[-1]
    elif '?' in id_part:
        id = id_part.split('?')[0]
    return id

def get_time_stamps_dict(transcript, words):
    time_stamps_dict = {}
    for word in words:
        time_stamp = get_time_stamps(transcript,word)
        if time_stamp == None:
            time_stamps_dict[word] = "Not Found"
        else:
            time_stamps_dict[word] = time_stamp
    return time_stamps_dict

if __name__ == '__main__':
    link = input("Enter YouTube Link That You Want To Search: ")
    id = get_youtubeId(link)
    transcript_list = get_transcript_list(id)
    
    manul_dict = get_langs(transcript_list)
    auto_dict = get_langs(transcript_list, manual=False)
    translation_dict = get_translation_langs(transcript_list)
    manul_names = list(manul_dict.keys())
    auto_names = list(auto_dict.keys())
    translation_names = list(translation_dict.keys())
    auto_names = list(filter(lambda elm: elm not in manul_names, auto_names))
    transcript = None

    print("Recommended: " + str(manul_names))
    print("Not Recommended: " + str(auto_names))
    choosen_lang = input("Choose Language To Search In (Type translate if you want another language, Not Recommended): ")
    if choosen_lang.lower() == "translate":
        try:
            choosen_lang = input("Choose Language To Translate To: ")
            transcript = translate_transcript(transcript_list, translation_dict[choosen_lang.capitalize()])
        except:
            transcript = print("Language Not Found Defaulting To English")
    else:
        found_in_manul = choosen_lang.capitalize() in manul_names
        found_in_auto = choosen_lang.capitalize() in auto_names
        lang = manul_dict[choosen_lang.capitalize()] if found_in_manul else auto_dict[choosen_lang.capitalize()]

        if found_in_manul or found_in_auto:
            transcript = get_transcript(transcript_list , lang=lang)
            
    flag = True
    while flag:
        word = input("Choose Words To Search For, Put One Space Between Each Word: ").lower().split()
        time_stamps = get_time_stamps_dict(transcript,word)
        print("You May Not Find The Word In These Intervals But It Colud Be Close To Them")
        for (word, time_stamp) in time_stamps.items():
            print(f"Intervals For {word}: ")
            print(time_stamp)
        ans = input("Do You Want To Search For Another Words?(y/n): ")
        flag = True if ans.lower() == 'y' else False

