import data
import numpy as np


class ClusterData(data.Data):
    def __init__(self, A, headers, K, means, codes, errors ):
        data.Data.__init__(self)

        self.matrixData = np.concatenate((A,means ),axis=0) # add means to the bottom of the A matrix
        self.headers = headers
        self.K = K
        self.data = A
        self.matrixData = A

        self.types = ["numeric"]* len(self.headers)
        self.header2raw = {}
        for i, value in enumerate(headers):
            self.header2raw[value] = i
            self.header2matrix[value] = i
        # self.enum_dict = {}
        # self.matrixData = pdata
        self.means = means
        self.codes = codes.astype(int).T.tolist()[0] #convert to list
        self.errors = errors
        # self.addcolumn(["clusterID", "numeric"]+ self.codes)
        # print self.headers, len(self.types)

    def getMeans(self):
        return self.means


    def getClusterId(self):
        return self.codes


    def getK(self):
        return self.K



  # """will write selected headers data to a csv file"""
  # def write(self, dest_file  ):
  #  if dest_file.__getattribute__('name')[-3:] != "csv": #if the input filename does not have csv extension, put csv extension
  #    dest_file += ".csv"
  #  mheaders = headers if headers != None else self.headers #headers is optional, if no headers, write all data
  # headers = self.headers
  # odes = self.codes + [i for i in range(self.K_value)]
  # types = ['numeric'] * (len(mheaders)+1)
  # rint mheaders, "mheaders", self.header2raw, "headerDict"
  # emp_data = self.get_data(mheaders).tolist() #get the data corresponding to those headers and make a list
  #  with open(dest_file, 'wb') as csvfile: # open csv file
  # ith dest_file as csvfile:
  #  spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
  #  spamwriter.writerow(mheaders+ ["clusterIds"]) #write headers
  #  spamwriter.writerow(mtypes)
  #  print len(temp_data), len(codes)
  #  for i  in range(len(temp_data)):
  # spamwriter.writerow(temp_data[i]+ [codes[i]])#write each row of data
