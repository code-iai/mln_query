from mln_robosherlock_msgs.srv import *
from mln.mln import MLN, readMLNFromFile
from mln.database import Database
from wcsp.converter import WCSPConverter
from time import time

from prac.core import PRAC
from prac.inference import *

import rospy
import sys, getopt


class MLNQueryService:
  model_filename=""
  def __init__(self,filename):
    self.model_filename=filename
    self.mln = readMLNFromFile(self.model_filename)
    self.prac =PRAC()

  def handle_query(self,req):
    start =time()
    db=Database(self.mln)
    infer = PRACInference(self.prac, [])
    inferenceStep = PRACInferenceStep(infer, self)
    inferenceStep.output_dbs= [db]
    infer.inference_steps.append(inferenceStep)
    
    for atom in req.mln_atoms:
      print "Atom "+atom.mln_atom
      db.addGroundAtom(atom.mln_atom)
    objRecog = self.prac.getModuleByName('obj_recognition')

    self.prac.run(infer,objRecog,mln=self.mln)
    step = infer.inference_steps[-1]
    res_list = []
    index_list = []
    for db in step.output_dbs:	
      for s in db.query("object(?cluster,?object)"):
        index_list.append(int(s["?cluster"][-1]))
        res_list.append(s["?object"])
      print res_list
      print index_list
    return MLNQueryResponse(index_list,res_list)


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
      filename ="data/final.mln"
    m = MLNQueryService(filename)

    print 'Input Files is:',filename
    rospy.init_node('get_object_identity')
    s = rospy.Service('query_prac', MLNQuery, m.handle_query)
    print "Ready to recieve requests"
    rospy.spin()

if __name__ == "__main__":
    get_object_identity(sys.argv[1:])
