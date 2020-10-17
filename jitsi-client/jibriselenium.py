#!/usr/bin/env python3

#   Copyright 2020 Clemens Hopfer, <datacop @ wireloss.net>
#
#   this is based on the old Python Jibri implementation
#   https://github.com/jitsi/jibri/tree/python_jibri
#
#   Copyright 2016 jitsi.org
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys, getopt, os
import signal
import time
import pprint
import logging
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0


class JibriSeleniumDriver():
    def __init__(self, 
            url, 
            authtoken=None, 
            xmpp_connect_timeout=10, 
            binary_location=None, 
            google_account=None,
            google_account_password=None, 
            displayname='Live Stream', 
            email='recorder@jitsi.org',
            xmpp_login = None,
            xmpp_password = None,
            pjsua_flag = False,
            alsa_output=None,
            alsa_input=None,
            urlParams = None):

      #init based on url and optional token
      self.url = url
      self.authtoken = authtoken
      self.google_account = google_account
      self.google_account_password = google_account_password
      self.displayname = displayname
      self.xmpp_login = xmpp_login
      self.xmpp_password = xmpp_password
      self.email = email
      self.pjsua_flag = pjsua_flag
      self.alsa_output = alsa_output
      self.alsa_input = alsa_input
      if urlParams:
        self.urlParams = urlParams
      else:
        self.urlParams = {
            'config.iAmRecorder':         'true',
            'config.externalConnectUrl':  'null',
            'config.startWithAudioMuted': 'true',
            'config.startWithVideoMuted': 'true',
            'interfaceConfig.APP_NAME':   '"Jibri"',
            'interfaceConfig.DISABLE_PRESENCE_STATUS':   'true',
            'interfaceConfig.DISABLE_JOIN_LEAVE_NOTIFICATIONS':   'true',
            'interfaceConfig.DISABLE_FOCUS_INDICATOR':   'true',
            'interfaceConfig.DISABLE_DOMINANT_SPEAKER_INDICATOR':   'true',
            'config.analytics.disabled':  'true',
            'config.p2p.enabled':         'false',
            #'config.prejoinPageEnabled':  'false', # seems to break audio and tile videos
            'config.requireDisplayName':  'false'
        }

      self.flag_jibri_identifiers_set = False
      self.flag_google_login_set = False

      #only wait this only before failing to load meet
      self.xmpp_connect_timeout = xmpp_connect_timeout

      self.desired_capabilities = DesiredCapabilities.CHROME
      self.desired_capabilities['loggingPrefs'] = { 'browser':'ALL' }

      self.options = Options()
      self.options.add_argument('--use-fake-ui-for-media-stream')
      self.options.add_argument('--start-maximized')
      self.options.add_argument('--kiosk')
      self.options.add_argument('--enabled')
      self.options.add_argument('--enable-logging')
      self.options.add_argument('--vmodule=*=3')
      self.options.add_argument("--disable-infobars")
      if self.alsa_output:
        self.options.add_argument('--alsa-output-device=%s' % self.alsa_output)
      if self.alsa_input:
        self.options.add_argument('--alsa-input-device=%s' % self.alsa_input)
      self.options.add_argument('--temp-profile')
      # self.options.add_argument(' --user-data-dir=chrome_jibri_profile')
      # self.options.add_argument('--first-run')
      # self.options.add_argument('--incognito')
      self.options.add_experimental_option("excludeSwitches", ['enable-automation']);
      #use microphone if provided
      if self.pjsua_flag:
        #self.options.add_argument('--alsa-input-device=plughw:1,1')
        self.xmpp_login=None
        self.xmpp_password=None

      if binary_location:
        self.options.binary_location = binary_location
      self.initDriver()

    def initDriver(self, options=None, desired_capabilities=None):
      #make sure the environment is set properly
      display=os.environ.get('DISPLAY', None)
      if not display:
        os.environ['DISPLAY'] =':0'

      if not desired_capabilities:
        desired_capabilities = self.desired_capabilities
      if not options:
        options = self.options

      print("Initializing Driver")
      self.driver = webdriver.Chrome(chrome_options=options, desired_capabilities=desired_capabilities)

    def setJibriIdentifiers(self, url,displayname=None, email=None,xmpp_login=None,xmpp_password=None,ignore_flag=False,):
      if displayname == None:
        displayname = self.displayname
      if email == None:
        email = self.email
      if xmpp_login == None:
        xmpp_login = self.xmpp_login
      if xmpp_password == None:
        xmpp_password = self.xmpp_password

      logging.info("setting jibri identifiers: display %s -  email %s"%(displayname,email))
      self.driver.get(url)
      script_text=''
      script_text+="window.localStorage.setItem('displayname','%s'); window.localStorage.setItem('email','%s');"%(displayname,email)
      if xmpp_login:
        logging.info("setting jibri identifiers: xmpp_username_override %s"%(xmpp_login))
        script_text+="window.localStorage.setItem('xmpp_username_override','%s');"%(xmpp_login)
      if xmpp_password:
        script_text+="window.localStorage.setItem('xmpp_password_override','%s');"%(xmpp_password)
      script_text+="window.localStorage.setItem('callStatsUserName', 'jibri');"

      self.execute_script(script_text)

    def urlParamsAppend(self, url, urlParams=None):
        if urlParams:
            params = []
            for k,v in urlParams.items():
                params.append(f'{k}={v}')
            url += '#'+'&'.join(params)
        return url

    def googleLogin(self):
      if self.google_account and not self.flag_google_login_set:
        logging.info("Logging in with google account")
        # log in
        timeout=5
        try:
          self.driver.get('https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fwww.youtube.com%2F&uilel=3&service=youtube&passive=true&hl=en')
          self.driver.find_element_by_id('Email').send_keys(self.google_account)
          self.driver.find_element_by_id('next').click()
          element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, "Passwd")))
          self.driver.find_element_by_id('Passwd').send_keys(self.google_account_password)
          self.driver.find_element_by_id('signIn').click()

          #now let's see what happened
          page=self.driver.execute_script('return window.location.href;')
          if page.startswith('https://accounts.google.com/ServiceLogin'):
            logging.info('Google Login or password wrong, failing to log in to google')
          elif page.startswith('https://accounts.google.com/signin/challenge'):
            logging.info("Google Login includes another challenge, failing to log in to google")
          elif page.startswith('https://www.youtube.com/'):
            logging.info("Google Login successful, continued to www.youtube.com")

            #hack to sign into youtube if neccessary after getting google login working
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.signin-container button')))
            self.driver.find_element_by_css_selector('div.signin-container button').click()
          else:
            logging.info("Unknown current page after Google Login: %s"%page)
        except Exception as e:
          logging.info("Exception occurred logging into google: %s"%e)

        #finished trying to log in
        logging.info("Google Login completed one way or another")
        self.flag_google_login_set = True

    def launchUrl(self, url=None):
      if not url:
        #pull URL if not provided
        url = self.url

      logging.info("Launching URL: %s"%url)

      #log in to google, if appropriate
      self.googleLogin()

      url = self.urlParamsAppend(url, self.urlParams)
      #launch the page early and set our identifiers, if we haven't done it already
      self.setJibriIdentifiers(url)

      #launch the page for real
      logging.debug("launchUrl Final driver.get() call begun")
      #instead of using driver.reload or attempting to get the same URL (which was skipping the reload) we now go to the "about:blank" page first before loading meet again
      self.driver.get('about:blank')
      self.driver.get(url)
      self.skipPrejoinPage()

    def skipPrejoinPage(self):
        "click the join button, until prejoinPageEnabled breaks audio and tile videos"
        self.driver.find_element_by_css_selector('div.prejoin-preview-dropdown-container div.action-btn').click()

    def execute_async_script(self, script):
      try:
        response=self.driver.execute_script(script)
      except WebDriverException as e:
        pprint.pprint(e)
        response = None
#      except ConnectionRefusedError as e:
        #should kill chrome and restart? unhealthy for sure
#        pprint.pprint(e)
#        response = None
      except:
        logging.error("Unexpected error:%s"%sys.exc_info()[0])
        raise

      return response


    def execute_script(self, script):
      try:
        response=self.driver.execute_script(script)
      except WebDriverException as e:
        pprint.pprint(e)
        response = None
#      except ConnectionRefusedError as e:
        #should kill chrome and restart? unhealthy for sure
#        pprint.pprint(e)
#        response = None
      except:
        print("Unexpected error:%s"%sys.exc_info()[0])
        raise

      return response

    def setBackgroundImageUrl(self, url):
        return self.execute_script("""
        return $("#largeVideoContainer").css({
            "background-image": "url('%s')",
            "background-size": "cover",
            "background-repeat": "no-repeat"
        });
        """ % url)

    def toggleTileView(self):
      try:
        from selenium.webdriver.common.action_chains import ActionChains
        return ActionChains(self.driver).send_keys("w").perform()
      except WebDriverException as e:
        pprint.pprint(e)
        
    def getRoomName(self):
        return self.execute_script("return APP.conference.roomName")

    def getParticipants(self):
        # APP.conference.listMembers()
        return self.execute_script("""
        _participants=[];
        for (var p of APP.conference.listMembers()) {
            var tracks=[]
            for (var t of p._tracks) {
                var audio_volume;
                var audio_muted;
                if (t.containers.length == 1) {
                    audio_volume = 20*Math.log10(t.containers[0].volume);
                    audio_muted = t.containers[0].muted;
                }
                tracks.push({
                    'audioLevel': t.audioLevel,
                    'isP2P': t.isP2P,
                    'muted': t.muted,
                    'ownerEndpointId': t.ownerEndpointId,
                    'hasBeenMuted': t.hasBeenMuted,
                    'disposed': t.disposed,
                    'ssrc': t.ssrc,
                    'type': t.type,
                    'audio_volume': audio_volume,
                    'audio_muted': audio_muted,
                    'videoType': t.videoType,
                });
            }
            var element_visible;
            var pelement = $("span#participant_"+p._id);
            if (pelement.length == 1) {
                element_visible = pelement.is(":visible");
            }
            _participants.push({
                'jid':     p._jid,
                'id':      p._id,
                'botType': p._botType,
                'connectionStatus': p._connectionStatus,
                'hidden':  p._hidden,
                'role': p._role,
                'tracks': tracks,
                'displayName': p._displayName,
                'status': p._status,
                'element_visible': element_visible
            });
        };
        return _participants;
        """)
    def showParticipant_OLD(self, id): # TODO REMOVE TODO
        return self.execute_script("""
        _participants=[];
        for (var p of APP.conference._room.getParticipants()) {
            if (p._id == "%s") {
                for (var t of p._tracks) {
                    if (t.type == "video") {
                        t.containers[0].click()
                        return true;
                    }
                }
            }
        };
        return false;
        """ % id)
    def showParticipant(self, id):
        return self.execute_script("""
        return APP.conference.getParticipantById("%s").getTracksByMediaType("video")[0].containers[0].click();
        """ % id)

    def setParticipantVisible(self, id, visible):
        return self.execute_script("""
        var pelement = $("span#participant_%s");
        if (pelement.length == 1) {
            if(%s)
                pelement.show();
            else
                pelement.hide();
        }
        return pelement.is(":visible");
        """ % (id, 'true' if visible else 'false')
        )

    def setParticipantVolumeMute_OLD(self, id, volume, muted = False):
        return self.execute_script("""
        var container = APP.conference.getParticipantById("%s").getTracksByMediaType("audio")[0].containers[0];
        %s
        container.muted = %s;
        return {'muted': container.muted, 'volume': container.volume};
        """ % ( id,
            "container.volume = %f;" % volume if volume else '',
            'true' if muted else 'false' )
        )

    def toggleParticipantMute_OLD(self, id):
        return self.execute_script("""
        var container = APP.conference.getParticipantById("%s").getTracksByMediaType("audio")[0].containers[0];
        if ( container.muted == false)
            container.muted = true;
        else
            container.muted = false;
        return {'muted': container.muted, 'volume': container.volume};
        """ % id)

    def setParticipantVolumeMute(self, id, volume, muted = False):
        return self.execute_script("""
        var container;
        for (var track of APP.conference.getParticipantById("%s")._tracks) {
            container = track.containers[0];
            %s
            container.muted = %s;
        }
        return {'muted': container.muted, 'volume': 20 * Math.log10(container.volume)};
        """ % ( id,
            "container.volume = Math.pow(10, %f/20);" % volume if volume else '',
            'true' if muted else 'false' )
        )

    def toggleParticipantMute(self, id):
        return self.execute_script("""
        var container;
        for (var track of APP.conference.getParticipantById("%s")._tracks) {
            container = track.containers[0];
            if ( container.muted == false)
                container.muted = true;
            else
                container.muted = false;
        }
        return {'muted': container.muted};
        """ % id)

    def getSpeakerStats(self):
        "APP.conference.getSpeakerStats()"
        return self.execute_script("""
        var _participants={};
        var _stats=APP.conference.getSpeakerStats();
        for (var id in _stats) {
            var p = _stats[id];
            _participants[p._userId] = {
                'id':           p._userId,
                'displayName':  p.displayName,
                'isLocalStats': p._isLocalStats,
                'hasLeft':      p._hasLeft,
                '_dominantSpeakerStart':  p._dominantSpeakerStart
            };
        }; return _participants;
        """)

    def getConnectionState(self):
        return self.execute_script("return APP.conference.getConnectionState();")

    def isJoined(self):
        return self.execute_script("return APP.conference.isJoined();")

    def isXMPPConnected(self):
      response = self.execute_async_script('return APP.conference._room.xmpp.connection.connected;')
      
      print('isXMPPConnected:%s'%response)
      return response
    
    def getDownloadBitrate(self):
      try:
        stats = self.execute_async_script("return APP.conference._room.room ? APP.conference.getStats() : undefined;")
        if stats == None:
          return 0
        return stats['bitrate']['download']
      except:
        return 0

    def waitDownloadBitrate(self,timeout=None, interval=2):
      logging.info('starting to wait for DownloadBitrate')
      if not timeout:
        timeout = self.xmpp_connect_timeout
      if self.getDownloadBitrate() > 0:
        logging.info('downloadbitrate > 0, done waiting')
        return True
      else:
        wait_time=0
        while wait_time < timeout:
          logging.info('waiting +%d = %d < %d for DownloadBitrate'%(interval, wait_time, timeout))
          time.sleep(interval)
          wait_time = wait_time + interval
          if self.getDownloadBitrate() > 0:
            logging.info('downloadbitrate > 0, done waiting')
            return True
          if wait_time >= timeout:
            logging.info('Timed out waiting for download bitrate')
            return None

    def waitXMPPConnected(self,timeout=None, interval=5):
      logging.info('starting to wait for XMPPConnected')
      if not timeout:
        timeout = self.xmpp_connect_timeout
      if self.isXMPPConnected():
        return True
      else:
        wait_time=0
        while wait_time < timeout:
          logging.info('waiting +%d = %d < %d for XMPPConnected'%(interval, wait_time, timeout))
          time.sleep(interval)
          wait_time = wait_time + interval
          if self.isXMPPConnected():
            logging.info('XMPP connected, done waiting')
            return True
          if wait_time >= timeout:
            logging.info('Timed out waiting for XMPP connection')
            return False


    def checkRunning(self, timeout=2, download_timeout=5, download_interval=1):
      logging.debug('checkRunning selenium')
#      self.driver.set_script_timeout(10)
      try:
        element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        if element:
          return self.waitDownloadBitrate(timeout=download_timeout, interval=download_interval)
        else:
          return False
      except Exception as e:
        logging.info("Failed to run script properly: %s"%e)
#        raise e
      return False

    def quit(self):
      try:
        response=self.execute_script('return APP.conference._room.connection.disconnect();')
        #give chrome a chance to finish logging out
        time.sleep(2)
      except Exception as e:
        print("Failed to click hangup button")
        pprint.pprint(e)

      self.driver.quit()


def sigterm_handler(a, b):
    if driver:
        driver.quit()
    exit("Jibri begone!")


if __name__ == '__main__':
  app = sys.argv[0]
  argv=sys.argv[1:]
  URL = ''
  token = ''
  loglevel='DEBUG'
  pjsua_flag=False
  timeout=60
  displayname='Live Stream' 
  email='recorder@jitsi.org'

  try:
    opts, args = getopt.getopt(argv,"phu:t:d:w:n:e:",["meeting_url=","token=","loglevel=","wait=","displayname=","email="])
  except getopt.GetoptError:
    print(app+' -u <meetingurl> -t <authtoken>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
       print(app+' -u <meetingurl> -t <authtoken>')
       sys.exit()
    elif opt == '-p':
       pjsua_flag = True
    elif opt in ("-u", "--meeting_url"):
       URL = arg
    elif opt in ("-t", "--token"):
       token = arg
    elif opt in ("-d", "--debug"):
       loglevel = arg
    elif opt in ("-w", "--wait"):
       timeout = int(arg)
    elif opt in ("-e", "--email"):
       email = arg
    elif opt in ("-n", "--displayname"):
       displayname = arg

  if not URL:
      print('No meeting URL provided.')
      exit(1)

  logging.basicConfig(level=loglevel,
                        format='%(asctime)s %(levelname)-8s %(message)s')
  signal.signal(signal.SIGTERM, sigterm_handler)
  js = JibriSeleniumDriver(URL,token,displayname=displayname,email=email,pjsua_flag=pjsua_flag)
  # js.xmpp_login = 'user@xmpp-domain.com'
  # js.xmpp_password = 'password'
  # js.google_account='user@gmail.com'
  # js.google_account_password='password'
  js.launchUrl()
  if js.checkRunning(download_timeout=60):
    if js.waitXMPPConnected():
      print('Successful connection to meet')
      if js.waitDownloadBitrate()>0:
        print('Successfully receving data in meet, waiting 60 seconds for fun')
        interval=1
        sleep_clock=0
        while sleep_clock < timeout:
          br=js.getDownloadBitrate()
          if not br:
            print('No more data, waiting a few...')
            if not js.waitDownloadBitrate():
              print('Never got more data, finishing up...')
              break
          else:
            print('Current bitrate: %s'%br)

          sleep_clock=sleep_clock+interval
          time.sleep(interval)

      else:
        print("Failed to receive data in meet client")

    else:
      print("Failed to connect to meet")
  else:
    print("Failed to start selenium/launch URL")

  print("Done waiting, finishing up and exiting...")
  js.quit()
