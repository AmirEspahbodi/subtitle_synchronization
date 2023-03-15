from fastapi import FastAPI, File
from subtitle_synchronization import main


app = FastAPI()

    
@app.post("/files/")
async def create_file(
        primary_subtitle: bytes = File(), secondary_subtitle:bytes = File(), 
        primary_language:str|None=None, secondary_language:str|None=None,
        is_primary_closed_caption:bool|None=None, is_secondary_closed_caption:bool|None=None,
        phonetic_type=None, movie_id:int|None=None, movie_name: str|None=None, user_language: str|None=None
    ):
    xlsx_file, synchronized_substring = main(primary_subtitle.decode(), secondary_subtitle.decode(), called_localy=False)
    return {
        'primary_subtitle': primary_subtitle,
        'secondary_subtitle':''.join(synchronized_substring), 
        'primary_language':primary_language,
        'secondary_language':secondary_language,
        'is_primary_closed_caption':is_primary_closed_caption,
        'is_secondary_closed_caption':is_secondary_closed_caption,
        'phonetic_type':phonetic_type,
        'movie_id':movie_id,
        'movie_name': movie_name,
        'user_language': user_language
    }


