import my_appapi as appapi
import datetime
import time
             
class presence_control(appapi.my_appapi):

  def initialize(self):
    # self.LOGLEVEL="DEBUG"
    self.log("presence_control App")
    self.log("self.args={}".format(self.args))
    if "trackers" in self.args:
      trackers=eval(self.args["trackers"])
      self.trackers=trackers
    else:
      self.log("Error trackers must be defined in appdaemon.cfg file")
      return
    if "tracker_list" in self.args:
      self.tracker_list=eval(self.args["tracker_list"])
    else:
      self.log("Error tracker_list must be defined in appdaemon.cfg file")

    self.log("trackers={}".format(trackers))
    self.log("tracker_list={}".format(self.tracker_list))
    for tracker in trackers:
      self.listen_state(self.state_callback,tracker)
    self.run_every(self.timer_callback,self.datetime(),10*60)

  def timer_callback(self,kwargs):
    self.set_tracker_state()

  def state_callback(self,tracker,state,old,new,kwargs):
    self.set_tracker_state()

  def set_tracker_state(self):
    everyone=True
    someone=False
    noone=True
    current_state=0
    tracker_mask=0
    for (tracker,bit) in self.trackers:
      tracker_mask=tracker_mask+bit
      current_state=current_state + (bit if self.get_state(tracker) in ["home","house"] else 0)
    self.log("tracker_mask={}, current_state={}".format(tracker_mask,current_state))
    for ib in self.tracker_list:
      self.log("current_state={}, tracker_list[{}]={}".format(current_state,ib,self.tracker_list[ib]))
      if (current_state in self.tracker_list[ib]):
        self.turn_on(ib)
      else:
        self.turn_off(ib)

