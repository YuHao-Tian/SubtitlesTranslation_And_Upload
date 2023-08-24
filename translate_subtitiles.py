import os

import openai
import pysrt
import PySimpleGUI as sg
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError


api_key = "Your_OPENAI_KEY"
openai.api_key = api_key

language_list = []
language_upload_policy = {"English": 'en', "Spanish": 'es',
                          "Chinese": 'zh', "Vietnamese": 'vi-VN',
                          "Thai": 'th-TH', "Indonesian": 'id'}
Converted = {}
Video_ID = ""


def translator(original_text, expect_language):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Translate this into {expect_language}:\n\n{original_text}\n\n",
        temperature=0.3,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()


def convertion(filename):
    file = pysrt.SubRipFile()
    # translate_subs = []

    for language in language_list:
        newfilename = filename[:len(filename) - 4]
        translate_srt_path = f"{newfilename}-{language}.srt"
        file = pysrt.SubRipFile()
        for sub in subs:
            start_time = sub.start
            end_time = sub.end
            text = sub.text
            translate_text = translator(text, language)
            translate_sub = pysrt.SubRipItem(
                index=sub.index,
                start=start_time,
                end=end_time,
                text=translate_text
            )
            file.append(translate_sub)
            print(f"Start: {start_time}, End: {end_time}, Text: {translate_text}")
            file.save(translate_srt_path)


def join(a, *p):
    """Join two or more pathname components, inserting '/' as needed.
    If any component is an absolute path, all previous path components
    will be discarded."""
    path = a
    for b in p:
        if b.startswith('/'):
            path = b
        elif path == '' or path.endswith('/'):
            path += b
        else:
            path += '/' + b
    return path


file_list_column = [
    [
        sg.Text("SRT file Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

Visible = False

text_viewer_column = [
    [sg.Text("Choose the srt file you want to convert from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Checkbox("English", key='s1', enable_events=True, visible=Visible), sg.Checkbox("Spanish", key='s2',
                                                                                        enable_events=True, visible=Visible),
     sg.Checkbox("Vietnamese", key='s3', enable_events=True, visible=Visible),
     sg.Checkbox("Thai", key='s4', enable_events=True, visible=Visible), sg.Checkbox("Indonesian", key='s5', enable_events=True,
                                                                                     visible=Visible)],
    [sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20), key='-PBAR-', visible=Visible),
     sg.Button('Convert', key='-Button-', visible=Visible)],
    [sg.Text('', key='-OUT-', enable_events=True, font=('Arial Bold', 16), justification='center', expand_x=True)],
    [sg.Text('', key='-OUT-', enable_events=True, font=('Arial Bold', 16), justification='center', expand_x=True)],
    [sg.Text('', key='-Video_ID_Text-')],
    [sg.In(size=(25, 1), enable_events=True, key="-Video_ID-", visible=Visible)],
    [sg.Text('', key='-Uploading-')],
    [sg.Button('Upload All', key='-Upload-', visible=Visible)]
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(text_viewer_column),
    ]
]

window = sg.Window(".SRT Convert APP", layout)

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []
        fnames = []
        for f in file_list:
            if f.lower().endswith(".srt"):
                file_path = join(folder, f)
                # print(file_path)
                fnames.append(file_path)

        window["-FILE LIST-"].update(fnames)
    if event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            print(filename)
            window["-TOUT-"].update(filename)
            Visible = True
            window['-PBAR-'].update(visible=Visible)
            window['-Button-'].update(visible=Visible)
            window['s1'].update(visible=True)
            window['s2'].update(visible=True)
            window['s3'].update(visible=True)
            window['s4'].update(visible=True)
            window['s5'].update(visible=True)
            event, values = window.read()
            print(event, values)
        except:
            pass

    if event == 's1':
        if values['s1'] == True:
            print("English")
            language_list.append("English")
        elif values['s1'] == False:
            print("No English")
            language_list.remove("English")

    if event == 's2':
        if values['s2'] == True:
            print("Spanish")
            language_list.append("Spanish")
        elif values['s2'] == False:
            print("No Spanish")
            language_list.remove("Spanish")

    if event == 's3':
        if values['s3'] == True:
            print("Vietnamese")
            language_list.append("Vietnamese")
        elif values['s3'] == False:
            print("No Vietnamese")
            language_list.remove("Vietnamese")

    if event == 's4':
        if values['s4'] == True:
            print("Thai")
            language_list.append("Thai")
        elif values['s4'] == False:
            print("No Thai")
            language_list.remove("Thai")

    if event == 's5':
        if values['s5'] == True:
            print("Indonesian")
            language_list.append("Indonesian")
        elif values['s5'] == False:
            print("No Indonesian")
            language_list.remove("Indonesian")




    if event == '-Button-':
        print(f"I clicked Button and filename is: {filename}")
        window['-Button-'].update(disabled=True)
        # for i in range(100):
        #     window['-PBAR-'].update(current_count=i + 1)
        #     window['-OUT-'].update(str(i + 1))
        #     time.sleep(1)
        #     window['-Button-'].update(disabled=False)
        print(f"Language list: {language_list}")
        file = pysrt.SubRipFile()
        # translate_subs = []
        subs = pysrt.open(filename, encoding="utf-8")
        totoal_length = len(language_list) * len(subs)
        print(f"total_length:{totoal_length}")
        Converted[filename] = "Chinese"
        for language in language_list:
            Ith_language = language_list.index(language) + 1
            print(f"{Ith_language}th language...")
            newfilename = filename[:len(filename) - 4]
            translate_srt_path = f"{newfilename}-{language}.srt"
            file = pysrt.SubRipFile()
            for sub in subs:
                Ith_sub = Ith_language * (subs.index(sub) + 1)
                print(f"{Ith_sub}th in {Ith_language}th language...")
                current_percentage = ((subs.index(sub) + 1) + (Ith_language - 1) * len(subs)) / totoal_length
                print(f"current_percentage: {current_percentage}")
                start_time = sub.start
                end_time = sub.end
                text = sub.text
                translate_text = translator(text, language)
                translate_sub = pysrt.SubRipItem(
                    index=sub.index,
                    start=start_time,
                    end=end_time,
                    text=translate_text
                )
                # translate_sub = sub.copy()
                # translate_sub.text = translate_text
                # translate_subs.append(translate_sub)
                file.append(translate_sub)
                print(f"Start: {start_time}, End: {end_time}, Text: {translate_text}")
                file.save(translate_srt_path)
                Converted[translate_srt_path] = language
                window['-PBAR-'].update(current_count=current_percentage * 100)
                window['-OUT-'].update(str(int(current_percentage * 100)))
                window['-Button-'].update(disabled=False)
                window.refresh()

        window['-Video_ID_Text-'].update("Please enter your Video ID")
        window['-Video_ID-'].update(visible=True)
        window['-Upload-'].update(visible=True)

        if event == 'Cancel':
            window['-PBAR-'].update(max=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    if event == '-Video_ID-':
        Video_ID = values["-Video_ID-"]
        print(f"Video ID: {Video_ID}")

    if event == '-Upload-':
        print(Converted)
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
        )
        flow.run_local_server(
            port=8088, prompt="consent", authorization_prompt_message=""
        )
        credentials = flow.credentials

        # Create YouTube Data API client
        youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

        try:
            window['-Uploading-'].update("Uploading...")
            for item in Converted:
                # if (subtitle_files.get(key) == None):
                #     print("There's no such file under this folder: " + subtitle_files.get(key))
                #     continue

                insert_request = youtube.captions().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'video_id': Video_ID,
                            'language': language_upload_policy.get(Converted.get(item)),
                            # Specify the language of the subtitles
                            'name': '',  # Name of the subtitles
                            'isDraft': False
                        }
                    },
                    media_body=MediaFileUpload(item)
                )
                response = insert_request.execute()
                print(response)
                window.refresh()
            window.refresh()
            window['-Uploading-'].update("Upload subtitles successfully!")
            sg.popup("upload subtitles successfully!")

        except HttpError as e:
            print('An HTTP error occurred:')
            print(e.content)
            sg.popup('An HTTP error occurred', e.content)
        except Exception as e:
            print('An error occurred:')
            print(str(e))
            sg.popup('An error occurred', str(e))

window.close()
