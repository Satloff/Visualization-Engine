import data
from copy import deepcopy

class PCAData(data.Data):
    def __init__(self, headers, pdata, evals, evecs, means):
        data.Data.__init__(self, filename1 = None, filename2 = None)

        self.evals = evals # numpy matrix
        self.evecs = evecs # numpy matrix
        self.means = means # numpy matrix
        self.data = pdata # numpy matrix
        self.matrixData = pdata
        self.header2header = {}
        self.originalHeaders = headers

        for i, value in enumerate(headers):
            header = eval("'p' + str(i)")
            self.headers.append(header)
            self.type.append('numeric')
            self.header2raw[header] = i
            self.header2matrix[header] = i
            self.header2header[value] = header

    def getEigenvalues(self):
        return self.evals

    def getEigenvectors(self):
        return self.evecs

    def getDataMeans(self):
        return self.means

    def getDataHeaders(self):
        return self.originalHeaders

    def getOriginalHeaders(self):
        return self.originalHeaders


class ClusterData(data.Data):
  def __init__(self, A, headers, K, means, codes, errors ):
    data.Data.__init__(self)

    self.matrixData = np.concatenate((A,means ),axis=0) # add means to the bottom of the A matrix
    self.headers = headers
    self.K = K

    #constructing raw data by converting each item to string
    for i in range(self.matrixData.shape[0]):
      rows = []
      for j in range(self.matrixData.shape[1]):
        rows.append(str(self.matrixData[i,j]))
      self.raw_data.append(rows)

    self.types = ["numeric"]* len(self.headers)
    self.header2raw = {}
    for i in range(len(self.headers)):
      self.header2raw[self.headers[i]] = i
    # self.enum_dict = {}
    # self.matrixData = pdata
    self.means = means
    self.codes = codes.T.tolist()[0] #convert to list
    self.errors = errors
    # self.addcolumn(["clusterID", "numeric"]+ self.codes)
    # print self.headers, len(self.types)

  def getMeans(self):
    return self.means


  def getClusterId(self):
    return self.codes


  def getK(self):
    return self.K



  """will write selected headers data to a csv file"""
  def write(self, dest_file  ):
    # if dest_file.__getattribute__('name')[-3:] != "csv": #if the input filename does not have csv extension, put csv extension
    #   dest_file += ".csv"
    # mheaders = headers if headers != None else self.headers #headers is optional, if no headers, write all data
    mheaders = self.headers
    codes = self.codes + [i for i in range(self.K_value)]
    mtypes = ['numeric'] * (len(mheaders)+1)
    print mheaders, "mheaders", self.header2raw, "headerDict"
    temp_data = self.get_data(mheaders).tolist() #get the data corresponding to those headers and make a list
    # with open(dest_file, 'wb') as csvfile: # open csv file
    with dest_file as csvfile:
      spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
      spamwriter.writerow(mheaders+ ["clusterIds"]) #write headers
      spamwriter.writerow(mtypes)
      print len(temp_data), len(codes)
      for i  in range(len(temp_data)):
        spamwriter.writerow(temp_data[i]+ [codes[i]])#write each row of data
