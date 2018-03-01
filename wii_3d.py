try:
  import pyext
except:
  print "ERROR: This script must be loaded by the PD/Max pyext external"

from collections import namedtuple
pos = namedtuple("pos", ["x","y","z"])

from math import sin, cos

import numpy as np

class speakers(pyext._class):

  # inlets and outlets
  _inlets = 1 # use messsages
  _outlets = 1 

  def __init__(self):
    self.speakers = {} # empty dictionary
    self.remotes = {}
    pos = namedtuple("pos", ["x","y","z"])

  def controller_1(self,*a):
    # args should be player_id, x, y, z, yaw, pitch
    if len(a) != 6:
      print "Requires 6 args: player_id, x, y, z, yaw, pitch"
    else:
      # create or update remote
      try:
        self.remotes[a[0]].update(a[1],a[2],a[3],a[4],a[5]) # tries to update in place
      except KeyError, e:
        self.remotes[a[0]] = remote(a[1],a[2],a[3],a[4],a[5]) # otherwise creates new
      r = self.remotes[a[0]]

      # compute distances to speakers from this remote
      distances = r.distances(self.speakers)

      # build string: "'distances' player_id speaker_id_1 d_1 speaker_id_2 ..."
      out_str = "distances "
      out_str += str(a[0]) # player id
      for speaker_id, d in distances.iteritems():
        out_str += " " + str(speaker_id) + " " + str(d) # speaker ids and distances

      self._outlet(1,out_str)

  
  def add_speaker_1(self,*a):
    """ args should be speaker_id, x, y, z """
    self.speakers[a[0]] = pos(a[1],a[2],a[3])

  def remove_speaker_1(self,a):
    # arg should be id of speaker to remove
    self.speakers.pop(a)

  def reset_speakers_1(self):
    self.speakers = {}


class remote:
  
  def __init__(self,x,y,z,yaw,pitch):
    self.x = x
    self.y = y
    self.z = z
    self.yaw = yaw
    self.pitch = pitch
    # changes in x, y, z (direction vector)
    self.dx = cos(yaw)*cos(pitch)
    self.dy = sin(yaw)*cos(pitch)
    self.dz = sin(pitch)

  def update(self,x,y,z,yaw,pitch):
    self.x = x
    self.y = y
    self.z = z
    self.yaw = yaw
    self.pitch = pitch
    # changes in x, y, z (direction vector)
    self.dx = cos(yaw)*cos(pitch)
    self.dy = sin(yaw)*cos(pitch)
    self.dz = sin(pitch)

  def distances(self,speakers):
    # get ids of speakers with angle < 90 deg
    fwd_speaker_ids = []
    for speaker_id, speaker in speakers.iteritems():
      if self.is_angle_less_90(speaker):
        fwd_speaker_ids.append(speaker_id)

    # filter dict of speakers to only fwd speakers
    fwd_speakers = { k: speakers[k] for k in fwd_speaker_ids }

    # create dict of distances to speakers. distances are infinity for speakers behind the remote
    ds = {}
    for speaker_id, speaker in fwd_speakers.iteritems(): # speakers in < 90 deg
        ds[speaker_id] = self.distance_to(np.array((speaker.x,speaker.y,speaker.z))) # compute actual distance
    for speaker_id in np.setdiff1d(speakers.keys(),fwd_speaker_ids): # other speakers (i.e. not in fwd_speaker_ids)
        ds[speaker_id] = float('inf') # use infinity instead
    return ds

  def is_angle_less_90(self,speaker):
    # if dot product of facing and displacement to speaker is positive, angle is less than 90
    if np.dot((self.dx,self.dy,self.dz), (speaker.x-self.x, speaker.y-self.y, speaker.z-self.z)) > 0:
      return True
    else:
      return False
    
  def distance_to(self,x0):
    x1 = np.array((self.x,self.y,self.z))
    x2 = np.add(x1,np.array((self.dx,self.dy,self.dz)))
    
    return np.true_divide(np.linalg.norm(np.cross(x0-x1,x0-x2)) , np.linalg.norm(x2-x1))
    

    
