from mln_robosherlock_msgs.srv import *
from mln.MarkovLogicNetwork import MLN, readMLNFromFile
from mln.database import Database
from wcsp.converter import WCSPConverter

import rospy
import sys, getopt

class MLNQueryService:
  model_filename="" 
  def __init__(self,filename):
      self.model_filename=filename


  def handle_query(self,req):
    mln = readMLNFromFile(self.model_filename)
    db=Database(mln)
    for atom in req.mln_atoms:
      print "Atom "+atom.mln_atom
      db.addGroundAtom(atom.mln_atom)
    
    mrf = mln.groundMRF(db)
    wcsp = WCSPConverter(mrf)
    results = wcsp.getMostProbableWorldDB()
    for s in results.query("object(?cluster,?object)"):
        return MLNQueryResponse(s["?object"])
    return MLNQueryResponse("Empty")


def get_object_identity(argv):
    filename=""
    try: 
        opts, args = getopt.getopt(argv,"hi:0",["ifile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile>'
        sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
        print 'service.py -i <inputfile>'
        sys.exit()
      elif opt in ("-i","--ifile"):
        filename = arg
    if filename == '':
      filename ="data/run_0.mln"
    m = MLNQueryService(filename)
  
    print 'Input Files is:',filename
    rospy.init_node('get_object_identity')
    s = rospy.Service('query_mln', MLNQuery, m.handle_query)
    print "Ready to recieve requests"
    rospy.spin()

if __name__ == "__main__":
    get_object_identity(sys.argv[1:])
