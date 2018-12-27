import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
             
class presence_control(hass.Hass):

  def initialize(self):
    # self.LOGLEVEL="DEBUG"
    self.lock=False
    self.log("presence_control App")
    self.log("self.args={}".format(self.args))
    if "trackers" in self.args:
      trackers=eval(self.args["trackers"])
      self.trackers=trackers
    else:
      self.log("Error trackers must be defined in apps.yaml file")
      return
    if "tracker_list" in self.args:
      self.tracker_list=eval(self.args["tracker_list"])
    else:
      self.log("Error tracker_list must be defined in apps.yaml file")
    self.homestate=["home","house","on","susans"]

    if "tlist" in self.args:
      self.tlist=eval(self.args["tlist"])
    else:
      self.log("Error tlist must be defined in apps.yaml file")



    self.log("trackers={}".format(trackers))
    self.log("tracker_list={}".format(self.tracker_list))
    self.log("tlist={}".format(self.tlist))
    for (tracker,bit) in trackers:
      self.log("setting listener for {}".format(tracker))
      self.listen_state(self.state_callback,tracker)
    self.run_every(self.timer_callback,self.datetime(),10*60)

    self.set_tracker_state()
    self.set_house_state()

    self.log("chip info={}".format(self.alexa_get_state("chip")))
    self.log("initialization complete")

  def alexa_get_state(self, aname):
    found=False
    for t in self.tlist:
      if aname.lower() in t["alexa_name"]:
        found=True
        break;
      else:
        continue;
    
    if found:
      t["attributes"]=self.get_state(t["entity"])
      return t
    else:
      return None

  def timer_callback(self,kwargs):
    if not self.lock:
      self.set_tracker_state()
      self.set_house_state()

  def set_house_state(self):
    state=0
    noonehomemask=0
    everyonehomemask=0
    for t in self.tlist:
      self.log("t={}, previous_state={}".format(t,state))
      cstate=self.get_state(t["entity"])
      if cstate==None:
          cstate="Away"
      if cstate.split()[-1].lower() in ["home","house","susans"]:
          state=state+t["bit"]
      everyonehomemask=everyonehomemask+t["bit"]
    self.log("everyonehomemask={} noonehomemask={} 12,48".format(everyonehomemask,noonehomemask))
    self.log("state={}".format(state))
    if state==everyonehomemask:
        self.set_state("input_boolean.everyone_home",state="on")
        self.set_state("input_boolean.noone_home",state="off")
        self.set_state("input_boolean.someone_home",state="on")
    elif state==noonehomemask:
        self.set_state("input_boolean.everyone_home",state="off")
        self.set_state("input_boolean.noone_home",state="on")
        self.set_state("input_boolean.someone_home",state="off")
    else:
        self.set_state("input_boolean.everyone_home",state="off")
        self.set_state("input_boolean.noone_home",state="off")
        self.set_state("input_boolean.someone_home",state="on")
    
    self.log("Everyone={}, Noone={}, Someone={}".format(self.get_state("input_boolean.everyone_home"),self.get_state("input_boolean.noone_home"),self.get_state("input_boolean.someone_home")))

    if (state & 12) >0:
        self.log("state= {} master is home".format(state))
        self.set_state("input_boolean.masterishome",state="on")
    else:
        self.log("state= {} master is not home".format(state))
        self.set_state("input_boolean.masterishome",state="off")
    if (state & 48) >0:
        self.log("state={} guest is home".format(state))
        self.set_state("input_boolean.guestishome",state="on")
    else:
        self.log("state={} guest is not home".format(state))
        self.set_state("input_boolean.guestishome",state="off")

  def state_callback(self,tracker,state,old,new,kwargs):
    self.log("tracker={},state={},old={},new={}".format(tracker,state,old,new))
    if not self.lock:
      self.set_tracker_state()
      self.set_house_state()
    else:
      self.log("app currently locked")

  def set_tracker_state(self):
    self.lock=True
    everyone=True
    someone=False
    noone=True
    self.current_state=0
    tracker_mask=0
    #for (tracker,bit) in self.trackers:
    for t in self.tlist:
      tracker=t["entity"]
      bit=t["bit"]
      self.log("bit={}".format(bit))
      tracker_mask=tracker_mask | bit
      self.log("tracker={}".format(tracker))
      loct = self.get_state(tracker)
      if loct==None:
          loct="Away"
      self.log("loct={}".format(loct))
      loc = loct.split()
      self.log("tracker={},loc={},loc[-1]={},homestate={} state={}".format(t["entity"],loc,loc[-1],self.homestate,"on" if loc[-1].lower() in self.homestate else "off"))
      self.current_state=self.current_state | (bit if loc[-1].lower() in self.homestate else 0)
      self.log("tracker={},loct={}, tracker_mask={}, self.current_state={}".format(tracker,loct,tracker_mask,self.current_state))
    for ib in self.tracker_list:
      self.log("self.current_state={}, tracker_list[{}]={}".format(self.current_state,ib,self.tracker_list[ib]))
      if (self.current_state in self.tracker_list[ib]):
        self.turn_on(ib)
        self.log("turned on {}".format(ib))
      else:
        self.turn_off(ib)
        self.log("turned off {}".format(ib))
    self.lock=False
