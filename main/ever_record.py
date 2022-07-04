import google_auth_oauthlib
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import requests
import json

# imports to upload sound file to Google Drive
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# Class handles audio and other responsibilities like timer.
class AudioHandler(Screen):
    sound = ObjectProperty()
    time = NumericProperty(0)

    has_record = False

    # start recording sound.
    def start_recording(self):
        state = self.sound.state
        if state == 'ready':
            self.sound.start()

        if state == 'recording':
            self.sound.stop()
            self.has_record = True
            # stop timer and resets label.
            self.on_stop_timer()
            self.update_label_reset()

        # start the clock, update the labels for timer.
        self.update_labels()
        self.on_start()
        self.update_label()

    # play the recording.
    def play_recording(self):
        state = self.sound.state
        if state == 'playing':
            self.sound.stop()
        else:
            self.sound.play()

        self.update_labels()

    # update labels for recordings.
    def update_labels(self):
        record_button = self.ids['record_button']
        play_button = self.ids['play_button']
        state_label = self.ids['state_label']

        state = self.sound.state
        state_label.text = 'Sound is: ' + state

        play_button.disabled = not self.has_record

        if state == 'ready':
            record_button.text = 'Start Recording'

        if state == 'recording':
            record_button.text = 'Press to Stop Recording'
            play_button.disabled = True

        if state == 'playing':
            play_button.text = 'Stop'
            record_button.disabled = True
        else:
            play_button.text = 'Press to play'
            record_button.disabled = False

    # start clock, set interval to 1s.
    def on_start(self):
        Clock.schedule_interval(self.update_label, 1)

    # update timer label
    def update_label(self, *args):
        self.ids.clock.text = str(int(self.ids.clock.text) + 1)

    # stop timer
    def on_stop_timer(self):
        Clock.schedule_interval(self.update_label_reset, 0)

    # reset the timer
    def update_label_reset(self, *args):
        self.ids.clock.text = str(int(self.ids.clock.text) * 0)


# Classes connect to .kv file. GUI is build in KV file; classes required here to make a page (Screen).


class AppInfo(Screen):
    pass


class SettingsTab(Screen):
    pass


class About(Screen):
    pass


class Recordings(Screen):
    pass


# ==> NEW CODE <==
class ShareToDrive(Screen):
    service: object
    global SCOPES

    # specify the scope you're accessing
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def setup_drive_conn(self):

        # variable will store access token.
        # If no valid token is found, one will be created.
        self.creds = None

        # token.pickle stores user access & refresh tokens.
        # if authorization flow completes properly for the first time,
        # it is created
        if os.path.exists('token.pickle'):

            # Read token from a file
            # store it in variable self.credentials
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

            # if no valid credentials available, request user to log in
            if not self.creds or not self.creds.valid:

                # if token is expired, refresh it. otherwise request a new token
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('Other/credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=8080)

                # Save access token acquired in token.pickle
                # use file for future
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)

                self.service = build('drive', 'v3', credentials=self.creds)

                # see files in drive
                results = self.service.files().list(
                    pageSize=100, fields="files(id, name)").execute()
                items = results.get('files', [])

                print("List of files: \n")
                print(*items, sep="\n", end="\n\n")

    def file_upload(self, filepath):

        # official file path

        # get file name from file path
        name = filepath.split('/Users/kwame/Music/audio.wav')[-1]

        # get MimeType of file (i.e file type)
        mimetype = MimeTypes().guess_type(name)[0]

        # create metadata for file
        file_metadata = {'name': name}

        # try uploading files to google drive
        try:
            media = MediaFileUpload(filepath, mimetype=mimetype)

            # Create a new file in Drive
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
            print("File successfully uploaded.")

        except:

            # UploadError if file is not uploaded
            print("Can't upload file.")
            # raise UploadError("Can't Upload File.")

    def file_uploaded(self):
        obj = ShareToDrive()
        obj.setup_drive_conn()
        obj.file_upload(filepath='/Users/kwame/Music/audio.wav')


class Confirmed(Screen):
    # url to access firebase
    firebase_url = "https://ever-record-db-default-rtdb.firebaseio.com/.json"

    # Create method that will take user input and put it into firebase.
    def store_to_db(self):
        print("test")
        # create variables to store user data as they fill form
        f_name = "test"
        l_name = "if"
        email = "strings"
        is_musician = "store as var"
        json_data = {"first name": f_name, "last name": l_name, "email": email, "is_musician": is_musician}
        res = requests.post(url=self.firebase_url, json=json_data)
        print(res)


# logic to store user info goes here.

# ==> NEW CODE ENDED <==


class FormSubmitted(Screen):
    pass


class WindowManager(ScreenManager):
    pass


# load kv file


kv = Builder.load_file("ever_record.kv")


# build the app


class EverRecord(App):

    def build(self):
        return kv

    def on_pause(self):
        return True


# run app


if __name__ == "__main__":
    EverRecord().run()
